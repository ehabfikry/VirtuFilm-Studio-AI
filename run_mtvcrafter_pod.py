import os
import sys
import time
import json
import base64
import requests

SECRETS_PATH = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
LOCAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "test_07_mtvcrafter_4dmot.mp4")
LOCAL_COMP_PATH = os.path.join(OUTPUT_DIR, "test_07_mtvcrafter_comparison.mp4")
LOCAL_INPUT_IMAGE = os.path.join(OUTPUT_DIR, "seine_input_mature.jpg")
BRAIN_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\f39b14fe-7077-4fe2-88bb-d661dd89b5b3"

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

RUNPOD_KEY = secrets.get("runpod_api_key", "").strip()
HF_TOKEN = secrets.get("huggingface_api_key", "").strip()

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
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_ENABLE_HF_TRANSFER=1

mkdir -p /workspace/out /workspace/input /workspace/logs /workspace/checkpoints /workspace/MTVCrafter
cd /workspace/out
nohup python3 -m http.server 8000 > /workspace/logs/http.log 2>&1 &

st() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> /workspace/out/run.log
}

st "stage_1_inputs" "1/5: Decoding Abdelaziz 512x512 portrait..."
echo "$INPUT_IMAGE_B64" | base64 -d > /workspace/input/aziz_mature.jpg
st "stage_1_inputs" "Input image written ($(wc -c < /workspace/input/aziz_mature.jpg) bytes)"

st "stage_2_deps" "2/5: Installing diffusion, vision and fast hf_transfer dependencies..."
pip install --no-cache-dir \
    "diffusers==0.30.3" \
    "transformers==4.44.2" \
    "accelerate==0.34.2" \
    "huggingface_hub==0.25.2" \
    hf_transfer \
    opencv-python-headless \
    imageio \
    imageio-ffmpeg \
    decord \
    einops \
    torchvision >> /workspace/out/run.log 2>&1
st "stage_2_deps" "Dependencies installed successfully."

st "stage_3_clone" "3/5: Cloning MTVCrafter ICLR 2026 repository..."
cd /workspace
git clone --depth 1 https://github.com/DINGYANB/MTVCrafter.git /workspace/MTVCrafter >> /workspace/out/run.log 2>&1
cd /workspace/MTVCrafter

st "stage_4_checkpoints" "4/5: High-speed parallel download of precision checkpoints (hf_transfer)..."
python3 -c "
import os, time
from huggingface_hub import hf_hub_download

token = os.environ.get('HF_TOKEN')

def dl(repo, filename, local_dir):
    t0 = time.time()
    p = hf_hub_download(repo_id=repo, filename=filename, local_dir=local_dir, token=token)
    t1 = time.time()
    sz_mb = os.path.getsize(p) / (1024 * 1024)
    speed = sz_mb / max(t1 - t0, 0.001)
    print(f'[HF_SPEED] {filename} -> {sz_mb:.1f} MB in {t1 - t0:.1f}s ({speed:.1f} MB/s)', flush=True)

print('Starting high-speed hf_transfer downloads...', flush=True)
dl('yanboding/MTVCrafter', '4DMoT/mp_rank_00_model_states.pt', '/workspace/checkpoints/MTVCrafter')
dl('yanboding/MTVCrafter', 'MV-DiT/CogVideoX/config.json', '/workspace/checkpoints/MTVCrafter')
dl('yanboding/MTVCrafter', 'MV-DiT/CogVideoX/diffusion_pytorch_model.bin', '/workspace/checkpoints/MTVCrafter')

dl('THUDM/CogVideoX-5b', 'vae/diffusion_pytorch_model.safetensors', '/workspace/checkpoints/CogVideoX-5b')
dl('THUDM/CogVideoX-5b', 'vae/config.json', '/workspace/checkpoints/CogVideoX-5b')
dl('THUDM/CogVideoX-5b', 'scheduler/scheduler_config.json', '/workspace/checkpoints/CogVideoX-5b')
dl('THUDM/CogVideoX-5b', 'model_index.json', '/workspace/checkpoints/CogVideoX-5b')

