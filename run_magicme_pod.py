import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_09_magicme_idlock.mp4")
LOCAL_COMP_PATH = os.path.join(OUTPUT_DIR, "test_09_magicme_comparison.mp4")
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

POD_WORKER_SCRIPT = r'''#!/usr/bin/env bash
set -e
mkdir -p /workspace/out
mkdir -p /workspace/models
cd /workspace

# Start HTTP progress server
python3 -m http.server 8000 --directory /workspace/out &
HTTP_PID=$!
echo "[init] HTTP log server started on port 8000 (PID: $HTTP_PID)" > /workspace/out/run.log

exec >> /workspace/out/run.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_1_deps] 1/4: Installing dependencies & hf_transfer..."
export HF_HUB_ENABLE_HF_TRANSFER=1
pip install --no-cache-dir diffusers==0.22.1 transformers==4.29.0 accelerate==0.24.1 huggingface_hub==0.25.2 hf_transfer einops omegaconf safetensors opencv-python-headless imageio imageio-ffmpeg

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_2_repo] 2/4: Cloning Zhen-Dong/Magic-Me repository..."
if [ ! -d "/workspace/Magic-Me" ]; then
    git clone --depth 1 https://github.com/Zhen-Dong/Magic-Me.git /workspace/Magic-Me
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_3_weights] 3/4: Downloading SD 1.5, AnimateDiff Motion Module & ID Embeddings..."
python3 - << 'EOF'
import os
import time
import urllib.request
from huggingface_hub import snapshot_download, hf_hub_download

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# 1. Download SD 1.5 base models (VAE, text_encoder, tokenizer, unet)
print("Downloading runwayml/stable-diffusion-v1-5...", flush=True)
t0 = time.time()
snapshot_download(
    repo_id="runwayml/stable-diffusion-v1-5",
    local_dir="/workspace/models/StableDiffusion",
    allow_patterns=["vae/*", "text_encoder/*", "tokenizer/*", "unet/*", "scheduler/*", "model_index.json"]
)
print(f"SD 1.5 downloaded in {time.time() - t0:.1f}s!", flush=True)

# 2. Download AnimateDiff motion module
print("Downloading mm_sd_v15_v2.ckpt...", flush=True)
os.makedirs("/workspace/models/Motion_Module", exist_ok=True)
hf_hub_download(
    repo_id="guoyww/animatediff",
    filename="mm_sd_v15_v2.ckpt",
    local_dir="/workspace/models/Motion_Module"
)

# 3. Download RealisticVision V5.1 weights
print("Downloading Realistic_Vision_V5.1_fp16-no-ema.safetensors...", flush=True)
os.makedirs("/workspace/models/DreamBooth_LoRA", exist_ok=True)
hf_hub_download(
    repo_id="SG161222/Realistic_Vision_V5.1_noVAE",
    filename="Realistic_Vision_V5.1_fp16-no-ema.safetensors",
    local_dir="/workspace/models/DreamBooth_LoRA"
)

# 4. Download Pre-trained Biometric ID Embeddings from Magic-Me HF Space
os.makedirs("/workspace/models/embeddings", exist_ok=True)
for emb_name in ["altman.pt", "musk.pt", "zuck.pt"]:
    emb_url = f"https://huggingface.co/spaces/visionMaze/Magic-Me/resolve/main/models/embeddings/{emb_name}"
    urllib.request.urlretrieve(emb_url, f"/workspace/models/embeddings/{emb_name}")
    print(f"Downloaded ID embedding: {emb_name}", flush=True)

print("All weights and biometric embeddings ready!", flush=True)
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stage_4_inference] 4/4: Executing Magic-Me 3D Gaussian Noise Prior ID-Locked Inference..."
python3 - << 'EOF'
import os
import sys
import math
import time
import torch
from omegaconf import OmegaConf
from safetensors import safe_open
from diffusers import AutoencoderKL, DDIMScheduler
from transformers import CLIPTextModel, CLIPTokenizer
import cv2
import numpy as np

sys.path.append("/workspace/Magic-Me")
import animatediff.pipelines.vcd_pipeline_animation as vcd_pipeline_animation
from animatediff.models.unet import UNet3DConditionModel
from animatediff.utils.util import add_token, save_videos_grid
from animatediff.utils.convert_from_ckpt import convert_ldm_unet_checkpoint, convert_ldm_clip_checkpoint, convert_ldm_vae_checkpoint

print(f"[Magic-Me] PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()} ({torch.cuda.get_device_name(0)})", flush=True)

device = "cuda"
pretrained_path = "/workspace/models/StableDiffusion"
motion_module_path = "/workspace/models/Motion_Module/mm_sd_v15_v2.ckpt"
realistic_path = "/workspace/models/DreamBooth_LoRA/Realistic_Vision_V5.1_fp16-no-ema.safetensors"
embedding_path = "/workspace/models/embeddings/altman.pt"

modifier_tokens = ['<new1>', '<new2>', '<new3>', '<new4>']

print("[Magic-Me] Loading Base SD 1.5 & AnimateDiff 3D UNet...", flush=True)
tokenizer = CLIPTokenizer.from_pretrained(pretrained_path, subfolder="tokenizer")
text_encoder = CLIPTextModel.from_pretrained(pretrained_path, subfolder="text_encoder")
vae = AutoencoderKL.from_pretrained(pretrained_path, subfolder="vae")

unet_kwargs = {
    "use_inflated_groupnorm": True,
    "unet_use_cross_frame_attention": False,
    "unet_use_temporal_attention": False,
    "use_motion_module": True,
    "motion_module_resolutions": [1, 2, 4, 8],
    "motion_module_mid_block": True,
    "motion_module_decoder_only": False,
    "motion_module_type": "Vanilla",
    "motion_module_kwargs": {
        "num_attention_heads": 8,
        "num_transformer_block": 1,
        "attention_block_types": ["Temporal_Self", "Temporal_Self"],
        "temporal_position_encoding": True,
        "temporal_position_encoding_max_len": 32,
        "temporal_attention_dim_div": 1
    }
}

unet = UNet3DConditionModel.from_pretrained_2d(pretrained_path, subfolder="unet", unet_additional_kwargs=unet_kwargs)

print("[Magic-Me] Injecting Motion Module weights...", flush=True)
mm_state_dict = torch.load(motion_module_path, map_location="cpu")
unet.load_state_dict(mm_state_dict, strict=False)

print("[Magic-Me] Injecting RealisticVision V5.1 weights...", flush=True)
safetensor_dict = {}
with safe_open(realistic_path, framework="pt", device="cpu") as f:
    for key in f.keys():
        safetensor_dict[key] = f.get_tensor(key)

converted_unet = convert_ldm_unet_checkpoint(safetensor_dict, unet.config)
unet.load_state_dict(converted_unet, strict=False)
text_encoder = convert_ldm_clip_checkpoint(safetensor_dict, text_encoder)
converted_vae = convert_ldm_vae_checkpoint(safetensor_dict, vae.config)
vae.load_state_dict(converted_vae, strict=False)

print("[Magic-Me] Adding ID modifier tokens & injecting Biometric Identity Lock...", flush=True)
add_token(tokenizer, text_encoder, modifier_tokens)

# Load trained embedding weights into modifier tokens
emb_dict = torch.load(embedding_path, map_location="cpu", weights_only=False)
id_embeds = emb_dict['string_to_param']['*']  # shape [4, 768]
token_embeds = text_encoder.get_input_embeddings().weight.data

for idx, t in enumerate(modifier_tokens):
    token_id = tokenizer.convert_tokens_to_ids(t)
    token_embeds[token_id] = id_embeds[idx]
    print(f" Locked biometric token {t} (ID: {token_id}) with learned prior tensor", flush=True)

scheduler = DDIMScheduler(
    num_train_timesteps=1000,
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="linear",
    steps_offset=1,
    clip_sample=False
)

pipe = vcd_pipeline_animation.AnimationPipeline(
    unet=unet.to(device),
    vae=vae.to(device),
    tokenizer=tokenizer,
    text_encoder=text_encoder.to(device),
    scheduler=scheduler
).to(device)
pipe.enable_vae_slicing()

prompt = "photo of a <new1> <new2> <new3> <new4> man in casual clothes, natural skin, cinematic lighting, highly detailed face, sharp focus, 8k"
n_prompt = "semi-realistic, cgi, 3d, render, sketch, cartoon, anime, close up, cropped, bad anatomy, deformed, blurry, ugly, duplicate, morbid, extra limbs"

print(f"[Magic-Me] Generating 16-frame ID-Locked Video with 3D Gaussian Noise Prior (cov_alpha=0.05)...", flush=True)
t_gen = time.time()
generator = torch.Generator(device=device)
generator.manual_seed(42)

video_tensor = pipe(
    prompt=prompt,
    negative_prompt=n_prompt,
    video_length=16,
    height=512,
    width=512,
    num_inference_steps=25,
    guidance_scale=7.5,
    generator=generator,
    modifier_tokens=modifier_tokens,
    cov_alpha=0.05
).videos

gen_time = time.time() - t_gen
print(f"[Magic-Me] Generation finished in {gen_time:.1f}s!", flush=True)

# Save Clean Video (.mp4)
out_vid_path = "/workspace/out/test_09_magicme_idlock.mp4"
video_frames = video_tensor[0].permute(1, 2, 3, 0).cpu().numpy()  # [F, H, W, C]
video_frames = (video_frames * 255).astype(np.uint8)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_writer = cv2.VideoWriter(out_vid_path, fourcc, 8.0, (512, 512))
for f_idx in range(video_frames.shape[0]):
    frame_bgr = cv2.cvtColor(video_frames[f_idx], cv2.COLOR_RGB2BGR)
    out_writer.write(frame_bgr)
out_writer.release()
print(f"[Magic-Me] Clean video saved: {out_vid_path} ({os.path.getsize(out_vid_path)} bytes)", flush=True)

# Save Stills
cv2.imwrite("/workspace/out/magicme_frame_00.jpg", cv2.cvtColor(video_frames[0], cv2.COLOR_RGB2BGR))
cv2.imwrite("/workspace/out/magicme_frame_08.jpg", cv2.cvtColor(video_frames[7], cv2.COLOR_RGB2BGR))
cv2.imwrite("/workspace/out/magicme_frame_15.jpg", cv2.cvtColor(video_frames[-1], cv2.COLOR_RGB2BGR))

print(f"SUCCESS_DONE: Video generated successfully ({os.path.getsize(out_vid_path)} bytes) at {out_vid_path}", flush=True)
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [complete] ALL MAGIC-ME STAGES FINISHED"
'''

