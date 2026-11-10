# -*- coding: utf-8 -*-
"""
Cindy AI - Real FLUX.1-dev LoRA training on the user's own RunPod account.

Flow:
  1. Dataset ZIP (images + .txt captions) is uploaded to temporary storage (Fal CDN upload, free).
  2. A GPU pod is deployed on RunPod with a bootstrap script (passed via env, base64).
  3. Pod installs ostris/ai-toolkit, downloads FLUX.1-dev with the user's HF token, trains,
     and serves status/progress/result under a secret path on port 8000 (RunPod HTTPS proxy).
  4. Local server polls status, downloads lora.safetensors, verifies it, registers it.
  5. Pod is terminated in all cases (success, failure, timeout). The pod also carries its own
     watchdog that self-terminates if the local PC goes offline.
"""
import base64
import json
import os
import re
import secrets as pysecrets
import struct
import time

import requests

RUNPOD_GQL = "https://api.runpod.io/graphql"
POD_IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"


def gql(api_key, query, variables=None, timeout=30):
    body = {"query": query}
    if variables is not None:
        body["variables"] = variables
    r = requests.post(f"{RUNPOD_GQL}?api_key={api_key.strip()}", json=body, timeout=timeout)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if r.status_code != 200 or data.get("errors"):
        msg = (data.get("errors") or [{"message": r.text[:300]}])[0].get("message")
        raise RuntimeError(f"RunPod API: {msg}")
    return data.get("data", {})


def gpu_price(api_key, gpu_id):
    q = 'query($id: String!) { gpuTypes(input: {id: $id}) { id displayName communityPrice securePrice } }'
    try:
        g = gql(api_key, q, {"id": gpu_id}).get("gpuTypes", [])
        return g[0] if g else None
    except Exception:
        return None


def terminate_pod(api_key, pod_id):
    if not pod_id:
        return
    for _ in range(3):
        try:
            gql(api_key, 'mutation($id: String!) { podTerminate(input: {podId: $id}) }', {"id": pod_id})
            return
        except Exception:
            time.sleep(4)


def list_pods(api_key):
    return gql(api_key, "query { myself { pods { id name desiredStatus costPerHr } } }").get("myself", {}).get("pods", [])


def _bootstrap_script(token, trigger, steps, is_style, max_seconds):
    sample_prompt = f"{trigger}, cinematic portrait" if not is_style else f"a city street in the style of {trigger}"
    cfg = f"""job: extension
config:
  name: cindy_lora
  process:
    - type: sd_trainer
      training_folder: /workspace/output
      device: cuda:0
      trigger_word: "{trigger}"
      network:
        type: lora
        linear: 16
        linear_alpha: 16
      save:
        dtype: float16
        save_every: 100000
        max_step_saves_to_keep: 1
      datasets:
        - folder_path: /workspace/dataset
          caption_ext: txt
          caption_dropout_rate: 0.05
          shuffle_tokens: false
          cache_latents_to_disk: true
          resolution: [512, 768, 1024]
      train:
        batch_size: 1
        steps: {steps}
        gradient_accumulation_steps: 1
        train_unet: true
        train_text_encoder: false
        gradient_checkpointing: true
        noise_scheduler: flowmatch
        optimizer: adamw8bit
        lr: 0.0001
        dtype: bf16
        skip_first_sample: true
        disable_sampling: true
        ema_config:
          use_ema: true
          ema_decay: 0.99
      model:
        name_or_path: black-forest-labs/FLUX.1-dev
        is_flux: true
        quantize: true
      sample:
        sampler: flowmatch
        sample_every: 100000
        width: 1024
        height: 1024
        prompts: ["{sample_prompt}"]
        neg: ""
        seed: 42
        walk_seed: true
        guidance_scale: 4
        sample_steps: 20
meta:
  name: cindy
  version: '1.0'
"""
    cfg_b64 = base64.b64encode(cfg.encode()).decode()
    return f"""#!/bin/bash
OUT=/workspace/out/{token}
mkdir -p $OUT /workspace/dataset
st() {{ printf '{{"stage":"%s","msg":"%s","t":%s}}' "$1" "$2" "$(date +%s)" > $OUT/status.json; }}
selfdestruct() {{
python3 - <<'PY'
import os, json, urllib.request
q = {{"query": 'mutation {{ podTerminate(input: {{podId: "%s"}}) }}' % os.environ["RUNPOD_POD_ID"]}}
req = urllib.request.Request("https://api.runpod.io/graphql?api_key=" + os.environ["RP_KEY"],
                             data=json.dumps(q).encode(), headers={{"Content-Type": "application/json"}})
urllib.request.urlopen(req, timeout=30)
PY
}}
fail() {{ st failed "$1"; sleep 900; selfdestruct; exit 1; }}
st booting "pod started"
cd /workspace/out && nohup python3 -m http.server 8000 > /dev/null 2>&1 &
( sleep {max_seconds}; st failed "hard time limit reached"; sleep 120; selfdestruct ) &

st installing "installing ai-toolkit"
cd /workspace
git clone --depth 1 https://github.com/ostris/ai-toolkit.git > $OUT/install.log 2>&1 || fail "git clone failed"
cd ai-toolkit
pip install --no-cache-dir -r requirements.txt >> $OUT/install.log 2>&1 || fail "requirements install failed"
pip install --no-cache-dir bitsandbytes accelerate huggingface_hub >> $OUT/install.log 2>&1

export HF_HUB_ENABLE_HF_TRANSFER=0
huggingface-cli login --token "$HF_TOKEN" >> $OUT/install.log 2>&1 || true

st dataset "downloading dataset"
curl -sL "$DATA_URL" -o /workspace/d.zip || fail "dataset download failed"
cd /workspace/dataset && unzip -q -o /workspace/d.zip || fail "dataset unzip failed"
N=$(ls /workspace/dataset | grep -iE '\\.(jpg|jpeg|png|webp)$' | wc -l)
[ "$N" -ge 4 ] || fail "dataset has only $N images"

echo "{cfg_b64}" | base64 -d > /workspace/cfg.yaml
( while true; do tr '\\r' '\\n' < $OUT/train.log 2>/dev/null | grep -oE '[0-9]+/{steps}' | tail -1 > $OUT/progress.txt; sleep 10; done ) &
st training "training $N images"
cd /workspace/ai-toolkit
HF_TOKEN="$HF_TOKEN" HUGGING_FACE_HUB_TOKEN="$HF_TOKEN" python3 run.py /workspace/cfg.yaml > $OUT/train.log 2>&1 || fail "training process failed"

F=$(find /workspace/output -name "*.safetensors" 2>/dev/null | head -1)
[ -n "$F" ] || fail "no safetensors produced"
cp "$F" $OUT/lora.safetensors
st done "$(stat -c %s $OUT/lora.safetensors)"
sleep 1800
selfdestruct
"""