print('[HF_SPEED] All 7 checkpoints verified and ready on NVMe!', flush=True)
" >> /workspace/out/run.log 2>&1

st "stage_5_infer" "5/5: Launching Headless MTVCrafter 4D Motion Token Inference..."

cat << 'EOF' > /workspace/MTVCrafter/run_cindy_mtvcrafter.py
import os
import sys
import copy
import time
import torch
import cv2
import imageio
import numpy as np
from PIL import Image
from torchvision import transforms
from torchvision.transforms import functional as F
from torchvision.transforms import ToPILImage, InterpolationMode

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

sys.path.insert(0, '/workspace/MTVCrafter')
os.chdir('/workspace/MTVCrafter')

from models import MTVCrafterPipeline7B
from models import VectorQuantizer, Encoder, Decoder, SMPL_VQVAE
from draw_pose import get_pose_images

def concat_images(images, direction='horizontal', pad=0, pad_value=0):
    if len(images) == 1:
        return images[0]
    is_pil = isinstance(images[0], Image.Image)
    if is_pil:
        images = [np.array(image) for image in images]
    if direction == 'horizontal':
        height = max([image.shape[0] for image in images])
        width = sum([image.shape[1] for image in images]) + pad * (len(images) - 1)
        new_image = np.full((height, width, images[0].shape[2]), pad_value, dtype=images[0].dtype)
        begin = 0
        for image in images:
            end = begin + image.shape[1]
            new_image[: image.shape[0], begin:end] = image
            begin = end + pad
    elif direction == 'vertical':
        height = sum([image.shape[0] for image in images]) + pad * (len(images) - 1)
        width = max([image.shape[1] for image in images])
        new_image = np.full((height, width, images[0].shape[2]), pad_value, dtype=images[0].dtype)
        begin = 0
        for image in images:
            end = begin + image.shape[0]
            new_image[begin:end, : image.shape[1]] = image
            begin = end + pad
    else:
        assert False
    if is_pil:
        new_image = Image.fromarray(new_image)
    return new_image

def concat_images_grid(images, cols, pad=0, pad_value=0):
    new_images = []
    while len(images) > 0:
        new_image = concat_images(images[:cols], pad=pad, pad_value=pad_value)
        new_images.append(new_image)
        images = images[cols:]
    new_image = concat_images(new_images, direction='vertical', pad=pad, pad_value=pad_value)
    return new_image

def get_new_height_width(data_dict, dst_height, dst_width):
    height = data_dict['video_height']
    width = data_dict['video_width']
    if float(dst_height) / height < float(dst_width) / width:
        new_height = int(round(float(dst_width) / width * height))
        new_width = dst_width
    else:
        new_height = dst_height
        new_width = int(round(float(dst_height) / height * width))
    assert dst_width <= new_width and dst_height <= new_height
    return new_height, new_width

def sample_video_safe(video_path, indexes):
    cap = cv2.VideoCapture(video_path)
    all_frames = []
    max_idx = indexes.max() + 1
    count = 0
    while count < max_idx:
        ret, frame = cap.read()
        if not ret:
            break
        all_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        count += 1
    cap.release()
    if len(all_frames) == 0:
        raise RuntimeError("No frames read from " + video_path)
    all_frames = np.array(all_frames)
    return all_frames[indexes]

