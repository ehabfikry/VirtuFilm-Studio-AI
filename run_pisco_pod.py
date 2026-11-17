import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_08_pisco_insertion.mp4")
LOCAL_COMP_PATH = os.path.join(OUTPUT_DIR, "test_08_pisco_comparison.mp4")
BRAIN_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\f39b14fe-7077-4fe2-88bb-d661dd89b5b3"

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()

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

# Pod worker script executed inside the container
POD_WORKER_SCRIPT = r'''#!/usr/bin/env bash
set -e
mkdir -p /workspace/out
cd /workspace

# Start HTTP progress server
python3 -m http.server 8000 --directory /workspace/out &
HTTP_PID=$!
echo "[init] HTTP log server started on port 8000 (PID: $HTTP_PID)" > /workspace/out/run.log

exec >> /workspace/out/run.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_1_deps] 1/4: Installing dependencies & hf_transfer..."
export HF_HUB_ENABLE_HF_TRANSFER=1
pip install --no-cache-dir diffusers==0.30.3 transformers==4.44.2 accelerate==0.34.2 huggingface_hub==0.25.2 hf_transfer einops sentencepiece protobuf ftfy decord opencv-python-headless imageio imageio-ffmpeg pandas modelscope peft datasets wandb

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_2_repo] 2/4: Cloning taco-group/PISCO repository..."
if [ ! -d "/workspace/PISCO" ]; then
    git clone --depth 1 https://github.com/taco-group/PISCO.git /workspace/PISCO
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_3_weights] 3/4: Downloading PISCO-1.3B precision weights with hf_transfer..."
python3 - << 'EOF'
import os
import time
from huggingface_hub import snapshot_download

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
target_dir = "/workspace/PISCO/models/xiangbog/PISCO-1.3B"
os.makedirs(target_dir, exist_ok=True)
print(f"Downloading PISCO-1.3B to {target_dir}...", flush=True)
t0 = time.time()
snapshot_download(
    repo_id="xiangbog/PISCO-1.3B",
    local_dir=target_dir,
    allow_patterns=[
        "Wan2.1_VAE.safetensors",
        "diffusion_pytorch_model.safetensors",
        "models_t5_umt5-xxl-enc-bf16.safetensors",
        "google/umt5-xxl/*",
        "config.json"
    ]
)
dt = time.time() - t0
print(f"PISCO-1.3B models downloaded in {dt:.1f}s!", flush=True)
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_4_inference] 4/4: Executing PISCO 1.3B Video Instance Insertion..."
python3 - << 'EOF'
import os
import sys
import time
import glob
import torch
import numpy as np
from PIL import Image
import cv2

sys.path.append("/workspace/PISCO")
from diffsynth.pipelines.wan_video import WanVideoPipeline, ModelConfig
from diffsynth.utils.data import VideoData, save_video
from inference.utils import load_image_sequence

print(f"[PISCO] PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()} ({torch.cuda.get_device_name(0)})", flush=True)

print("[PISCO] Loading WanVideoPipeline 1.3B...", flush=True)
t_load = time.time()
pipe = WanVideoPipeline.from_pretrained(
    torch_dtype=torch.bfloat16,
    device="cuda",
    model_configs=[
        ModelConfig(model_id="xiangbog/PISCO-1.3B", origin_file_pattern="diffusion_pytorch_model*.safetensors"),
        ModelConfig(model_id="xiangbog/PISCO-1.3B", origin_file_pattern="models_t5_umt5-xxl-enc-bf16.safetensors"),
        ModelConfig(model_id="xiangbog/PISCO-1.3B", origin_file_pattern="Wan2.1_VAE.safetensors"),
    ],
    tokenizer_config=ModelConfig(model_id="xiangbog/PISCO-1.3B", origin_file_pattern="google/umt5-xxl/"),
)
print(f"[PISCO] Pipeline loaded in {time.time() - t_load:.1f}s!", flush=True)

base_path = "/workspace/PISCO/eval/example1"
print(f"[PISCO] Preparing inputs from {base_path}...", flush=True)

# 1. Load clean videos
pisco_video = VideoData(video_file=os.path.join(base_path, "clean.mp4"), height=480, width=832)
pisco_video.set_length(49)
pisco_depth = VideoData(video_file=os.path.join(base_path, "clean_depth.mp4"), height=480, width=832)
pisco_depth.set_length(49)

# 2. Load pre-masked image sequences (sparse reference)
pisco_video_mask = load_image_sequence(os.path.join(base_path, "mask"), height=480, width=832)
pisco_video_mask.set_length(49)

pisco_reference_video = load_image_sequence(os.path.join(base_path, "video_masked"), height=480, width=832)
pisco_reference_video.set_length(49)

pisco_reference_depth = load_image_sequence(os.path.join(base_path, "video_depth_masked"), height=480, width=832)
pisco_reference_depth.set_length(49)

# 3. Create sparse mask indicator (frames 10, 20, 46)
mask = torch.zeros(49, dtype=torch.bool).to(pipe.device)
mask[[10, 20, 46]] = True

print("[PISCO] Starting DiT diffusion generation (49 frames, 50 inference steps)...", flush=True)
t_gen = time.time()
video = pipe(
    prompt="",
    negative_prompt="",
    pisco_video=pisco_video,
    pisco_video_mask=(pisco_video_mask, mask),
    pisco_reference_video=(pisco_reference_video, mask),
    pisco_depth=(pisco_depth, mask),
    pisco_reference_depth=(pisco_reference_depth, mask),
    num_frames=49,
    num_inference_steps=50,
    seed=1,
    tiled=False
)
gen_duration = time.time() - t_gen
print(f"[PISCO] Generation complete in {gen_duration:.1f}s! ({len(video)} frames)", flush=True)

# Save Clean Generated Video
out_vid_path = "/workspace/out/test_08_pisco_insertion.mp4"
save_video(video, out_vid_path, fps=24, quality=5)
print(f"[PISCO] Inserted video saved: {out_vid_path} ({os.path.getsize(out_vid_path)} bytes)", flush=True)

# Save Side-by-Side Comparison Video [Original Background | PISCO Instance Insertion]
comp_path = "/workspace/out/test_08_pisco_comparison.mp4"
clean_cap = cv2.VideoCapture(os.path.join(base_path, "clean.mp4"))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
comp_writer = cv2.VideoWriter(comp_path, fourcc, 24.0, (832 * 2, 480))

for f_idx in range(len(video)):
    ret, clean_f = clean_cap.read()
    if not ret:
        clean_f = np.zeros((480, 832, 3), dtype=np.uint8)
    else:
        clean_f = cv2.resize(clean_f, (832, 480))
    gen_f = cv2.cvtColor(np.array(video[f_idx]), cv2.COLOR_RGB2BGR)
    gen_f = cv2.resize(gen_f, (832, 480))
    combined = np.hstack([clean_f, gen_f])
    comp_writer.write(combined)
clean_cap.release()
comp_writer.release()
print(f"[PISCO] Comparison video saved: {comp_path} ({os.path.getsize(comp_path)} bytes)", flush=True)

# Save keyframe stills
for f_idx, s_name in [(0, "pisco_frame_00.jpg"), (24, "pisco_frame_24.jpg"), (48, "pisco_frame_48.jpg")]:
    still_img = video[min(f_idx, len(video) - 1)]
    still_path = f"/workspace/out/{s_name}"
    still_img.save(still_path)
    print(f"[PISCO] Still saved: {still_path} ({os.path.getsize(still_path)} bytes)", flush=True)

print(f"SUCCESS_DONE: Video generated successfully ({os.path.getsize(out_vid_path)} bytes) at {out_vid_path}", flush=True)
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [complete] ALL PISCO STAGES FINISHED"
'''

