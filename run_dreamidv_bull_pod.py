import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_02_dreamidv_bull_aziz.mp4")

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()
HF_TOKEN = secrets.get("huggingface_api_key", "").strip()

# Proven pre-patched DreamID-V codebase & assets
CODE_ZIP_URL = "https://v3b.fal.media/files/b/0ab2867e/CXfd-8bwxfA3_aCv9ZRvv_dreamidv_clean.zip"
FLASH_ATTN_WHEEL = "https://huggingface.co/ehabfikry/cindy-wheels/resolve/main/flash_attn-2.7.4.post1+cu12torch2.4cxx11abiFALSE-cp311-cp311-linux_x86_64.whl"

# Approved Mature Abdelaziz Face
REF_FACE_URL = "https://v3b.fal.media/files/b/0ab2887d/Xw2oB2iSYg5b7hdeCBhgu_frame2_mature.jpg"
# Approved 81-frame 832x480 driving video cut from 4K bull struggle footage (Slow_push_on_struggling_bull)
DRIVING_VIDEO_URL = "https://v3b.fal.media/files/b/0ab28930/qVuvetaIUn_MhuQ6MGI1Y_driving_bull_832x480.mp4"

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

mkdir -p /workspace/out /workspace/input /workspace/logs /workspace/DreamID-V /workspace/models
cd /workspace/out
nohup python3 -m http.server 8000 > /workspace/logs/http.log 2>&1 &

st() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> /workspace/out/run.log
}

st "stage_1_inputs" "1/5: Downloading Real Bull Footage & Abdelaziz Face portrait..."
curl -sL "$REF_FACE_URL" -o /workspace/input/aziz_face.jpg
curl -sL "$DRIVING_VIDEO_URL" -o /workspace/input/driving_bull.mp4
curl -sL "$CODE_ZIP_URL" -o /workspace/code.zip
python3 -c "import zipfile; zipfile.ZipFile('/workspace/code.zip').extractall('/workspace/DreamID-V')"
rm -f /workspace/code.zip

st "stage_2_deps" "2/5: Installing dependencies (decord, mediapipe, onnxruntime, flash-attn)..."
WHL_NAME="flash_attn-2.7.4.post1+cu12torch2.4cxx11abiFALSE-cp311-cp311-linux_x86_64.whl"
curl -sL -H "Authorization: Bearer $HF_TOKEN" "$FLASH_ATTN_WHEEL" -o "/workspace/$WHL_NAME"
pip install --no-cache-dir "/workspace/$WHL_NAME" >> /workspace/out/run.log 2>&1
pip install --no-cache-dir decord einops scipy matplotlib huggingface_hub hf_transfer diffusers transformers accelerate tqdm easydict imageio imageio-ffmpeg ftfy dashscope opencv-python onnxruntime mediapipe >> /workspace/out/run.log 2>&1

st "stage_3_weights" "3/5: Fast snapshot download of Wan2.1-1.3B & DreamID-V weights..."
export HF_HUB_ENABLE_HF_TRANSFER=1
python3 -c "
import os
from huggingface_hub import snapshot_download
token = os.environ.get('HF_TOKEN')
print('Downloading Wan2.1-1.3B...')
snapshot_download('Wan-AI/Wan2.1-T2V-1.3B', local_dir='/workspace/models/Wan2.1-T2V-1.3B', token=token)
print('Downloading DreamID-V...')
snapshot_download('XuGuo699/DreamID-V', local_dir='/workspace/models/DreamID-V', token=token)
" >> /workspace/out/run.log 2>&1

mkdir -p /workspace/DreamID-V/pose/models
cp /workspace/models/DreamID-V/dw-ll_ucoco_384.onnx /workspace/DreamID-V/pose/models/ 2>/dev/null || true
cp /workspace/models/DreamID-V/yolox_l.onnx /workspace/DreamID-V/pose/models/ 2>/dev/null || true

st "stage_4_inference" "4/5: Running DreamID-V Face Replacement on Real 4K Bull Footage (81 frames, 832x480)..."
cd /workspace/DreamID-V
python generate_dreamidv_faster.py \
    --size 832*480 \
    --ckpt_dir /workspace/models/Wan2.1-T2V-1.3B \
    --dreamidv_ckpt /workspace/models/DreamID-V/dreamidv_faster.pth \
    --ref_image /workspace/input/aziz_face.jpg \
    --ref_video /workspace/input/driving_bull.mp4 \
    --sample_steps 16 \
    --base_seed 42 \
    --save_file /workspace/out/test_02_dreamidv_bull_aziz.mp4 >> /workspace/out/run.log 2>&1