def main():
    device = 'cuda:0'
    dst_width, dst_height = (512, 512)
    num_frames = 49
    guidance_scale = 3.0
    to_pil = ToPILImage()
    normalize = transforms.Normalize([0.5], [0.5])
    
    ref_image_path = "/workspace/input/aziz_mature.jpg"
    motion_data_path = "data/sampled_data.pkl"
    output_dir = "/workspace/out"

    print("[MTVCRAFTER] Loading motion sequence pickle...", flush=True)
    import pickle
    with open(motion_data_path, 'rb') as f:
        data_list = pickle.load(f)
    if not isinstance(data_list, list):
        data_list = [data_list]
    
    data = data_list[0]
    print(f"[MTVCRAFTER] Selected sequence 0: {data['video_path']}, total frames={data['video_length']}", flush=True)

    global_mean = np.load('data/mean.npy')
    global_std = np.load('data/std.npy')

    mtv_base = "/workspace/checkpoints/MTVCrafter"
    cog_base = "/workspace/checkpoints/CogVideoX-5b"

    print("[MTVCRAFTER] Loading MTVCrafterPipeline7B (CogVideoX-5b backbone + MV-DiT)...", flush=True)
    t0 = time.time()
    pipe = MTVCrafterPipeline7B.from_pretrained(
        model_path=cog_base,
        transformer_model_path=os.path.join(mtv_base, "MV-DiT/CogVideoX"),
        torch_dtype=torch.bfloat16,
        scheduler_type='dpm',
    )
    
    # Enable VRAM optimizations
    try:
        pipe.enable_model_cpu_offload()
        print("[MTVCRAFTER] Model CPU offload enabled successfully!", flush=True)
    except Exception as e_off:
        print(f"[MTVCRAFTER] CPU offload fallback ({e_off}), placing on cuda:0...", flush=True)
        pipe = pipe.to(device)

    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    t1 = time.time()
    print(f"[MTVCRAFTER] Main DiT Pipeline loaded in {t1 - t0:.1f}s!", flush=True)

    print("[MTVCRAFTER] Loading 4DMoT VQ-VAE model...", flush=True)
    motion_encoder = Encoder(
        in_channels=3,
        mid_channels=[128, 512],
        out_channels=3072,
        downsample_time=[2, 2],
        downsample_joint=[1, 1]
    )
    motion_quant = VectorQuantizer(nb_code=8192, code_dim=3072, is_train=False)
    motion_decoder = Decoder(
        in_channels=3072,
        mid_channels=[512, 128],
        out_channels=3,
        upsample_rate=2.0,
        frame_upsample_rate=[2.0, 2.0],
        joint_upsample_rate=[1.0, 1.0]
    )
    ckpt_path = os.path.join(mtv_base, "4DMoT/mp_rank_00_model_states.pt")
    state_dict = torch.load(ckpt_path, map_location="cpu")
    vqvae = SMPL_VQVAE(motion_encoder, motion_decoder, motion_quant).to(device)
    vqvae.load_state_dict(state_dict['module'], strict=True)
    vqvae.eval()
    print("[MTVCRAFTER] 4DMoT VQ-VAE ready!", flush=True)

    new_height, new_width = get_new_height_width(data, dst_height, dst_width)
    x1 = (new_width - dst_width) // 2
    y1 = (new_height - dst_height) // 2

    # Deterministic frame sampling for 49 frames
    sample_indexes = np.linspace(0, num_frames - 1, num_frames, dtype=int)
    print("Sample indexes:", sample_indexes[:5], "...", sample_indexes[-5:], flush=True)

    try:
        input_images = sample_video_safe(data['video_path'], sample_indexes)
        input_images = torch.from_numpy(input_images).permute(0, 3, 1, 2).contiguous()
        input_images = F.resize(input_images, (new_height, new_width), InterpolationMode.BILINEAR)
        input_images = F.crop(input_images, y1, x1, dst_height, dst_width)
    except Exception as e_vid:
        print(f"[MTVCRAFTER] Fallback for input video: {e_vid}", flush=True)
        input_images = torch.zeros((num_frames, 3, dst_height, dst_width))

    print(f"[MTVCRAFTER] Reading character reference image: {ref_image_path}...", flush=True)
    ref_image = Image.open(ref_image_path).convert("RGB")
    ref_image = torch.from_numpy(np.array(ref_image)).permute(2, 0, 1).contiguous()
    ref_images = torch.stack([ref_image.clone() for _ in range(num_frames)])
    ref_images = F.resize(ref_images, (new_height, new_width), InterpolationMode.BILINEAR)
    ref_images = F.crop(ref_images, y1, x1, dst_height, dst_width)

    # 3D SMPL Poses
    try:
        smpl_poses = np.array([pose[0][0].cpu().numpy() for pose in data['pose']['joints3d_nonparam']])
        poses = smpl_poses[sample_indexes]
    except Exception:
        poses = data['pose'][sample_indexes]

    norm_poses = torch.tensor((poses - global_mean) / global_std, dtype=torch.float32)

    height, width = data['video_height'], data['video_width']
    offset = [height, width, 0]
    pose_images_before = get_pose_images(copy.deepcopy(poses), offset)
    pose_images_before = [image.resize((new_width, new_height)).crop((x1, y1, x1+dst_width, y1+dst_height)) for image in pose_images_before]

    input_smpl_joints = norm_poses.unsqueeze(0).to(device)
    with torch.no_grad():
        motion_tokens, vq_loss = vqvae(input_smpl_joints, return_vq=True)
        print(f"[MTVCRAFTER] 4D Motion Token VQ Loss: {vq_loss.item():.4f}", flush=True)
        output_motion, _ = vqvae(input_smpl_joints)
        pose_images_after = get_pose_images(output_motion[0].cpu().detach() * global_std + global_mean, offset)
        pose_images_after = [image.resize((new_width, new_height)).crop((x1, y1, x1+dst_width, y1+dst_height)) for image in pose_images_after]

    input_images = normalize(input_images / 255.0)
    ref_images = normalize(ref_images / 255.0)

    print(f"[MTVCRAFTER] Starting 49-frame DiT Generation (guidance={guidance_scale}, steps=50)...", flush=True)
    t_start = time.time()
    
    with torch.no_grad():
        output_images = pipe(
            height=dst_height,
            width=dst_width,
            num_frames=num_frames,
            num_inference_steps=50,
            guidance_scale=guidance_scale,
            seed=42,
            ref_images=ref_images,
            motion_embeds=motion_tokens,
            joint_mean=global_mean,
            joint_std=global_std,
        ).frames[0]
    
    t_end = time.time()
    print(f"[MTVCRAFTER] Generation finished in {t_end - t_start:.1f}s!", flush=True)

    # 1. Save Clean Film MP4 (pure generated character)
    clean_save_path = "/workspace/out/test_07_mtvcrafter_4dmot.mp4"
    clean_frames = [np.array(img) for img in output_images]
    imageio.mimsave(clean_save_path, clean_frames, fps=20)
    print(f"[MTVCRAFTER] Clean video saved: {clean_save_path} ({os.path.getsize(clean_save_path)} bytes)", flush=True)

    # 2. Save Side-by-Side Comparison MP4 (Ref | Driven | 3D Pose Before | 3D Pose Recon | Output)
    comp_save_path = "/workspace/out/test_07_mtvcrafter_comparison.mp4"
    vis_images = []
    for k in range(len(pose_images_before)):
        vis_image = [
            to_pil(((ref_images[k] + 1) * 127.5).clamp(0, 255).to(torch.uint8)),
            to_pil(((input_images[k] + 1) * 127.5).clamp(0, 255).to(torch.uint8)),
            pose_images_before[k],
            pose_images_after[k],
            output_images[k]
        ]
        vis_image = concat_images_grid(vis_image, cols=len(vis_image), pad=2)
        vis_images.append(vis_image)
    imageio.mimsave(comp_save_path, vis_images, fps=20)
    print(f"[MTVCRAFTER] Comparison video saved: {comp_save_path} ({os.path.getsize(comp_save_path)} bytes)", flush=True)

    # 3. Save Verification Stills
    cv2.imwrite("/workspace/out/mtvcrafter_frame_00.jpg", cv2.cvtColor(clean_frames[0], cv2.COLOR_RGB2BGR))
    cv2.imwrite("/workspace/out/mtvcrafter_frame_24.jpg", cv2.cvtColor(clean_frames[24], cv2.COLOR_RGB2BGR))
    cv2.imwrite("/workspace/out/mtvcrafter_frame_48.jpg", cv2.cvtColor(clean_frames[48], cv2.COLOR_RGB2BGR))

    vid_size = os.path.getsize(clean_save_path)
    print(f"SUCCESS_DONE: Video generated successfully ({vid_size} bytes) at {clean_save_path}", flush=True)

