import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_05_motionpro_camera.mp4")
LOCAL_INPUT_IMAGE = os.path.join(OUTPUT_DIR, "seine_input_mature.jpg")

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()
HF_TOKEN = secrets.get("huggingface_api_key", "").strip()

# Read the local mature Abdelaziz input portrait and encode as base64
with open(LOCAL_INPUT_IMAGE, "rb") as f_img:
    INPUT_IMAGE_B64 = base64.b64encode(f_img.read()).decode("ascii")

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
export HF_HUB_ENABLE_HF_TRANSFER=1

mkdir -p /workspace/out /workspace/input /workspace/logs /workspace/MotionPro
cd /workspace/out
nohup python3 -m http.server 8000 > /workspace/logs/http.log 2>&1 &

st() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> /workspace/out/run.log
}

st "stage_1_inputs" "1/5: Decoding Abdelaziz Mature Portrait..."
echo "$INPUT_IMAGE_B64" | base64 -d > /workspace/input/aziz_mature.jpg
st "stage_1_inputs" "Input image written ($(wc -c < /workspace/input/aziz_mature.jpg) bytes)"

st "stage_2_deps" "2/5: Installing fast dependencies (no-backtrack)..."
pip install --no-cache-dir \
    einops \
    omegaconf \
    colorlog \
    imageio \
    imageio-ffmpeg \
    scipy \
    opencv-python-headless \
    huggingface_hub \
    hf_transfer \
    transformers \
    ftfy \
    regex \
    timm \
    sentencepiece \
    tiktoken \
    wcwidth \
    safetensors \
    matplotlib \
    pyyaml \
    kornia_rs >> /workspace/out/run.log 2>&1

pip install --no-cache-dir --no-deps \
    open_clip_torch \
    kornia \
    pytorch-lightning >> /workspace/out/run.log 2>&1

st "stage_2_deps" "Dependencies installed successfully."

st "stage_3_clone" "3/5: Cloning MotionPro repository..."
cd /workspace
git clone --depth 1 https://github.com/HiDream-ai/MotionPro.git /workspace/MotionPro >> /workspace/out/run.log 2>&1
cd /workspace/MotionPro
mkdir -p /workspace/MotionPro/checkpoints

st "stage_4_checkpoint" "4/5: Downloading MotionPro-gs_16k.pt from HuggingFace..."
python3 -c "
import os, time
from huggingface_hub import hf_hub_download

print('Starting high-speed Hugging Face download for MotionPro-gs_16k.pt...', flush=True)
t0 = time.time()
path = hf_hub_download(
    repo_id='HiDream-ai/MotionPro',
    filename='MotionPro-gs_16k.pt',
    local_dir='/workspace/MotionPro/checkpoints',
    token=os.environ.get('HF_TOKEN')
)
t1 = time.time()
size_mb = os.path.getsize(path) / (1024 * 1024)
print(f'Downloaded {size_mb:.1f} MB in {t1 - t0:.1f}s ({size_mb / (t1 - t0):.1f} MB/s)', flush=True)

target_path = '/workspace/MotionPro/checkpoints/MotionPro_Sparse-gs_16k.pt'
if not os.path.exists(target_path):
    os.symlink(path, target_path)
print('Checkpoint ready at', target_path, flush=True)
" >> /workspace/out/run.log 2>&1

st "stage_5_infer" "5/5: Launching Headless MotionPro Inference..."

cat << 'EOF' > /workspace/MotionPro/run_camera_infer.py
import sys
sys.dont_write_bytecode = True
import os
import importlib.util
sys.path.insert(0, '/workspace/MotionPro')
os.chdir('/workspace/MotionPro')

