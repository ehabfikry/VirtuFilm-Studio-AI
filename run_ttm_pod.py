import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_06_ttm_dualclock.mp4")
BRAIN_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\f39b14fe-7077-4fe2-88bb-d661dd89b5b3"

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()
HF_TOKEN = secrets.get("huggingface_api_key", "").strip()

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
            print(f"[SAFETY] Pod {pod_id} TERMINATED. Zero lingering cost.", flush=True)
            return
        except Exception:
            time.sleep(3)

BASH_BOOTSTRAP = r"""#!/bin/bash
set -e
export HF_TOKEN="$HF_TOKEN"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
unset HF_HUB_ENABLE_HF_TRANSFER

mkdir -p /workspace/out /workspace/input /workspace/logs /workspace/TTM
cd /workspace/out
nohup python3 -m http.server 8000 > /workspace/logs/http.log 2>&1 &

st() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> /workspace/out/run.log
}

st "stage_1_deps" "1/5: Installing diffusion and video dependencies (pinned for PyTorch 2.4)..."
pip install --no-cache-dir \
    "diffusers==0.30.3" \
    "transformers==4.44.2" \
    "accelerate==0.34.2" \
    "huggingface_hub==0.25.2" \
    opencv-python-headless \
    imageio \
    imageio-ffmpeg >> /workspace/out/run.log 2>&1
st "stage_1_deps" "Dependencies installed successfully."

st "stage_2_inputs" "2/5: Downloading TTM inputs from ehabfikry/cindy-wheels..."
python3 -c "
import os
from huggingface_hub import snapshot_download

token = os.environ.get('HF_TOKEN')
snapshot_download(
    repo_id='ehabfikry/cindy-wheels',
    allow_patterns='ttm_input_aziz/*',
    local_dir='/workspace/input',
    token=token
)
print('TTM input assets downloaded successfully:', os.listdir('/workspace/input/ttm_input_aziz'), flush=True)
" >> /workspace/out/run.log 2>&1

st "stage_3_clone" "3/5: Cloning Time-to-Move (TTM) ICLR 2026 repository..."
cd /workspace
git clone --depth 1 https://github.com/time-to-move/TTM.git /workspace/TTM >> /workspace/out/run.log 2>&1
cd /workspace/TTM

st "stage_4_author" "4/5: Authoring Headless Dual-Clock Runner for SVD..."

cat << 'EOF' > /workspace/TTM/run_cindy_ttm.py
import os
import sys
import time
import torch
import cv2
import numpy as np
from pathlib import Path

# Allow TF32 for high throughput
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

sys.path.insert(0, '/workspace/TTM')
os.chdir('/workspace/TTM')

from pipelines.svd_pipeline import StableVideoDiffusionTTMPipeline
from diffusers.utils import export_to_video, load_image

MODEL_ID = "stabilityai/stable-video-diffusion-img2vid-xt"
DTYPE = torch.float16

input_dir = "/workspace/input/ttm_input_aziz"
image_path = os.path.join(input_dir, "first_frame.png")
motion_signal_video_path = os.path.join(input_dir, "motion_signal.mp4")
motion_signal_mask_path = os.path.join(input_dir, "mask.mp4")
output_path = "/workspace/out/test_06_ttm_dualclock.mp4"

print("[TTM] Loading SVD XT pipeline with fp16...", flush=True)
t0 = time.time()
pipe = StableVideoDiffusionTTMPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=DTYPE,
    variant="fp16"
)
try:
    pipe.enable_model_cpu_offload()
    print("[TTM] Model CPU offload enabled successfully!", flush=True)
except Exception as e_off:
    print(f"[TTM] CPU offload fallback ({e_off}), moving directly to cuda...", flush=True)
    pipe.to("cuda")

try:
    pipe.enable_attention_slicing()
    print("[TTM] Attention slicing enabled!", flush=True)
except Exception:
    pass

t1 = time.time()
print(f"[TTM] SVD Pipeline ready in {t1 - t0:.1f}s!", flush=True)

image = load_image(image_path)
print(f"[TTM] Input image loaded: {image.size}", flush=True)

seed = 42
num_inference_steps = 50
tweak_index = 16
tstrong_index = 21
num_frames = 21
motion_bucket_id = 25

print(f"[TTM] Starting Dual-Clock Denoising: steps={num_inference_steps}, tweak={tweak_index}, tstrong={tstrong_index}, frames={num_frames}...", flush=True)
t_infer_start = time.time()

generator = torch.Generator().manual_seed(seed)

result = pipe(
    [image],
    generator=generator,
    motion_bucket_id=motion_bucket_id,
    num_inference_steps=num_inference_steps,
    motion_signal_video_path=motion_signal_video_path,
    motion_signal_mask_path=motion_signal_mask_path,
    tweak_index=tweak_index,
    tstrong_index=tstrong_index,
    num_frames=num_frames,
    decode_chunk_size=4
)

t_infer_end = time.time()
print(f"[TTM] Inference finished in {t_infer_end - t_infer_start:.1f}s!", flush=True)

frames = result.frames[0]
print(f"[TTM] Denoised frames count: {len(frames)}, type: {type(frames[0])}", flush=True)

# Export to video
try:
    export_to_video(frames, output_path, fps=7)
    print(f"[TTM] export_to_video saved: {output_path}", flush=True)
except Exception as e:
    print(f"[TTM] export_to_video fallback to cv2: {e}", flush=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    h_out, w_out = frames[0].size[1], frames[0].size[0]
    vw = cv2.VideoWriter(output_path, fourcc, 7, (w_out, h_out))
    for f in frames:
        arr = np.array(f)
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        vw.write(bgr)
    vw.release()

# Save keyframe stills for visual verification
still_00 = np.array(frames[0])
still_10 = np.array(frames[10])
still_20 = np.array(frames[20])

cv2.imwrite("/workspace/out/test_06_ttm_frame_00.jpg", cv2.cvtColor(still_00, cv2.COLOR_RGB2BGR))
cv2.imwrite("/workspace/out/test_06_ttm_frame_10.jpg", cv2.cvtColor(still_10, cv2.COLOR_RGB2BGR))
cv2.imwrite("/workspace/out/test_06_ttm_frame_20.jpg", cv2.cvtColor(still_20, cv2.COLOR_RGB2BGR))

vid_size = os.path.getsize(output_path)
print(f"SUCCESS_DONE: Video generated successfully ({vid_size} bytes) at {output_path}", flush=True)
EOF

st "stage_5_infer" "5/5: Launching TTM SVD Dual-Clock Inference..."
python3 /workspace/TTM/run_cindy_ttm.py >> /workspace/out/run.log 2>&1
st "complete" "ALL STAGES FINISHED"
"""

