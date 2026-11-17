import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_04_motioncanvas_drone.mp4")

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()
HF_TOKEN = secrets.get("huggingface_api_key", "").strip()

# Approved Mature Abdelaziz Face Portrait
REF_FACE_URL = "https://v3b.fal.media/files/b/0ab2887d/Xw2oB2iSYg5b7hdeCBhgu_frame2_mature.jpg"
FLASH_ATTN_WHEEL = "https://huggingface.co/ehabfikry/cindy-wheels/resolve/main/flash_attn-2.7.4.post1+cu12torch2.4cxx11abiFALSE-cp311-cp311-linux_x86_64.whl"

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

mkdir -p /workspace/out /workspace/input /workspace/logs /workspace/models
cd /workspace/out
nohup python3 -m http.server 8000 > /workspace/logs/http.log 2>&1 &

st() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> /workspace/out/run.log
}

st "stage_1_inputs" "1/5: Downloading Abdelaziz Portrait..."
curl -sL "$REF_FACE_URL" -o /workspace/input/aziz_mature.jpg

st "stage_2_deps" "2/5: Installing diffusers, transformers (pinned <=4.46.3), decord, ftfy, oss2, hf_transfer, opencv..."
pip install --no-cache-dir "transformers>=4.44.0,<=4.46.3" diffusers einops sentencepiece accelerate peft oss2 decord imageio imageio-ffmpeg opencv-python-headless ftfy hf_transfer huggingface_hub >> /workspace/out/run.log 2>&1

st "stage_3_repo" "3/5: Cloning MotionCanvas repository & applying patches..."
git clone --depth 1 https://github.com/Doubiiu/MotionCanvas.git /workspace/MotionCanvas >> /workspace/out/run.log 2>&1
sed -i 's/weights_only=True/weights_only=False/g' /workspace/MotionCanvas/diffsynth/models/utils.py
sed -i 's/import decord/decord = None/' /workspace/MotionCanvas/diffsynth/pipelines/tracker_utils.py
sed -i 's/from decord import VideoReader/VideoReader = None/' /workspace/MotionCanvas/diffsynth/pipelines/tracker_utils.py
sed -i 's/from modelscope import snapshot_download/snapshot_download = None/' /workspace/MotionCanvas/diffsynth/models/downloader.py
cd /workspace/MotionCanvas
pip install -e . --no-deps >> /workspace/out/run.log 2>&1

st "stage_4_weights" "4/5: Parallel download of Wan2.1 + CLIP (Hugging Face) and model.pt (ModelScope)..."
mkdir -p /workspace/models/doubiiu/MotionCanvas /workspace/models/Wan2.1-T2V-1.3B

export HF_HUB_ENABLE_HF_TRANSFER=1
python3 -c "
import os
from huggingface_hub import snapshot_download
token = os.environ.get('HF_TOKEN')
print('Downloading Wan2.1 base weights, T5 and CLIP from Hugging Face...', flush=True)
snapshot_download('alibaba-pai/Wan2.1-Fun-1.3B-InP', local_dir='/workspace/models/Wan2.1-T2V-1.3B', token=token,
                  allow_patterns=['*.pth', 'google/*', 'xlm-roberta-large/*'])
print('Wan2.1, T5 and CLIP weights downloaded successfully from Hugging Face!', flush=True)
" >> /workspace/out/run.log 2>&1 &
PID_HF=$!

python3 -c "
import urllib.request, concurrent.futures, os, time

url = 'https://www.modelscope.cn/models/doubiiu/MotionCanvas/resolve/master/model.pt'
dest = '/workspace/models/doubiiu/MotionCanvas/model.pt'
os.makedirs(os.path.dirname(dest), exist_ok=True)

# Resolve final redirect URL once
for attempt in range(5):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            final_url = r.geturl()
            total = int(r.headers.get('Content-Length', 0))
        break
    except Exception:
        time.sleep(2)