def main():
    print("==================================================================", flush=True)
    print(" [DIRECTOR DIRECTIVE] Launching Tool #07: taco-group/PISCO (NeurIPS 2026)", flush=True)
    print(" Precise Video Instance Insertion with Sparse Control (DiffSynth + Wan2.1)", flush=True)
    print("==================================================================", flush=True)

    # 1. GPU Selection
    q_gpus = '''query {
      gpuTypes {
        id
        displayName
        memoryInGb
        lowestPrice(input: {gpuCount: 1}) {
          uninterruptablePrice
        }
      }
    }'''
    r_gpus = run_gql(q_gpus)
    all_gpus = r_gpus.get("gpuTypes", [])

    gpu_ladder = [
        ("NVIDIA GeForce RTX 4090", 0.44),
        ("NVIDIA GeForce RTX 3090", 0.22),
        ("NVIDIA A40", 0.59),
        ("NVIDIA RTX A5000", 0.27),
        ("NVIDIA RTX A6000", 0.33),
        ("NVIDIA RTX 4000 Ada Generation", 0.29),
        ("NVIDIA RTX 5000 Ada Generation", 0.49),
        ("NVIDIA L4", 0.38),
    ]

    # 2. Encode worker script in base64
    b64_script = base64.b64encode(POD_WORKER_SCRIPT.encode("utf-8")).decode("utf-8")

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

    pod_id = None
    selected_gpu = None
    selected_price = 0.50

    for gpu_id, ref_price in gpu_ladder:
        for cloud in ("SECURE", "COMMUNITY"):
            print(f"[POD] Attempting {gpu_id} on {cloud} cloud...", flush=True)
            payload = {
                "gpuCount": 1,
                "gpuTypeId": gpu_id,
                "cloudType": cloud,
                "name": "cindy-pisco-test08",
                "imageName": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                "containerDiskInGb": 50,
                "volumeInGb": 0,
                "ports": "8000/http",
                "startSsh": False,
                "dockerArgs": "bash -c 'echo $CINDY_B64 | base64 -d > /start.sh && chmod +x /start.sh && /start.sh; sleep infinity'",
                "env": [
                    {"key": "CINDY_B64", "value": b64_script}
                ]
            }

            try:
                res = run_gql(deploy_mutation, {"input": payload})
                pod = res.get("podFindAndDeployOnDemand")
                if pod and pod.get("id"):
                    pod_id = pod["id"]
                    selected_gpu = gpu_id
                    cost = pod.get("costPerHr")
                    if cost:
                        selected_price = float(cost)
                    else:
                        selected_price = ref_price
                    print(f"[POD] Success! Pod created on {selected_gpu} ({cloud}) at ${selected_price}/hr. ID: {pod_id}", flush=True)
                    break
            except Exception as e_dep:
                print(f" [RETRY] {gpu_id} ({cloud}) failed: {e_dep}. Trying next...", flush=True)
                time.sleep(1)

        if pod_id:
            break

    if not pod_id:
        raise RuntimeError("Failed to deploy on all candidate GPUs in ladder.")

    proxy_url = f"https://{pod_id}-8000.proxy.runpod.net"
    print(f"[POD] Monitoring proxy URL: {proxy_url}", flush=True)

    # Launch local monitor script
    monitor_script_path = r"C:\Users\DELL\Desktop\Cindy-AI-Director\monitor_pisco.py"
    monitor_code = f'''import os
import sys
import time
import json
import requests

POD_ID = "{pod_id}"
RATE = {selected_price}
PROXY_URL = "{proxy_url}"
OUTPUT_DIR = r"{OUTPUT_DIR}"
LOCAL_OUTPUT_PATH = r"{LOCAL_OUTPUT_PATH}"
LOCAL_COMP_PATH = r"{LOCAL_COMP_PATH}"
BRAIN_DIR = r"{BRAIN_DIR}"
SECRETS_PATH = r"{SECRETS_PATH}"

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()

def run_gql(query, variables=None):
    body = {{"query": query}}
    if variables:
        body["variables"] = variables
    headers = {{"Authorization": f"Bearer {{RUNPOD_KEY}}", "Content-Type": "application/json"}}
    r = requests.post("https://api.runpod.io/graphql", headers=headers, json=body, timeout=45)
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL Error: {{data['errors']}}")
    return data.get("data", {{}})

def terminate_pod(pod_id):
    if not pod_id:
        return
    print(f"\\n[SAFETY] Terminating pod {{pod_id}} immediately to protect balance...", flush=True)
    q = 'mutation($id: String!) {{ podTerminate(input: {{podId: $id}}) }}'
    for _ in range(3):
        try:
            run_gql(q, {{"id": pod_id}})
            print(f"[SAFETY] Pod {{pod_id}} TERMINATED. Zero lingering cost.", flush=True)
            return
        except Exception:
            time.sleep(3)

def main():
    print(f"[MONITOR] Attached to running pod: {{POD_ID}} ({selected_gpu} @ ${{RATE}}/hr)", flush=True)
    seen_lines = 0
    success = False

    try:
        # 180 ticks * 5s = 15 minutes max
        for tick in range(180):
            time.sleep(5)
            try:
                r = requests.get(f"{{PROXY_URL}}/run.log", timeout=5)
                if r.status_code == 200:
                    text = r.text
                    lines = text.strip().split("\\n")
                    if len(lines) > seen_lines:
                        for l in lines[seen_lines:]:
                            print(f" [POD] {{l}}", flush=True)
                        seen_lines = len(lines)

                    if "SUCCESS_DONE:" in text:
                        success = True
                        break

                    if "ModuleNotFoundError:" in text or "Traceback (most recent call last):" in text:
                        print(f"\\n[ERROR_DETECTED] Encountered fatal error in pod run.log. Aborting...", flush=True)
                        break

                    last_chunk = repr(text[-150:])
                    if "%|" in last_chunk:
                        idx = last_chunk.rfind("%|")
                        start_idx = max(0, idx - 4)
                        end_idx = min(len(last_chunk), idx + 45)
                        prog_str = last_chunk[start_idx:end_idx].replace(r"\\r", "").replace("'", "")
                        print(f" ... [DiT Progress] {{prog_str}}", flush=True)
            except Exception:
                pass

        if not success:
            raise RuntimeError("PISCO generation timed out or failed.")

        print("\\n[نجاح باهر] تم الانتهاء من توليد PISCO بنجاح! جارٍ التحميل...", flush=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Download Clean Video
        vid_url = f"{{PROXY_URL}}/test_08_pisco_insertion.mp4"
        r_vid = requests.get(vid_url, timeout=60)
        with open(LOCAL_OUTPUT_PATH, "wb") as f_out:
            f_out.write(r_vid.content)
        vid_size = os.path.getsize(LOCAL_OUTPUT_PATH)
        print(f" [تم التحميل] الفيديو النقي: {{LOCAL_OUTPUT_PATH}} ({{vid_size:,}} bytes)", flush=True)

        # Download Comparison Video
        comp_url = f"{{PROXY_URL}}/test_08_pisco_comparison.mp4"
        try:
            r_comp = requests.get(comp_url, timeout=60)
            with open(LOCAL_COMP_PATH, "wb") as f_comp:
                f_comp.write(r_comp.content)
            print(f" [تم التحميل] فيديو المقارنة: {{LOCAL_COMP_PATH}} ({{os.path.getsize(LOCAL_COMP_PATH):,}} bytes)", flush=True)
        except Exception as e_c:
            print(f" [تنبيه] تعذر تحميل فيديو المقارنة: {{e_c}}", flush=True)

        # Download Stills
        for still_name in ["pisco_frame_00.jpg", "pisco_frame_24.jpg", "pisco_frame_48.jpg"]:
            try:
                s_url = f"{{PROXY_URL}}/{{still_name}}"
                r_s = requests.get(s_url, timeout=10)
                local_s_path = os.path.join(BRAIN_DIR, still_name)
                with open(local_s_path, "wb") as f_s:
                    f_s.write(r_s.content)
                print(f" [تم التحميل] اللقطة: {{local_s_path}} ({{os.path.getsize(local_s_path):,}} bytes)", flush=True)
            except Exception as e_s:
                print(f" [تنبيه] تعذر تحميل {{still_name}}: {{e_s}}", flush=True)

        print("\\n==========================================")
        print(f" مسار الفيديو النهائي: {{LOCAL_OUTPUT_PATH}}")
        print("==========================================", flush=True)

    finally:
        terminate_pod(POD_ID)

if __name__ == "__main__":
    main()
'''
    with open(monitor_script_path, "w", encoding="utf-8") as f_m:
        f_m.write(monitor_code)
    print(f"[MONITOR] Monitor script written to {monitor_script_path}", flush=True)

if __name__ == "__main__":
    main()