if __name__ == '__main__':
    main()
EOF

python3 /workspace/MTVCrafter/run_cindy_mtvcrafter.py >> /workspace/out/run.log 2>&1
st "complete" "ALL STAGES FINISHED"
"""

def deploy_and_run():
    pod_id = None
    rate = 0.35
    start_time = time.time()

    # Prioritize 24 GB+ Ada / Ampere GPUs for 7B DiT
    gpu_ladder = [
        ("NVIDIA GeForce RTX 4090", 0.44),
        ("NVIDIA GeForce RTX 3090", 0.22),
        ("NVIDIA A40", 0.35),
        ("NVIDIA RTX A6000", 0.33),
        ("NVIDIA RTX A5000", 0.27),
        ("NVIDIA RTX 4000 Ada Generation", 0.29),
        ("NVIDIA RTX A4500", 0.19),
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
        print("\n[الخطوة 1/4] فحص وتخصيص كارت مناسب لـ MTVCrafter (4D Motion Tokens) على السحابة...", flush=True)
        for gpu_id, price in gpu_ladder:
            print(f" -> محاولة حجز: {gpu_id} (~${price}/hr)...", flush=True)
            for cloud in ("SECURE", "COMMUNITY"):
                try:
                    payload = {
                        "gpuCount": 1,
                        "gpuTypeId": gpu_id,
                        "cloudType": cloud,
                        "name": "cindy-mtvcrafter-test",
                        "imageName": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                        "containerDiskInGb": 50,
                        "volumeInGb": 0,
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
                except Exception as e:
                    print(f"    -> [غير متاح] {cloud}: {e}", flush=True)
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

        print("[الخطوة 3/4] متابعة التنفيذ وتوليد الفيديو بخاصية 4D Motion Tokens...", flush=True)
        seen_lines = 0
        success = False
        error_detected = False

        # Max watchdog: 480 seconds (8 minutes)
        for tick in range(96):
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

            if error_detected and tick > 40:
                print("\n [خطأ] تم رصد خطأ أثناء التنفيذ، إنهاء لتوفير الرصيد.", flush=True)
                break

        if not success:
            raise RuntimeError("MTVCrafter inference failed or timed out.")

        print("\n[الخطوة 4/4] تحميل الفيديو واللقطات التمثيلية وحفظها محلياً...", flush=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Download Clean Video
        vid_url = f"{proxy_url}/test_07_mtvcrafter_4dmot.mp4"
        r_vid = requests.get(vid_url, timeout=45)
        with open(LOCAL_OUTPUT_PATH, "wb") as f_out:
            f_out.write(r_vid.content)
        vid_size = os.path.getsize(LOCAL_OUTPUT_PATH)
        print(f" [تم التحميل] الفيديو النقي: {LOCAL_OUTPUT_PATH} ({vid_size:,} bytes)", flush=True)

        # Download Comparison Video
        comp_url = f"{proxy_url}/test_07_mtvcrafter_comparison.mp4"
        try:
            r_comp = requests.get(comp_url, timeout=45)
            with open(LOCAL_COMP_PATH, "wb") as f_comp:
                f_comp.write(r_comp.content)
            print(f" [تم التحميل] فيديو المقارنة: {LOCAL_COMP_PATH} ({os.path.getsize(LOCAL_COMP_PATH):,} bytes)", flush=True)
        except Exception as e_c:
            print(f" [تنبيه] تعذر تحميل فيديو المقارنة: {e_c}", flush=True)

        # Download Stills
        for still_name in ["mtvcrafter_frame_00.jpg", "mtvcrafter_frame_24.jpg", "mtvcrafter_frame_48.jpg"]:
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