print(f'Starting fast parallel download of model.pt ({total/1024/1024:.1f} MB)...', flush=True)
chunk_size = 16 * 1024 * 1024
chunks = [(i * chunk_size, min(total - 1, (i + 1) * chunk_size - 1)) for i in range((total + chunk_size - 1) // chunk_size)]
with open(dest, 'wb') as f:
    f.seek(total - 1)
    f.write(b'\0')

def dl_part(item):
    idx, (st, en) = item
    expected = en - st + 1
    for attempt in range(8):
        try:
            r = urllib.request.Request(final_url, headers={'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={st}-{en}'})
            with urllib.request.urlopen(r, timeout=30) as resp:
                data = bytearray()
                while len(data) < expected:
                    part = resp.read(min(2 * 1024 * 1024, expected - len(data)))
                    if not part:
                        break
                    data.extend(part)
                if len(data) == expected:
                    with open(dest, 'r+b') as f:
                        f.seek(st)
                        f.write(data)
                    return
        except Exception:
            time.sleep(1 + attempt)
    raise RuntimeError(f'Chunk {st}-{en} failed after 8 retries')

t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
    list(pool.map(dl_part, enumerate(chunks)))
print(f'Finished model.pt in {time.time()-t0:.1f}s ({os.path.getsize(dest)/1024/1024:.1f} MB)!', flush=True)
" >> /workspace/out/run.log 2>&1 &
PID_MS=$!

wait $PID_HF
wait $PID_MS
echo "All weights downloaded successfully in parallel!" >> /workspace/out/run.log

st "stage_5_inference" "5/5: Running MotionCanvas 3D Camera Drone/Orbit Generation..."
cat << 'PYEOF' > /workspace/run_inference.py
import builtins, sys, os
import torch
import torch.nn as nn
builtins.nn = nn
sys.modules['nn'] = nn

from PIL import Image
import numpy as np
print(f"PyTorch version: {torch.__version__}, CUDA available: {torch.cuda.is_available()}")

# Patch MotionCanvas pipeline bug (unbound num_frames_, height_, width_)
pipeline_path = "/workspace/MotionCanvas/diffsynth/pipelines/wan_video_motioncanvas.py"
with open(pipeline_path, "r", encoding="utf-8") as f:
    content = f.read()

target_str = "if training_visualization and latents_shape is not None:\n            num_frames_ = (num_frames-1)*4+1\n            height_ = height * 8\n            width_ = width * 8"
replacement_str = "num_frames_ = num_frames\n        height_ = height\n        width_ = width\n        if training_visualization and latents_shape is not None:\n            num_frames_ = (num_frames-1)*4+1\n            height_ = height * 8\n            width_ = width * 8"
if target_str in content:
    content = content.replace(target_str, replacement_str)

target_vae = 'self.load_models_to_device(["text_encoder"])'
replacement_vae = 'self.load_models_to_device(["text_encoder", "vae"])'
if target_vae in content:
    content = content.replace(target_vae, replacement_vae)

target_neg = "prompt_emb_nega = self.encode_prompt([negative_prompt] * len(prompt), positive=False)"
replacement_neg = "prompt_emb_nega = self.encode_prompt(negative_prompt if isinstance(negative_prompt, list) else [negative_prompt], positive=False)"
if target_neg in content:
    content = content.replace(target_neg, replacement_neg)

with open(pipeline_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched wan_video_motioncanvas.py successfully!")

# Patch downloader.py to ensure modelscope import never breaks
dl_path = "/workspace/MotionCanvas/diffsynth/models/downloader.py"
if os.path.exists(dl_path):
    with open(dl_path, "r", encoding="utf-8") as f_dl:
        dl_c = f_dl.read()
    dl_c = dl_c.replace("from modelscope import snapshot_download", "snapshot_download = None")
    with open(dl_path, "w", encoding="utf-8") as f_dl:
        f_dl.write(dl_c)
    print("Patched downloader.py successfully!")

# Patch tracker_utils.py to ensure decord/oss2 never breaks
tr_path = "/workspace/MotionCanvas/diffsynth/pipelines/tracker_utils.py"
if os.path.exists(tr_path):
    with open(tr_path, "r", encoding="utf-8") as f_tr:
        tr_c = f_tr.read()
    tr_c = tr_c.replace("import decord\nfrom decord import VideoReader", "decord = None\nVideoReader = None")
    with open(tr_path, "w", encoding="utf-8") as f_tr:
        f_tr.write(tr_c)
    print("Patched tracker_utils.py successfully!")

# Patch utils.py to ensure weights_only=False for PyTorch 2.4 unpickling
u_path = "/workspace/MotionCanvas/diffsynth/models/utils.py"
if os.path.exists(u_path):
    with open(u_path, "r", encoding="utf-8") as f_u:
        u_c = f_u.read()
    u_c = u_c.replace("weights_only=True", "weights_only=False")
    with open(u_path, "w", encoding="utf-8") as f_u:
        f_u.write(u_c)
    print("Patched utils.py to weights_only=False successfully!")

try:
    torch.serialization.add_safe_globals([set])
except Exception:
    pass

from diffsynth import ModelManager, WanVideoPipeline_motioncanvas, save_video
from diffsynth.pipelines.tracker_utils import create_pos_feature_map

print("Initializing ModelManager on CPU...")
model_manager = ModelManager(torch_dtype=torch.bfloat16, device="cpu")

model_paths = [
    "/workspace/models/Wan2.1-T2V-1.3B/Wan2.1_VAE.pth",
    "/workspace/models/Wan2.1-T2V-1.3B/models_t5_umt5-xxl-enc-bf16.pth",
    "/workspace/models/Wan2.1-T2V-1.3B/models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth",
    "/workspace/models/doubiiu/MotionCanvas/model.pt",
]

for p in model_paths:
    print(f"Loading {p} ({os.path.getsize(p) / 1024 / 1024:.1f} MB)...")
    model_manager.load_models([p])

print("Building WanVideoPipeline_motioncanvas...")
pipe = WanVideoPipeline_motioncanvas.from_model_manager(model_manager, torch_dtype=torch.bfloat16, device="cuda")

if pipe.dit is None:
    print("Direct fallback instantiation for WanModelMotionCanvas...")
    from diffsynth.models.wan_video_motioncanvas import WanModel as WanModelMotionCanvas
    state_dict = torch.load("/workspace/models/doubiiu/MotionCanvas/model.pt", map_location="cpu")
    if "state_dict" in state_dict:
        state_dict = state_dict["state_dict"]
    elif "module" in state_dict:
        state_dict = state_dict["module"]
    dit = WanModelMotionCanvas(
        has_image_input=True,
        patch_size=[1, 2, 2],
        in_dim=36,
        dim=1536,
        ffn_dim=8960,
        freq_dim=256,
        text_dim=4096,
        out_dim=16,
        num_heads=12,
        num_layers=30,
        eps=1e-6
    )
    clean_sd = {}
    for k, v in state_dict.items():
        new_k = k
        for prefix in ["pipe.dit.", "pipe.denoising_model.", "dit.", "denoising_model.", "module."]:
            if new_k.startswith(prefix):
                new_k = new_k[len(prefix):]
        clean_sd[new_k] = v
    dit.load_state_dict(clean_sd, strict=False)
    pipe.dit = dit.to(dtype=torch.bfloat16, device="cuda")

    bbox_sd = {}
    for k, v in state_dict.items():
        for prefix in ["pipe.bbox_zeroconv.", "bbox_zeroconv."]:
            if k.startswith(prefix):
                bbox_sd[k[len(prefix):]] = v
    if bbox_sd:
        pipe.bbox_zeroconv.load_state_dict(bbox_sd, strict=False)
        print("Loaded trained bbox_zeroconv weights from checkpoint!")
    pipe.bbox_zeroconv = pipe.bbox_zeroconv.to(dtype=torch.bfloat16, device="cuda")

print("Enabling VRAM management across pipeline modules...")
pipe.enable_vram_management()

# Construct Synthetic Cinematic Camera Drone Trajectory:
# 49 frames, 832x480 resolution
B = 1
T = 49
H = 480
W = 832
grid_size = 12
N = grid_size * grid_size

y = torch.linspace(40, H - 40, grid_size)
x = torch.linspace(40, W - 40, grid_size)
gy, gx = torch.meshgrid(y, x, indexing='ij')
pts_0 = torch.stack([gx.flatten(), gy.flatten()], dim=-1)

# Drone orbit: smooth curved camera movement
tracks = []
for t in range(T):
    angle = 0.35 * (t / (T - 1))
    shift_x = - 90.0 * np.sin(angle)
    shift_y = 30.0 * (1 - np.cos(angle))
    pts_t = pts_0.clone()
    pts_t[:, 0] += float(shift_x)
    pts_t[:, 1] += float(shift_y)
    tracks.append(pts_t)

pred_tracks = torch.stack(tracks, dim=0).unsqueeze(0) # [1, 49, 144, 2]
pred_visibility = torch.ones(B, T, N, dtype=torch.bool)

print("Synthesizing 3D camera trajectory feature map...")
feat_map, _ = create_pos_feature_map(
    pred_tracks=pred_tracks,
    pred_visibility=pred_visibility,
    downsample_ratios=[4, 8, 8],
    height=H,
    width=W,
    pos_emb_dim=16,
    track_num=N,
    t_down_strategy="sample",
    device=torch.device("cpu"),
    dtype=torch.float32
)
track_video = feat_map.permute(0, 4, 1, 2, 3).to(dtype=torch.bfloat16, device="cuda") # [1, 16, 13, 60, 104]

# Bounding box mask: centered on Abdelaziz
bbox_mask = torch.zeros(1, 3, T, H, W, dtype=torch.bfloat16, device="cuda")
bbox_mask[:, :, :, int(H*0.1):int(H*0.9), int(W*0.25):int(W*0.75)] = 1.0

# Load Abdelaziz Portrait
input_image = Image.open("/workspace/input/aziz_mature.jpg").convert("RGB").resize((W, H))

print("Starting MotionCanvas Video Generation (49 frames @ 832x480, 25 steps)...")
prompt = ["Cinematic shot, dynamic drone orbit camera movement around mature Egyptian man Abdelaziz, detailed lighting, photorealistic 8k, movie scene, smooth parallax"]
negative_prompt = ["Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, static, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, deformed"]

video = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    input_image=input_image,
    height=H,
    width=W,
    num_frames=T,
    num_inference_steps=25,
    bbox_mask=bbox_mask,
    track_video=track_video,
    tiled=True,
    seed=42
)

out_file = "/workspace/out/test_04_motioncanvas_drone.mp4"
os.makedirs("/workspace/out/frames", exist_ok=True)
frames_list = video[0]
print(f"Saving {len(frames_list)} frames to disk...")
for i, frame in enumerate(frames_list):
    frame.save(f"/workspace/out/frames/frame_{i:04d}.png")

print("Encoding MP4 video from generated frames...")
try:
    save_video(frames_list, out_file, fps=15)
    print("Encoded video via diffsynth.save_video successfully!")
except Exception as e:
    print(f"diffsynth.save_video note: {e}")

if not os.path.exists(out_file) or os.path.getsize(out_file) < 1000:
    print("Encoding video via OpenCV VideoWriter fallback...")
    import cv2
    h, w = frames_list[0].size[1], frames_list[0].size[0]
    vw = cv2.VideoWriter(out_file, cv2.VideoWriter_fourcc(*'mp4v'), 15, (w, h))
    for frame in frames_list:
        vw.write(cv2.cvtColor(np.array(frame.convert("RGB")), cv2.COLOR_RGB2BGR))
    vw.release()

if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
    print(f"MotionCanvas video saved successfully to {out_file} ({os.path.getsize(out_file)} bytes)!")
else:
    raise FileNotFoundError("Failed to generate valid MP4 output file")
PYEOF

python3 /workspace/run_inference.py >> /workspace/out/run.log 2>&1

VID=$(find /workspace/out -name "*.mp4" 2>/dev/null | head -1)
if [ -n "$VID" ]; then
    cp "$VID" /workspace/out/test_04_motioncanvas_drone.mp4
    st "done" "SUCCESS_DONE: MotionCanvas video generated successfully ($(stat -c %s /workspace/out/test_04_motioncanvas_drone.mp4) bytes)"
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
        print(" VirtuFilm Studio AI: MotionCanvas Camera Control Evaluation", flush=True)
        print(" Director: Ehab Fikry | Asset: Mature Abdelaziz 3D Drone Shot", flush=True)
        print(" Repository: Doubiiu/MotionCanvas (SIGGRAPH 2025)", flush=True)
        print("=" * 70, flush=True)

        gpu_ladder = [
            ("NVIDIA RTX A5000", 0.27),
            ("NVIDIA GeForce RTX 4090", 0.34),
            ("NVIDIA GeForce RTX 3090", 0.22),
            ("NVIDIA A40", 0.59),
            ("NVIDIA RTX A6000", 0.69),
            ("NVIDIA RTX 6000 Ada Generation", 0.74),
            ("NVIDIA L40S", 0.79)
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
                        "name": "cindy-motioncanvas-test",
                        "imageName": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                        "containerDiskInGb": 70,
                        "volumeInGb": 0,
                        "minVcpuCount": 4,
                        "minMemoryInGb": 16,
                        "ports": "8000/http",
                        "startSsh": False,
                        "dockerArgs": "bash -c 'echo $CINDY_B64 | base64 -d > /cindy.sh && bash /cindy.sh; sleep infinity'",
                        "env": [
                            {"key": "CINDY_B64", "value": script_b64},
                            {"key": "REF_FACE_URL", "value": REF_FACE_URL},
                            {"key": "FLASH_ATTN_WHEEL", "value": FLASH_ATTN_WHEEL},
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
                except Exception as e:
                    time.sleep(1)
            if pod_id:
                break

        if not pod_id:
            raise RuntimeError("All cloud GPUs currently unavailable or out of stock.")

        proxy_url = f"https://{pod_id}-8000.proxy.runpod.net"
        print(f"\n[الخطوة 2/4] انتظار تفعيل الحاوية وخادم البروكسي: {proxy_url}...", flush=True)

        for wait_s in range(0, 180, 5):
            time.sleep(5)
            try:
                r_test = requests.get(f"{proxy_url}/run.log", timeout=4)
                if r_test.status_code == 200:
                    print(f" -> البروكسي جاهز ومتصل بنجاح!", flush=True)
                    break
            except Exception:
                pass

        print(f"\n[الخطوة 3/4] متابعة التنفيذ الحي والريست (Fail-Fast Active)...", flush=True)
        log_url = f"{proxy_url}/run.log"
        last_logged_line = ""
        stuck_error_count = 0
        last_change_time = time.time()
        timeout_limit = 1200 # 20 mins max

        for elapsed in range(0, timeout_limit, 8):
            time.sleep(8)
            try:
                r_log = requests.get(log_url, timeout=6)
                if r_log.status_code == 200:
                    text = r_log.text.strip()
                    lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
                    last = lines[-1] if lines else "..."
                    if last != last_logged_line:
                        print(f" [{int(time.time() - start_time)}s] {last}", flush=True)
                        last_logged_line = last
                        last_change_time = time.time()

                    # Fail-fast detection on genuine errors
                    err_indicators = ["Traceback (most recent call last)", "ModuleNotFoundError", "CUDA out of memory", "ERROR_FAILED", "RuntimeError"]
                    for err in err_indicators:
                        if err in text:
                            print(f"\n[FAIL-FAST TRIGGERED] Detected failure: {err}", flush=True)
                            print(f"--- Full Error Tail ---", flush=True)
                            for l_err in lines[-15:]:
                                print(f"  {l_err}", flush=True)
                            print(f"Terminating immediately to conserve director budget.", flush=True)
                            raise RuntimeError(f"MotionCanvas container failed with: {err}")

                    if "SUCCESS_DONE:" in text:
                        print("\n[نجاح باهر] تم توليد فيديو MotionCanvas بنجاح!", flush=True)
                        success = True
                        break
            except requests.RequestException:
                pass

            if time.time() - last_change_time > 360:
                print("\n[STALL DETECTED] No output from pod for 6 minutes. Aborting to prevent spend waste.", flush=True)
                raise TimeoutError("Pod stalled during execution.")

        if not success:
            raise RuntimeError("Pod timed out before completing MotionCanvas execution.")

        print(f"\n[الخطوة 4/4] تحميل ملف الفيديو النهائي محلياً...", flush=True)
        video_url = f"{proxy_url}/test_04_motioncanvas_drone.mp4"
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        r_vid = requests.get(video_url, timeout=120)
        if r_vid.status_code == 200 and len(r_vid.content) > 10000:
            with open(LOCAL_OUTPUT_PATH, "wb") as f_out:
                f_out.write(r_vid.content)
            size_mb = len(r_vid.content) / (1024 * 1024)
            print(f" [اكتمل التحميل] {LOCAL_OUTPUT_PATH} ({size_mb:.2f} MB)", flush=True)
        else:
            raise RuntimeError("Failed to download output MP4 or file is empty.")

    except Exception as e:
        print(f"\n[خطأ تشغيلي]: {e}", flush=True)
    finally:
        elapsed = time.time() - start_time
        cost = (elapsed / 3600.0) * rate
        print(f"\n[تقرير الاستهلاك المالي]: المدة: {elapsed:.1f} ثانية ({elapsed/60:.1f} دقيقة) | التكلفة التقديرية: ${cost:.4f}", flush=True)
        terminate_pod(pod_id)

if __name__ == "__main__":
    deploy_and_run()