def deploy_and_run():
    pod_id = None
    rate = 0.35
    start_time = time.time()

    # Cost-efficient GPUs for 21-frame SVD inference
    gpu_ladder = [
        ("NVIDIA GeForce RTX 3090", 0.22),
        ("NVIDIA GeForce RTX 4090", 0.44),
        ("NVIDIA RTX A5000", 0.27),
        ("NVIDIA A40", 0.40),
        ("NVIDIA RTX 4000 Ada Generation", 0.29),
        ("NVIDIA L4", 0.38)
    ]

    try:
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
        print("\n[الخطوة 1/4] فحص وتخصيص كارت مناسب لـ TTM (Dual-Clock) على السحابة...", flush=True)
        for gpu_id, price in gpu_ladder:
            print(f" -> محاولة حجز: {gpu_id} (~${price}/hr)...", flush=True)
            for cloud in ("SECURE", "COMMUNITY"):
                try:
                    payload = {
                        "gpuCount": 1,
                        "gpuTypeId": gpu_id,
                        "cloudType": cloud,
                        "name": "cindy-ttm-test",
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
                            {"key": "HF_TOKEN", "value": HF_TOKEN},
                            {"key": "HUGGING_FACE_HUB_TOKEN", "value": HF_TOKEN}
                        ]
                    }
                    res = run_gql(deploy_mutation, {"input": payload})
                    pod = res.get("podFindAndDeployOnDemand")
                    if pod and pod.get("id"):
                        pod_id = pod["id"]
                        rate = pod.get("costPerHr") or price
                        chosen_info = f"{gpu_id} ({cloud}) @ ${rate}/hr"
                        print(f" [نجاح الحجز] Pod ID: {pod_id} | GPU: {chosen_info}", flush=True)
                        break
                except Exception:
                    time.sleep(1)
            if pod_id:
                break

        if not pod_id:
            raise RuntimeError("All cloud GPUs currently unavailable or out of stock.")

        proxy_url = f"https://{pod_id}-8000.proxy.runpod.net"
        print(f"\n[الخطوة 2/4] انتظار جاهزية الحاوية والبروكسي: {proxy_url}...", flush=True)

        for wait_sec in range(0, 180, 5):
            time.sleep(5)
            try:
                r = requests.get(f"{proxy_url}/run.log", timeout=4)
                if r.status_code == 200:
                    print(" [اتصال ناجح] تم فتح قناة البروكسي وبدء تدفق السجلات المباشرة.\n", flush=True)
                    break
            except Exception:
                pass
            if wait_sec % 15 == 0:
                print(f" ... جارٍ إقلاع النظام ({wait_sec} ثانية)...", flush=True)

        print("[الخطوة 3/4] متابعة التنفيذ وتوليد الفيديو بخاصية Dual-Clock Denoising...", flush=True)
        seen_lines = 0
        success = False
        error_detected = False

        # Max watchdog: 360 seconds (6 minutes)
        for tick in range(72):
            time.sleep(5)
            try:
                r = requests.get(f"{proxy_url}/run.log", timeout=5)
                if r.status_code == 200:
                    lines = r.text.strip().split("\n")
                    if len(lines) > seen_lines:
                        for l in lines[seen_lines:]:
                            print(f" [POD] {l}", flush=True)
                            if "SUCCESS_DONE:" in l:
                                success = True
                            if "Traceback (most recent call last)" in l or "Error:" in l:
                                error_detected = True
                        seen_lines = len(lines)
            except Exception:
                pass

            if success:
                print("\n [نجاح باهر] تم الانتهاء من التوليد بنجاح!", flush=True)
                break

            if error_detected and tick > 30:
                print("\n [خطأ] تم رصد خطأ أثناء التنفيذ، إنهاء لتوفير الرصيد.", flush=True)
                break

        if not success:
            raise RuntimeError("TTM inference failed or timed out.")

        print("\n[الخطوة 4/4] تحميل الفيديو واللقطات التمثيلية وحفظها محلياً...", flush=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Download generated video
        vid_url = f"{proxy_url}/test_06_ttm_dualclock.mp4"
        r_vid = requests.get(vid_url, timeout=30)
        with open(LOCAL_OUTPUT_PATH, "wb") as f_out:
            f_out.write(r_vid.content)
        vid_size = os.path.getsize(LOCAL_OUTPUT_PATH)
        print(f" [تم التحميل] الفيديو: {LOCAL_OUTPUT_PATH} ({vid_size:,} bytes)", flush=True)

        # Download extracted stills
        for still_name in ["test_06_ttm_frame_00.jpg", "test_06_ttm_frame_10.jpg", "test_06_ttm_frame_20.jpg"]:
            try:
                s_url = f"{proxy_url}/{still_name}"
                r_s = requests.get(s_url, timeout=10)
                local_s_path = os.path.join(BRAIN_DIR, still_name)
                with open(local_s_path, "wb") as f_s:
                    f_s.write(r_s.content)
                print(f" [تم التحميل] اللقطة: {local_s_path} ({os.path.getsize(local_s_path):,} bytes)", flush=True)
            except Exception as e_s:
                print(f" [تنبيه] تعذر تحميل {still_name}: {e_s}", flush=True)

        elapsed = time.time() - start_time
        cost_est = (elapsed / 3600.0) * float(rate)
        print(f"\n==========================================")
        print(f" زمن التشغيل الكامل: {elapsed:.1f} ثانية ({elapsed/60.0:.2f} دقيقة)")
        print(f" التكلفة المقدرة لهذه المحاولة: ~${cost_est:.4f} USD")
        print(f" مسار الفيديو النهائي: {LOCAL_OUTPUT_PATH}")
        print(f"==========================================", flush=True)

    finally:
        if pod_id:
            terminate_pod(pod_id)

if __name__ == "__main__":
    deploy_and_run()