VID=$(find /workspace/out -name "*.mp4" 2>/dev/null | head -1)
if [ -n "$VID" ]; then
    cp "$VID" /workspace/out/test_02_dreamidv_bull_aziz.mp4
    st "done" "SUCCESS_DONE: DreamID-V video generated successfully ($(stat -c %s /workspace/out/test_02_dreamidv_bull_aziz.mp4) bytes)"
else
    st "failed" "ERROR_FAILED: No mp4 generated"
fi

sleep 600
"""

def deploy_and_run():
    pod_id = None
    start_time = time.time()
    rate = 0.34
    success = False

    try:
        print("=" * 70, flush=True)
        print(" VirtuFilm Studio AI: DreamID-V Real Footage Evaluation Pipeline", flush=True)
        print(" Director: Ehab Fikry | Asset: Mature Abdelaziz on 4K Bull Footage", flush=True)
        print(" Repository: bytedance/DreamID-V (Wan2.1-1.3B Backbone)", flush=True)
        print("=" * 70, flush=True)

        gpu_ladder = [
            ("NVIDIA GeForce RTX 3090", 0.22),
            ("NVIDIA RTX A5000", 0.27),
            ("NVIDIA RTX A6000", 0.33),
            ("NVIDIA GeForce RTX 4090", 0.89),
            ("NVIDIA GeForce RTX 5090", 0.69),
            ("NVIDIA L40S", 0.79),
            ("NVIDIA RTX 6000 Ada Generation", 0.74)
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
                        "name": "cindy-dreamidv-bull",
                        "imageName": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                        "containerDiskInGb": 50,
                        "volumeInGb": 0,
                        "minVcpuCount": 4,
                        "minMemoryInGb": 16,
                        "ports": "8000/http",
                        "startSsh": False,
                        "dockerArgs": "bash -c 'echo $CINDY_B64 | base64 -d > /cindy.sh && bash /cindy.sh; sleep infinity'",
                        "env": [
                            {"key": "CINDY_B64", "value": script_b64},
                            {"key": "DRIVING_VIDEO_URL", "value": DRIVING_VIDEO_URL},
                            {"key": "REF_FACE_URL", "value": REF_FACE_URL},
                            {"key": "CODE_ZIP_URL", "value": CODE_ZIP_URL},
                            {"key": "FLASH_ATTN_WHEEL", "value": FLASH_ATTN_WHEEL},
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
                except Exception:
                    pass
            if pod and pod.get("id"):
                break

        if not pod or not pod.get("id"):
            raise RuntimeError("Could not find available GPU on RunPod right now.")

        pod_id = pod["id"]
        print(f"\n[الخطوة 2/4] تم حجز السيرفر بنجاح: {chosen_info} | Pod ID: {pod_id}", flush=True)
        proxy_url = f"https://{pod_id}-8000.proxy.runpod.net"

        print("\n[الخطوة 3/4] متابعة خطوات DreamID-V لحظة بلحظة...", flush=True)
        last_logged_line = ""
        stuck_error_count = 0

        for elapsed in range(0, 1500, 10):
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
                        print("\n[الخطوة 4/4] اكتمال التوليد بنجاح! جاري سحب فيديو تبديل الملامح...", flush=True)
                        vid_url = f"{proxy_url}/test_02_dreamidv_bull_aziz.mp4"
                        r_vid = requests.get(vid_url, timeout=45)
                        if r_vid.status_code == 200 and len(r_vid.content) > 10000:
                            os.makedirs(OUTPUT_DIR, exist_ok=True)
                            with open(LOCAL_OUTPUT_PATH, 'wb') as f_out:
                                f_out.write(r_vid.content)
                            print(f"\n[DONE] تم حفظ الفيديو بنجاح: {LOCAL_OUTPUT_PATH} ({len(r_vid.content)/(1024*1024):.2f} MB)", flush=True)
                            success = True
                            break

                    # Fail-fast on ANY error or failure in log
                    err_keywords = ["ERROR", "error:", "Traceback", "ModuleNotFoundError", "failed", "RuntimeError"]
                    if any(k in text for k in err_keywords) and "SUCCESS_DONE" not in text:
                        stuck_error_count += 1
                        if stuck_error_count >= 1:
                            print(f"\n[FAIL-FAST DETECTED] خطأ في الحاوية - إنهاء فوري:\n{text[-1500:]}", flush=True)
                            terminate_pod(pod_id)
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