def _verify_safetensors(path):
    try:
        with open(path, "rb") as fh:
            n = struct.unpack("<Q", fh.read(8))[0]
            header = json.loads(fh.read(n))
        return len([k for k in header if k != "__metadata__"]) > 0
    except Exception:
        return False


def run_training_job(job, api_key, hf_token, data_url, gpu_id, upload_fn, register_fn, loras_dir,
                     max_minutes=90):
    """Blocking worker. Mutates `job` dict (status/logs/progress) for the UI."""
    def log(msg):
        job["logs"].append(msg)
        job["logs"] = job["logs"][-12:]
        print(f"[RunPod {job['id']}] {msg}")

    token = pysecrets.token_hex(16)
    script = _bootstrap_script(token, job["trigger_word"], job["steps"], job["is_style"], max_minutes * 60)
    pod_id = None
    try:
        deploy_q = """mutation($input: PodFindAndDeployOnDemandInput) {
          podFindAndDeployOnDemand(input: $input) { id costPerHr machine { gpuDisplayName } } }"""
        base_input = {
            "gpuCount": 1, "gpuTypeId": gpu_id, "name": f"cindy-lora-{job['trigger_word']}"[:40],
            "imageName": POD_IMAGE, "containerDiskInGb": 90, "volumeInGb": 0,
            "minVcpuCount": 8, "minMemoryInGb": 32, "ports": "8000/http", "startSsh": False,
            "dockerArgs": "bash -c 'echo $CINDY_B64 | base64 -d > /cindy.sh && bash /cindy.sh'",
            "env": [
                {"key": "CINDY_B64", "value": base64.b64encode(script.encode()).decode()},
                {"key": "DATA_URL", "value": data_url},
                {"key": "HF_TOKEN", "value": hf_token},
                {"key": "RP_KEY", "value": api_key},
            ],
        }

        # Fallback list of GPUs if preferred one is out of stock in community cloud
        candidate_gpus = [gpu_id]
        for alt in ["NVIDIA GeForce RTX 4090", "NVIDIA RTX A6000", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A5000", "NVIDIA A40"]:
            if alt not in candidate_gpus:
                candidate_gpus.append(alt)

        pod = None
        chosen_gpu = gpu_id
        for cand_gpu in candidate_gpus:
            current_input = dict(base_input, gpuTypeId=cand_gpu)
            for cloud in ("COMMUNITY", "SECURE"):
                try:
                    res_deploy = gql(api_key, deploy_q, {"input": dict(current_input, cloudType=cloud)})
                    pod = res_deploy.get("podFindAndDeployOnDemand")
                    if pod and pod.get("id"):
                        chosen_gpu = cand_gpu
                        break
                except Exception as e:
                    pass
            if pod and pod.get("id"):
                break

        if not pod or not pod.get("id"):
            raise RuntimeError("لا يوجد كارت شاشة متاح حالياً على RunPod. يرجى المحاولة بعد لحظات.")

        pod_id = pod["id"]
        job["pod_id"] = pod_id
        job["cost_per_hr"] = pod.get("costPerHr")
        disp_name = (pod.get("machine") or {}).get("gpuDisplayName") or chosen_gpu
        job["gpu_display"] = disp_name
        job["status"] = "IN_PROGRESS"
        job["progress"] = 10
        log(f"تم حجز وتشغيل كمبيوتر سحابي {pod_id} ({disp_name}) بسعر ${pod.get('costPerHr')}/ساعة.")

        base = f"https://{pod_id}-8000.proxy.runpod.net/{token}"
        stage_ar = {
            "booting": "الجهاز بيقلع وبيتجهز في الداتا سنتر...",
            "installing": "تثبيت أدوات التدريب (ai-toolkit + CUDA)...",
            "dataset": "تحميل حزمة صور التدريب على كارت الشاشة...",
            "training": "التدريب شغال على كارت الشاشة (تحميل FLUX.1-dev وبدء الخطوات)..."
        }
        last_stage, started = None, time.time()
        while time.time() - started < max_minutes * 60 + 300:
            time.sleep(15)
            job["elapsed_cost"] = round((time.time() - started) / 3600 * float(job.get("cost_per_hr") or 0), 3)
            try:
                s = requests.get(f"{base}/status.json", timeout=12)
                if s.status_code != 200:
                    continue
                st = s.json()
            except Exception:
                continue
            stage = st.get("stage")
            if stage != last_stage:
                last_stage = stage
                if stage in stage_ar:
                    log(stage_ar[stage])
                    if stage == "installing":
                        job["progress"] = 15
                    elif stage == "dataset":
                        job["progress"] = 25
                    elif stage == "training":
                        job["progress"] = 30
            if stage == "training":
                try:
                    p = requests.get(f"{base}/progress.txt", timeout=8).text.strip()
                    if "/" in p:
                        cur, tot = [int(x) for x in p.split("/")]
                        train_pct = int(cur * 100 / max(tot, 1))
                        # Scale progress from 30% to 90%
                        job["progress"] = 30 + int(train_pct * 0.6)
                        job["logs"][-1] = f"التدريب شغال: خطوة {cur} من {tot} ({train_pct}%)"
                except Exception:
                    pass
            elif stage == "failed":
                tail = ""
                for f in ("train.log", "install.log"):
                    try:
                        tail = requests.get(f"{base}/{f}", timeout=10).text[-1500:]
                        if tail:
                            break
                    except Exception:
                        pass
                job["error_tail"] = tail
                raise RuntimeError(f"فشل على الجهاز السحابي: {st.get('msg')}")
            elif stage == "done":
                log("التدريب اكتمل بنجاح! جاري تنزيل ملف الأوزان (.safetensors) على جهازك...")
                job["progress"] = 92
                fname = f"{re.sub(r'[^A-Za-z0-9_]', '_', job['trigger_word'])}_{job['id'][-6:]}.safetensors"
                fpath = os.path.join(loras_dir, fname)
                with requests.get(f"{base}/lora.safetensors", stream=True, timeout=300) as r:
                    r.raise_for_status()
                    with open(fpath, "wb") as fh:
                        for chunk in r.iter_content(1024 * 1024):
                            fh.write(chunk)
                if os.path.getsize(fpath) < 1_000_000 or not _verify_safetensors(fpath):
                    raise RuntimeError("ملف الأوزان الذي تم تنزيله تالف أو غير مكتمل.")
                job["local_file"] = fname
                job["file_size"] = os.path.getsize(fpath)
                log(f"تم استلام ملف الموديل بنجاح ({job['file_size'] // (1024 * 1024)} MB). جاري إتاحته للتوليد...")
                job["progress"] = 97
                if upload_fn:
                    job["weights_url"] = upload_fn(fpath)
                if register_fn:
                    register_fn(job)
                job["progress"] = 100
                job["status"] = "COMPLETED"
                log("اكتمل التدريب وحُفظ الموديل في مكتبتك بنجاح! 🎬")
                return
        raise RuntimeError("تجاوز التدريب الحد الزمني الأقصى.")
    except Exception as e:
        job["status"] = "FAILED"
        job["error"] = str(e)
        log(f"خطأ: {e}")
    finally:
        if pod_id:
            terminate_pod(api_key, pod_id)
            try:
                still = [p for p in list_pods(api_key) if p.get("id") == pod_id]
                log("تم إيقاف وحذف الجهاز السحابي فوراً لحماية رصيدك ✅" if not still else "تم إرسال أمر الإيقاف النهائي للجهاز.")
            except Exception:
                log("تم إرسال أمر إيقاف الجهاز السحابي وحذفه.")
            if job.get("cost_per_hr"):
                mins = (time.time() - job.get("start_time", time.time())) / 60
                job["final_cost_estimate"] = round(mins / 60 * float(job["cost_per_hr"]), 3)
                log(f"استغرق التدريب {mins:.1f} دقيقة بتكلفة إجمالية تقريبية ${job['final_cost_estimate']}.")
