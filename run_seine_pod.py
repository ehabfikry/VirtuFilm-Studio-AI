import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_03_seine_transition.mp4")

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()
HF_TOKEN = secrets.get("huggingface_api_key", "").strip()

YOUNG_URL = "https://v3b.fal.media/files/b/0ab2887d/_8kUnuaViaZh9FI-jeW-R_frame1_young.jpg"
MATURE_URL = "https://v3b.fal.media/files/b/0ab2887d/Xw2oB2iSYg5b7hdeCBhgu_frame2_mature.jpg"

def run_gql(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    headers = {"Authorization": f"Bearer {RUNPOD_KEY}", "Content-Type": "application/json"}
    r = requests.post("https://api.runpod.io/graphql", headers=headers, json=body, timeout=45)
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL Error: {data['errors']}")
    return data.get("data", {})

def terminate_pod(pod_id):
    if not pod_id:
        return
    print(f"\n[SAFETY] Terminating pod {pod_id} immediately to protect balance...", flush=True)
    q = 'mutation($id: String!) { podTerminate(input: {podId: $id}) }'
    for _ in range(3):
        try:
            run_gql(q, {"id": pod_id})
            print(f"[SAFETY] Pod {pod_id} TERMINATED. Zero cost.", flush=True)
            return
        except Exception:
            time.sleep(3)

BASH_BOOTSTRAP = r"""#!/bin/bash
set -e
export HF_TOKEN="$HF_TOKEN"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"

mkdir -p /workspace/out /workspace/logs
cd /workspace/out
nohup python3 -m http.server 8000 > /workspace/logs/http.log 2>&1 &

st() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> /workspace/out/run.log
}

st "stage_1_repo" "1/5: Cloning Vchitect/SEINE repository..."
cd /workspace
rm -rf /workspace/SEINE
git clone --depth 1 https://github.com/Vchitect/SEINE.git /workspace/SEINE >> /workspace/out/run.log 2>&1

# Patch with_mask_sample.py to use imageio fallback for video saving (bypassing PyAV 14.0 pict_type bug)
python3 -c "
with open('/workspace/SEINE/sample_scripts/with_mask_sample.py', 'r') as f:
    code = f.read()
old = 'torchvision.io.write_video(save_video_path, video_, fps=8)'
new = '''try:
        torchvision.io.write_video(save_video_path, video_, fps=8)
    except Exception as e:
        print(\"Torchvision write_video failed, saving with imageio:\", e)
        import imageio
        imageio.mimsave(save_video_path, video_.cpu().numpy(), fps=8)'''
if old in code:
    code = code.replace(old, new)
    with open('/workspace/SEINE/sample_scripts/with_mask_sample.py', 'w') as f:
        f.write(code)
    print('with_mask_sample.py patched with imageio fallback!')
else:
    print('Target string not found in with_mask_sample.py')
" >> /workspace/out/run.log 2>&1

cd /workspace/SEINE
mkdir -p /workspace/SEINE/input/transition/aziz_matchcut /workspace/SEINE/pretrained

st "stage_2_inputs" "2/5: Downloading Young and Mature Abdelaziz matching frames (CDN)..."
curl -sL "$YOUNG_URL" -o /workspace/SEINE/input/transition/aziz_matchcut/01_young.jpg
curl -sL "$MATURE_URL" -o /workspace/SEINE/input/transition/aziz_matchcut/02_mature.jpg

st "stage_3_deps" "3/5: Installing dependencies (tensorboard, diffusers, transformers, huggingface_hub==0.25.2, av<14.0.0, etc.)..."
pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cu118 diffusers==0.15.0 transformers==4.29.2 "huggingface_hub==0.25.2" decord imageio imageio[ffmpeg] "av<14.0.0" einops omegaconf timm==0.9.10 rotary-embedding-torch==0.3.5 natsort tensorboard >> /workspace/out/run.log 2>&1

python3 -c "import torch, torchvision, diffusers, transformers, decord, imageio, av, einops, omegaconf, timm, rotary_embedding_torch, natsort, tensorboard; print('ALL DEPENDENCY IMPORTS VERIFIED SUCCESSFULLY!')" >> /workspace/out/run.log 2>&1

st "stage_4_weights" "4/5: Downloading base SD-1.4 and SEINE checkpoint seine.pt..."
mkdir -p /workspace/SEINE/pretrained/stable-diffusion-v1-4
huggingface-cli download CompVis/stable-diffusion-v1-4 --include "unet/*" "vae/*" "text_encoder/*" "tokenizer/*" --local-dir /workspace/SEINE/pretrained/stable-diffusion-v1-4 >> /workspace/out/run.log 2>&1
wget -q -c -O /workspace/SEINE/pretrained/seine.pt https://huggingface.co/Vchitect/SEINE/resolve/main/seine.pt >> /workspace/out/run.log 2>&1

cat << 'EOF' > /workspace/SEINE/configs/aziz_transition.yaml
ckpt: "pretrained/seine.pt"
pretrained_model_path: "pretrained/stable-diffusion-v1-4"
input_path: "input/transition/aziz_matchcut"
save_path: "/workspace/out/"

model: UNet
num_frames: 16
image_size: [512, 512]

use_fp16: True
enable_xformers_memory_efficient_attention: False

seed: 42
run_time: 13
cfg_scale: 8.0
sample_method: 'ddpm'
num_sampling_steps: 250
text_prompt: ['young_to_old_abdelaziz_transition']
additional_prompt: ", smooth cinematic aging transition from young laughing man to older laughing man, photorealistic, 8k."
negative_prompt: "blurry, low quality, artifacts, distorted face, jitter"
do_classifier_free_guidance: True
mask_type: "onelast1"
use_mask: True
EOF

st "stage_5_inference" "5/5: Running SEINE Generative Diffusion (250 steps DDPM, 16 frames)..."
python sample_scripts/with_mask_sample.py --config configs/aziz_transition.yaml >> /workspace/out/run.log 2>&1

VID=$(find /workspace/out -name "*.mp4" 2>/dev/null | head -1)
if [ -n "$VID" ]; then
    cp "$VID" /workspace/out/test_03_seine_transition.mp4
    st "done" "SUCCESS_DONE: Video generated successfully ($(stat -c %s /workspace/out/test_03_seine_transition.mp4) bytes)"
else
    st "failed" "ERROR_FAILED: No mp4 generated"
fi

sleep 600
"""

def deploy_and_run():
    pod_id = None
    start_time = time.time()
    rate = 0.22
    success = False

    try:
        print("=" * 70, flush=True)
        print(" VirtuFilm Studio AI: SEINE Generative Match-Cut Transition Test", flush=True)
        print(" Director: Ehab Fikry | Asset: Young Abdelaziz -> Mature Abdelaziz", flush=True)
        print(" Repository: Vchitect/SEINE (ICLR 2024)", flush=True)
        print("=" * 70, flush=True)

        gpu_ladder = [
            ("NVIDIA RTX A5000", 0.27),
            ("NVIDIA GeForce RTX 3090", 0.22),
            ("NVIDIA RTX A6000", 0.33),
            ("NVIDIA GeForce RTX 4090", 0.34),
            ("NVIDIA A40", 0.35)
        ]

        script_b64 = base64.b64encode(BASH_BOOTSTRAP.encode("utf-8")).decode("ascii")

        deploy_mutation = """
        mutation($input: PodFindAndDeployOnDemandInput) {
            podFindAndDeployOnDemand(input: $input) {
                id
                costPerHr
                machine {
                    gpuDisplayName
                }
            }
        }
        """

        pod = None
        chosen_info = None
        print("\n[الخطوة 1/4] فحص وتخصيص أرخص كارت متاح على السحابة...", flush=True)
        for gpu_id, price in gpu_ladder:
            print(f" -> جاري محاولة حجز كارت: {gpu_id} (${price}/hr)...", flush=True)
            for cloud in ("SECURE", "COMMUNITY"):
                try:
                    payload = {
                        "gpuCount": 1,
                        "gpuTypeId": gpu_id,
                        "cloudType": cloud,
                        "name": "cindy-seine-transition",
                        "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
                        "containerDiskInGb": 40,
                        "volumeInGb": 0,
                        "minVcpuCount": 4,
                        "minMemoryInGb": 16,
                        "ports": "8000/http",
                        "startSsh": False,
                        "dockerArgs": "bash -c 'echo $CINDY_B64 | base64 -d > /cindy.sh && bash /cindy.sh; sleep infinity'",
                        "env": [
                            {"key": "CINDY_B64", "value": script_b64},
                            {"key": "YOUNG_URL", "value": YOUNG_URL},
                            {"key": "MATURE_URL", "value": MATURE_URL},
                            {"key": "HF_TOKEN", "value": HF_TOKEN},
                            {"key": "HUGGING_FACE_HUB_TOKEN", "value": HF_TOKEN}
                        ]
                    }
                    res = run_gql(deploy_mutation, {"input": payload})
                    pod = res.get("podFindAndDeployOnDemand")
                    if pod and pod.get("id"):
                        rate = pod.get("costPerHr", price)
                        chosen_info = f"{gpu_id} [{cloud}] @ ${rate}/hr"
                        break
                except Exception as e_dep:
                    pass
            if pod and pod.get("id"):
                break

        if not pod or not pod.get("id"):
            raise RuntimeError("Could not find available GPU on RunPod right now.")

        pod_id = pod["id"]
        print(f"\n[الخطوة 2/4] تم حجز السيرفر بنجاح: {chosen_info} | Pod ID: {pod_id}", flush=True)
        proxy_url = f"https://{pod_id}-8000.proxy.runpod.net"

        print("\n[الخطوة 3/4] متابعة خطوات SEINE لحظة بلحظة...", flush=True)
        last_logged_line = ""
        stuck_error_count = 0

        for elapsed in range(0, 900, 10):
            time.sleep(10)
            curr = time.time() - start_time
            try:
                r_log = requests.get(f"{proxy_url}/run.log", timeout=5)
                if r_log.status_code == 200:
                    text = r_log.text.strip()
                    lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
                    last = lines[-1] if lines else "..."
                    if last != last_logged_line:
                        print(f"[{int(curr//60):02d}m {int(curr%60):02d}s] {last[:100]}", flush=True)
                        last_logged_line = last
                    else:
                        print(f"[{int(curr//60):02d}m {int(curr%60):02d}s] ... قيد التقدم: {last[:70]}", flush=True)

                    if "SUCCESS_DONE" in text:
                        print("\n[الخطوة 4/4] اكتمال التوليد بنجاح! جاري سحب فيديو النقلة...", flush=True)
                        vid_url = f"{proxy_url}/test_03_seine_transition.mp4"
                        r_vid = requests.get(vid_url, timeout=30)
                        if r_vid.status_code == 200 and len(r_vid.content) > 10000:
                            os.makedirs(OUTPUT_DIR, exist_ok=True)
                            with open(LOCAL_OUTPUT_PATH, 'wb') as f_out:
                                f_out.write(r_vid.content)
                            print(f"\n[DONE] تم حفظ الفيديو بنجاح: {LOCAL_OUTPUT_PATH} ({len(r_vid.content)/(1024*1024):.2f} MB)", flush=True)
                            success = True
                            break

                    if "ERROR_FAILED" in text or "ModuleNotFoundError" in text or "Traceback (most recent call last)" in text:
                        stuck_error_count += 1
                        if stuck_error_count >= 2:
                            print(f"\n[ERROR DETECTED] تفاصيل الخطأ في الحاوية:\n{text[-1500:]}", flush=True)
                            break
            except Exception:
                print(f"[{int(curr//60):02d}m {int(curr%60):02d}s] تهيئة الحاوية وتشغيل السيرفر...", flush=True)

    except Exception as e:
        print(f"\n[ERROR] خطأ أثناء التشغيل: {e}", flush=True)
    finally:
        terminate_pod(pod_id)
        total_time = time.time() - start_time
        total_cost = (total_time / 3600.0) * rate
        print(f"\n[تقرير الحساب النهائي]: المدة = {int(total_time//60)} دقيقة و {int(total_time%60)} ثانية | التكلفة الإجمالية = ${total_cost:.4f} USD", flush=True)

if __name__ == "__main__":
    deploy_and_run()