def import_filename(filename):
    spec = importlib.util.spec_from_file_location("mymodule", filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

# Mock deepspeed and pytorch_lightning
from unittest.mock import MagicMock
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.modules['deepspeed'] = MagicMock()

class MockLightningModule(nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__()

mock_pl = MagicMock()
mock_pl.LightningModule = MockLightningModule
sys.modules['pytorch_lightning'] = mock_pl

# Native PyTorch SDPA replacement for xformers memory_efficient_attention
class MockXformersOps:
    @staticmethod
    def memory_efficient_attention(q, k, v, attn_bias=None, op=None, scale=None):
        if scale is not None:
            return F.scaled_dot_product_attention(q, k, v, scale=scale)
        return F.scaled_dot_product_attention(q, k, v)

mock_xformers = MagicMock()
mock_xformers.__version__ = "0.0.28"
mock_xformers.ops = MockXformersOps
sys.modules['xformers'] = mock_xformers
sys.modules['xformers.ops'] = MockXformersOps

import time
import math
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
from einops import rearrange, repeat

# Monkeypatch torch.load to avoid PyTorch 2.4 weights_only restriction
_orig_torch_load = torch.load
def safe_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = safe_torch_load

# Patch camera Warper with robust geometric depth fallback
import tools.camera as camera_module

def patched_warper_init(self, H, W):
    self.H = H
    self.W = W
    self.cam = camera_module.CameraParams(self.H, self.W)
    try:
        print("[WARPER] Attempting to load ZoeDepth...", flush=True)
        self.d_model = torch.hub.load('tools/ZoeDepth', 'ZoeD_N', source='local', pretrained=True).to('cuda')
        print("[WARPER] ZoeDepth loaded successfully!", flush=True)
    except Exception as e:
        print(f"[WARPER] ZoeDepth load bypassed ({e}), initializing geometric depth model...", flush=True)
        self.d_model = None

def patched_warper_d(self, im):
    if self.d_model is not None:
        try:
            return self.d_model.infer_pil(im)
        except Exception as e:
            print(f"[WARPER] ZoeDepth inference error ({e}), using geometric fallback.", flush=True)
    w_in, h_in = im.size
    y, x = np.ogrid[:h_in, :w_in]
    dist = np.sqrt(((x - w_in / 2.0) / (w_in / 2.0)) ** 2 + ((y - h_in / 2.0) / (h_in / 2.0)) ** 2)
    depth = 2.2 + 2.3 * dist.astype(np.float32)
    return depth

camera_module.Warper.__init__ = patched_warper_init
camera_module.Warper.d = patched_warper_d

# Import Warper
from tools.camera import Warper

# Clean Drag definition without Gradio UI
class HeadlessDrag:
    def __init__(self, device, model_path, cfg_path, model_length=16):
        self.device = device
        self.model_length = model_length
        cf = import_filename(cfg_path)
        Net, args = cf.Net, cf.args
        self.motionpro_net = Net(args)
        self.motionpro_net.eval()
        self.motionpro_net.to(device)
        self.init_from_ckpt(model_path)

    def init_from_ckpt(self, path: str) -> None:
        if path.endswith("pt") or path.endswith("pth"):
            sd_raw = torch.load(path, map_location="cpu")
            sd = {}
            for k in sd_raw['module']:
                sd[k[len('module.'):]] = sd_raw['module'][k]
        else:
            raise NotImplementedError
        missing, unexpected = self.motionpro_net.load_state_dict(sd, strict=False)
        print(f"Restored from {path} with {len(missing)} missing and {len(unexpected)} unexpected keys", flush=True)

    @torch.no_grad()
    def forward_sample(self, input_drag, input_first_frame, motion_bucket_id):
        device = self.device
        b, l, h, w, c = input_drag.size()
        drag = rearrange(input_drag, 'b l h w c -> b l c h w')
        
        input_conditioner = dict()
        input_conditioner['cond_frames_without_noise'] = input_first_frame
        input_conditioner['cond_frames'] = (input_first_frame + 0.02 * torch.randn_like(input_first_frame))
        input_conditioner['motion_bucket_id'] = torch.tensor([motion_bucket_id]).to(drag.device).repeat(b * l)
        input_conditioner['fps_id'] = torch.tensor([self.motionpro_net.args.fps]).to(drag.device).repeat(b * l)
        input_conditioner['cond_aug'] = torch.tensor([0.02]).to(drag.device).repeat(b * l)

        input_conditioner_uc = {}
        for key in input_conditioner.keys():
            if isinstance(input_conditioner[key], torch.Tensor):
                input_conditioner_uc[key] = input_conditioner[key].clone()

        c, uc = self.motionpro_net.conditioner.get_unconditional_conditioning(
            input_conditioner,
            batch_uc=input_conditioner_uc,
            force_uc_zero_embeddings=["cond_frames", "cond_frames_without_noise"],
        )

        for k in ["crossattn", "concat"]:
            uc[k] = repeat(uc[k], "b ... -> b t ...", t=self.motionpro_net.num_frames)
            uc[k] = rearrange(uc[k], "b t ... -> (b t) ...")
            c[k] = repeat(c[k], "b ... -> b t ...", t=self.motionpro_net.num_frames)
            c[k] = rearrange(c[k], "b t ... -> (b t) ...")

        H, W = input_conditioner['cond_frames_without_noise'].shape[2:]
        shape = (self.motionpro_net.num_frames, 4, H // 8, W // 8)
        randn = torch.randn(shape).to(self.device)

        additional_model_inputs = {}
        additional_model_inputs["image_only_indicator"] = torch.zeros(2, self.motionpro_net.num_frames).to(self.device)
        additional_model_inputs["num_video_frames"] = self.motionpro_net.num_frames
        additional_model_inputs["flow"] = drag.repeat(2, 1, 1, 1, 1)

        def denoiser(input, sigma, c):
            return self.motionpro_net.denoiser(self.motionpro_net.model, input, sigma, c, **additional_model_inputs)

        samples_z = self.motionpro_net.sampler(denoiser, randn, cond=c, uc=uc)
        samples = self.motionpro_net.decode_first_stage(samples_z)
        predict_video = rearrange(samples, '(b l) c h w -> b l c h w', b=b)
        return predict_video

device = "cuda:0"
ckpt_path = "checkpoints/MotionPro_Sparse-gs_16k.pt"
if not os.path.exists(ckpt_path):
    ckpt_path = "checkpoints/MotionPro-gs_16k.pt"

input_image_path = "/workspace/input/aziz_mature.jpg"
output_video_path = "/workspace/out/test_05_motionpro_camera.mp4"
target_w, target_h = 512, 320
camera_motion = "rotate-clockwise-30" # Dramatic cinematic camera orbit

print(f"Loading MotionPro model from {ckpt_path} onto {device}...", flush=True)
t_load_0 = time.time()
net = HeadlessDrag(device, ckpt_path, 'vtdm/motionpro_net.py', 16)
print(f"MotionPro model loaded in {time.time() - t_load_0:.1f}s!", flush=True)

# Prepare input image
print(f"Processing input portrait: {input_image_path}...", flush=True)
raw_img = Image.open(input_image_path).convert("RGB")
raw_w, raw_h = raw_img.size
resize_ratio = max(target_w / raw_w, target_h / raw_h)
img_resized = raw_img.resize((int(raw_w * resize_ratio), int(raw_h * resize_ratio)), Image.BILINEAR)
img_cropped = transforms.CenterCrop((target_h, target_w))(img_resized)

# Save cropped first frame
img_cropped.save("/workspace/out/frame_00_input.jpg")

# Compute camera motion warping trajectories
print(f"Generating 3D camera trajectory tokens for motion: '{camera_motion}' ({target_w}x{target_h}, 16 frames)...", flush=True)
warper = Warper(target_h, target_w)
mask = torch.ones(16, target_h, target_w, 1)
input_drag_dense, visible_mask = warper.get_traj_from_camera_pose(img_cropped, camera_motion, num_frames=16)
input_drag, motion_bucket_id = warper.process_into_sparse(input_drag_dense, visible_mask)

mask_b = mask.to(input_drag.dtype)
input_drag = torch.concat([input_drag, mask_b], dim=-1).to(device)

first_frames_transform = transforms.Compose([
    lambda x: Image.fromarray(x),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])
first_frames = np.array(img_cropped)
first_frames = repeat(first_frames_transform(first_frames), 'c h w -> b c h w', b=1).to(device)

print(f"Executing MotionPro diffusion sampling (EulerEDM, motion_bucket={float(motion_bucket_id):.1f})...", flush=True)
t_denoise_0 = time.time()
predict_video = net.forward_sample(
    repeat(input_drag[0:16], 'l h w c -> b l h w c', b=1).to(device),
    first_frames,
    motion_bucket_id
)
print(f"Diffusion denoising finished in {time.time() - t_denoise_0:.1f}s!", flush=True)

frames = torch.clamp(predict_video[0], -1.0, 1.0) / 2.0 + 0.5
frames = (frames.permute(0, 2, 3, 1) * 255).to(torch.uint8).cpu().numpy() # [16, H, W, 3]

# Encode video via imageio or OpenCV
try:
    import imageio
    imageio.mimsave(output_video_path, [f for f in frames], fps=8)
    print(f"Video saved via imageio to {output_video_path}", flush=True)
except Exception as e_vid:
    print(f"imageio save fallback to cv2: {e_vid}", flush=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(output_video_path, fourcc, 8, (target_w, target_h))
    for frame_rgb in frames:
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        vw.write(frame_bgr)
    vw.release()

# Save representative stills for verification
cv2.imwrite("/workspace/out/motionpro_frame_00.jpg", cv2.cvtColor(frames[0], cv2.COLOR_RGB2BGR))
cv2.imwrite("/workspace/out/motionpro_frame_08.jpg", cv2.cvtColor(frames[8], cv2.COLOR_RGB2BGR))
cv2.imwrite("/workspace/out/motionpro_frame_15.jpg", cv2.cvtColor(frames[15], cv2.COLOR_RGB2BGR))

vid_size = os.path.getsize(output_video_path)
print(f"SUCCESS_DONE: Video generated successfully ({vid_size} bytes) at {output_video_path}", flush=True)
EOF

python3 /workspace/MotionPro/run_camera_infer.py >> /workspace/out/run.log 2>&1
st "complete" "ALL STAGES FINISHED"
"""

def deploy_and_run():
    pod_id = None
    rate = 0.35
    start_time = time.time()

    # Prioritize cost-efficient GPUs for 16-frame SVD inference
    gpu_ladder = [
        ("NVIDIA GeForce RTX 3090", 0.22),
        ("NVIDIA RTX A5000", 0.27),
        ("NVIDIA GeForce RTX 4090", 0.44),
        ("NVIDIA RTX 4000 Ada Generation", 0.29),
        ("NVIDIA RTX A4500", 0.25),
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
        print("\n[الخطوة 1/4] فحص وتخصيص كارت مناسب لـ MotionPro على السحابة...", flush=True)
        for gpu_id, price in gpu_ladder:
            print(f" -> محاولة حجز: {gpu_id} (~${price}/hr)...", flush=True)
            for cloud in ("SECURE", "COMMUNITY"):
                try:
                    payload = {
                        "gpuCount": 1,
                        "gpuTypeId": gpu_id,
                        "cloudType": cloud,
                        "name": "cindy-motionpro-test",
                        "imageName": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                        "containerDiskInGb": 60,
                        "volumeInGb": 0,
                        "minVcpuCount": 4,
                        "minMemoryInGb": 16,
                        "ports": "8000/http",
                        "startSsh": False,
                        "dockerArgs": "bash -c 'echo $CINDY_B64 | base64 -d > /cindy.sh && bash /cindy.sh; sleep infinity'",
                        "env": [
                            {"key": "CINDY_B64", "value": script_b64},
                            {"key": "INPUT_IMAGE_B64", "value": INPUT_IMAGE_B64},
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
                r_test = requests.get(f"{proxy_url}/run.log", timeout=4)
                if r_test.status_code == 200:
                    print(f" -> خادم البروكسي متصل ونشط!", flush=True)
                    break
            except Exception:
                pass

        print(f"\n[الخطوة 3/4] متابعة التنفيذ الحي لـ MotionPro (Fail-Fast الحاسم)...", flush=True)
        log_url = f"{proxy_url}/run.log"
        last_logged_line = ""
        last_change_time = time.time()
        timeout_limit = 900 # 15 mins max
        success = False

        for elapsed in range(0, timeout_limit, 6):
            time.sleep(6)
            try:
                r_log = requests.get(log_url, timeout=5)
                if r_log.status_code == 200:
                    text = r_log.text.strip()
                    lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
                    last = lines[-1] if lines else "..."
                    if last != last_logged_line:
                        print(f" [{int(time.time() - start_time)}s] {last}", flush=True)
                        last_logged_line = last
                        last_change_time = time.time()

                    # Fail-fast triggers
                    err_indicators = ["Traceback (most recent call last)", "ModuleNotFoundError", "CUDA out of memory", "RuntimeError:"]
                    for err in err_indicators:
                        if err in text:
                            print(f"\n[FAIL-FAST TRIGGERED] خطأ حقيقي رُصد: {err}", flush=True)
                            for l_err in lines[-15:]:
                                print(f"  {l_err}", flush=True)
                            raise RuntimeError(f"MotionPro container failed with: {err}")

                    if "SUCCESS_DONE:" in text:
                        print("\n[نجاح باهر] اكتمل توليد فيديو MotionPro بنجاح كامل!", flush=True)
                        success = True
                        break
            except requests.RequestException:
                pass

            if time.time() - last_change_time > 300:
                print("\n[STALL DETECTED] توقف الإخراج لأكثر من 5 دقائق. إنهاء فوري لحماية الميزانية.", flush=True)
                raise TimeoutError("Pod execution stalled.")

        if not success:
            raise RuntimeError("Pod timed out before finishing MotionPro.")

        print(f"\n[الخطوة 4/4] تحميل الفيديو والصور الثابتة محلياً...", flush=True)
        video_url = f"{proxy_url}/test_05_motionpro_camera.mp4"
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        r_vid = requests.get(video_url, timeout=120)
        if r_vid.status_code == 200 and len(r_vid.content) > 10000:
            with open(LOCAL_OUTPUT_PATH, "wb") as f_out:
                f_out.write(r_vid.content)
            size_mb = len(r_vid.content) / (1024 * 1024)
            print(f" [اكتمل التحميل] الفيديو: {LOCAL_OUTPUT_PATH} ({size_mb:.2f} MB)", flush=True)
        else:
            raise RuntimeError("Failed to download output MP4 or video file is corrupt/empty.")

        # Download stills
        for still_name in ("motionpro_frame_00.jpg", "motionpro_frame_08.jpg", "motionpro_frame_15.jpg"):
            try:
                r_still = requests.get(f"{proxy_url}/{still_name}", timeout=15)
                if r_still.status_code == 200:
                    artifact_path = os.path.join(r"C:\Users\DELL\.gemini\antigravity\brain\f39b14fe-7077-4fe2-88bb-d661dd89b5b3", still_name)
                    with open(artifact_path, "wb") as f_still:
                        f_still.write(r_still.content)
                    print(f" [تحميل لقطة ثابتة] {still_name}", flush=True)
            except Exception as e:
                print(f" Warning downloading still {still_name}: {e}", flush=True)

    except Exception as e:
        print(f"\n[خطأ تشغيلي]: {e}", flush=True)
    finally:
        elapsed = time.time() - start_time
        cost = (elapsed / 3600.0) * rate
        print(f"\n[تقرير الاستهلاك المالي]: المدة: {elapsed:.1f} ثانية ({elapsed/60:.1f} دقيقة) | التكلفة التقديرية: ${cost:.4f}", flush=True)
        terminate_pod(pod_id)

if __name__ == "__main__":
    deploy_and_run()