def main():
    print("==================================================================", flush=True)
    print(" [DIRECTOR DIRECTIVE] Launching Tool #08: Zhen-Dong/Magic-Me", flush=True)
    print(" Biometric Identity Lock & 3D Gaussian Noise Prior Video Generation", flush=True)
    print("==================================================================", flush=True)

    gpu_ladder = [
        ("NVIDIA GeForce RTX 3090", 0.22),
        ("NVIDIA GeForce RTX 4090", 0.34),
        ("NVIDIA RTX A6000", 0.33),
        ("NVIDIA A40", 0.35),
        ("NVIDIA RTX A5000", 0.27),
        ("NVIDIA RTX 5000 Ada Generation", 0.49),
        ("NVIDIA RTX 6000 Ada Generation", 0.74),
    ]

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
        for cloud in ("COMMUNITY", "SECURE"):
            print(f"[POD] Attempting {gpu_id} on {cloud} cloud...", flush=True)
            payload = {
                "gpuCount": 1,
                "gpuTypeId": gpu_id,
                "cloudType": cloud,
                "name": "cindy-magicme-test09",
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
                    selected_price = float(cost) if cost else ref_price
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

    monitor_script_path = r"C:\Users\DELL\Desktop\Cindy-AI-Director\monitor_magicme.py"
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

                    if "Traceback (most recent call last):" in text:
                        print(f"\\n[ERROR_DETECTED] Fatal error in pod log. Aborting...", flush=True)
                        break

                    last_chunk = repr(text[-150:])
                    if "%|" in last_chunk:
                        idx = last_chunk.rfind("%|")
                        start_idx = max(0, idx - 4)
                        end_idx = min(len(last_chunk), idx + 45)
                        prog_str = last_chunk[start_idx:end_idx].replace(r"\\r", "").replace("'", "")
                        print(f" ... [Diffusion Progress] {{prog_str}}", flush=True)
            except Exception:
                pass

        if not success:
            raise RuntimeError("Magic-Me generation timed out or failed.")

        print("\\n[نجاح باهر] تم الانتهاء من توليد Magic-Me بنجاح! جارٍ التحميل...", flush=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Download Clean Video
        vid_url = f"{{PROXY_URL}}/test_09_magicme_idlock.mp4"
        r_vid = requests.get(vid_url, timeout=60)
        with open(LOCAL_OUTPUT_PATH, "wb") as f_out:
            f_out.write(r_vid.content)
        vid_size = os.path.getsize(LOCAL_OUTPUT_PATH)
        print(f" [تم التحميل] فيديو قفل الهوية: {{LOCAL_OUTPUT_PATH}} ({{vid_size:,}} bytes)", flush=True)

        # Download Stills
        for still_name in ["magicme_frame_00.jpg", "magicme_frame_08.jpg", "magicme_frame_15.jpg"]:
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
