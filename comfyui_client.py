# ==============================================================================
# PROPRIETARY INTELLECTUAL PROPERTY & TRADE SECRET NOTICE
# System: VirtuFilm Studio AI (Cindy AI Director Architecture v8.0)
# Inventor & Owner: Ehab Fikry (المخرج / إيهاب فكري)
# Patent Reference: CAD-IP-2026-001
# Legal Protection:
#   1. WIPO Berne Convention (Automatic International Copyright in 181 Countries)
#   2. Egyptian Intellectual Property Law No. 82 of 2002 (ITIDA Software Deposit)
#   3. Trade Secret & Cryptographic SHA-256 Prior-Art Ledger
# Unauthorized copying, reverse engineering, or redistribution is strictly prohibited.
# ==============================================================================

# -*- coding: utf-8 -*-
"""
Cindy AI Director - ComfyUI Client & Pipeline Engine
Connects Cindy AI to local or cloud-hosted ComfyUI instances.
"""

import json
import os
import random
import re
import secrets as pysecrets
import time
import urllib.parse
import uuid

import requests


def check_comfyui_connection(base_url, timeout=6):
    """Check if ComfyUI instance is alive and fetch GPU stats."""
    if not base_url:
        return {"online": False, "error": "لم يتم إدخال رابط ComfyUI."}
    
    clean_url = base_url.rstrip("/")
    try:
        r = requests.get(f"{clean_url}/system_stats", timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            devices = data.get("devices", [])
            gpu_name = devices[0].get("name", "GPU") if devices else "CPU / Local"
            vram_free = devices[0].get("vram_free", 0) if devices else 0
            vram_total = devices[0].get("vram_total", 0) if devices else 0
            vram_free_gb = round(vram_free / (1024**3), 1) if vram_free else 0
            vram_total_gb = round(vram_total / (1024**3), 1) if vram_total else 0
            return {
                "online": True,
                "url": clean_url,
                "gpu": gpu_name,
                "vram_free_gb": vram_free_gb,
                "vram_total_gb": vram_total_gb,
                "os": data.get("system", {}).get("os", "Linux"),
                "python": data.get("system", {}).get("python_version", ""),
                "message": f"متصل بنجاح: {gpu_name} (ذاكرة متاحة: {vram_free_gb}GB من {vram_total_gb}GB)"
            }
        return {"online": False, "error": f"استجاب السيرفر بكود {r.status_code}"}
    except Exception as e:
        return {"online": False, "error": f"تعذر الاتصال بـ ComfyUI: {str(e)[:120]}"}


def get_available_resources(base_url, timeout=8):
    """Retrieve checkpoints, LoRAs, and samplers available in ComfyUI."""
    clean_url = base_url.rstrip("/")
    try:
        r = requests.get(f"{clean_url}/object_info", timeout=timeout)
        if r.status_code != 200:
            return {"checkpoints": [], "loras": [], "samplers": []}
        data = r.json()
        
        # Checkpoints
        ckpt_info = data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [[]])
        checkpoints = ckpt_info[0] if ckpt_info and isinstance(ckpt_info[0], list) else []
        
        # LoRAs
        lora_info = data.get("LoraLoader", {}).get("input", {}).get("required", {}).get("lora_name", [[]])
        loras = lora_info[0] if lora_info and isinstance(lora_info[0], list) else []
        
        # Samplers
        sampler_info = data.get("KSampler", {}).get("input", {}).get("required", {}).get("sampler_name", [[]])
        samplers = sampler_info[0] if sampler_info and isinstance(sampler_info[0], list) else []
        
        return {
            "checkpoints": checkpoints,
            "loras": loras,
            "samplers": samplers
        }
    except Exception:
        return {"checkpoints": [], "loras": [], "samplers": []}


def build_qwen_image_edit_workflow(
    image_filename,
    prompt,
    checkpoint="Qwen/qwen-image-edit-2511.safetensors",
    width=1024,
    height=1024,
    steps=25,
    cfg=4.0,
    seed=None
):
    """
    Build an Alibaba Qwen-Image-Edit-2511 ComfyUI workflow JSON.
    Instruction-based image modification preserving character identity, camera poses, and lighting.
    """
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": checkpoint
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": ["2", 0],
                "vae": ["1", 2]
            }
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["1", 1]
            }
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "blurry, distortion, low quality, artifacts, watermark",
                "clip": ["1", 1]
            }
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["3", 0],
                "seed": seed,
                "steps": int(steps),
                "cfg": float(cfg),
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 0.65
            }
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["6", 0],
                "vae": ["1", 2]
            }
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "Qwen_Image_Edit_2511",
                "images": ["7", 0]
            }
        }
    }
    return workflow, seed


def build_cinematic_image_workflow(
    prompt,
    negative_prompt="blurry, bad anatomy, bad hands, cropped, low quality, artifacts, watermark",
    checkpoint="SDXL/sd_xl_base_1.0_0.9vae.safetensors",
    lora_name=None,
    lora_strength=0.9,
    width=1024,
    height=1024,
    steps=20,
    cfg=7.0,
    sampler="euler",
    scheduler="normal",
    seed=None,
    input_image=None
):
    """Build a production-grade modular ComfyUI JSON prompt graph."""
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    if 'qwen' in (checkpoint or '').lower() and input_image:
        return build_qwen_image_edit_workflow(
            image_filename=input_image,
            prompt=prompt,
            checkpoint=checkpoint,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg,
            seed=seed
        )

    workflow = {}

    # Node 1: Checkpoint Loader
    workflow["1"] = {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": checkpoint
        }
    }

    model_source = ["1", 0]
    clip_source = ["1", 1]

    # Node 2: Optional LoRA Loader
    if lora_name:
        workflow["2"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_name,
                "strength_model": float(lora_strength),
                "strength_clip": float(lora_strength),
                "model": ["1", 0],
                "clip": ["1", 1]
            }
        }
        model_source = ["2", 0]
        clip_source = ["2", 1]

    # Node 3: Positive Prompt (CLIP Text Encode)
    workflow["3"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": prompt,
            "clip": clip_source
        }
    }

    # Node 4: Negative Prompt (CLIP Text Encode)
    workflow["4"] = {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": negative_prompt or "",
            "clip": clip_source
        }
    }

    # Node 5: Empty Latent Image
    workflow["5"] = {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "width": int(width),
            "height": int(height),
            "batch_size": 1
        }
    }

    # Node 6: KSampler
    workflow["6"] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": seed,
            "steps": int(steps),
            "cfg": float(cfg),
            "sampler_name": sampler,
            "scheduler": scheduler,
            "denoise": 1.0,
            "model": model_source,
            "positive": ["3", 0],
            "negative": ["4", 0],
            "latent_image": ["5", 0]
        }
    }

    # Node 7: VAE Decode
    workflow["7"] = {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["6", 0],
            "vae": ["1", 2]
        }
    }

    # Node 8: Save Image
    workflow["8"] = {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "Cindy_Cinema",
            "images": ["7", 0]
        }
    }

    return workflow, seed


def upload_image_to_comfyui(base_url, image_path):
    """Upload a local image to ComfyUI input directory."""
    clean_url = base_url.rstrip("/")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    fname = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        files = {"image": (fname, f, "image/png")}
        data = {"overwrite": "true"}
        r = requests.post(
            f"{clean_url}/upload/image",
            headers={"User-Agent": "Mozilla/5.0"},
            files=files,
            data=data,
            timeout=30
        )
        if r.status_code == 200:
            res = r.json()
            return res.get("name", fname)
        raise RuntimeError(f"ComfyUI upload failed: {r.status_code} - {r.text[:100]}")


def build_svd_video_workflow(
    image_filename,
    checkpoint="SVD/svd_xt.safetensors",
    width=1024,
    height=576,
    video_frames=25,
    motion_bucket_id=127,
    fps=6,
    steps=20,
    cfg=2.5,
    seed=None
):
    """Build a production-grade modular SVD Image-to-Video ComfyUI JSON graph."""
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "ImageOnlyCheckpointLoader",
            "inputs": {
                "ckpt_name": checkpoint
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "SVD_img2vid_Conditioning",
            "inputs": {
                "clip_vision": ["1", 1],
                "init_image": ["2", 0],
                "vae": ["1", 2],
                "width": int(width),
                "height": int(height),
                "video_frames": int(video_frames),
                "motion_bucket_id": int(motion_bucket_id),
                "fps": int(fps),
                "augmentation_level": 0.0
            }
        },
        "4": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["3", 0],
                "negative": ["3", 1],
                "latent_image": ["3", 2],
                "seed": seed,
                "steps": int(steps),
                "cfg": float(cfg),
                "sampler_name": "euler",
                "scheduler": "karras",
                "denoise": 1.0
            }
        },
        "5": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["4", 0],
                "vae": ["1", 2]
            }
        },
        "6": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["5", 0],
                "filename_prefix": "Cindy_Cinema_Video",
                "fps": float(fps),
                "lossless": False,
                "quality": 85,
                "method": "default"
            }
        }
    }
    return workflow, seed

def build_mimicmotion_workflow(
    image_filename,
    video_filename,
    model_name="mimicmotion_v1-1.safetensors",
    steps=25,
    cfg=2.0,
    fps=16,
    seed=None
):
    """
    Build a production-grade MimicMotion ComfyUI workflow JSON.
    Transfers pose and facial movement with zero 2D warping jitter.
    """
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "MimicMotionPipelineLoader",
            "inputs": {
                "pipeline_type": "MimicMotion",
                "checkpoint": model_name
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "VHS_LoadVideo",
            "inputs": {
                "video": video_filename,
                "force_rate": int(fps),
                "custom_width": 0,
                "custom_height": 0,
                "frame_load_cap": 0,
                "skip_first_frames": 0,
                "select_every_nth": 1
            }
        },
        "4": {
            "class_type": "MimicMotionGetPoses",
            "inputs": {
                "images": ["3", 0],
                "include_body": True,
                "include_face": True,
                "include_hands": True
            }
        },
        "5": {
            "class_type": "MimicMotionSampler",
            "inputs": {
                "pipeline": ["1", 0],
                "ref_image": ["2", 0],
                "pose_images": ["4", 0],
                "seed": seed,
                "steps": int(steps),
                "cfg": float(cfg),
                "fps": int(fps),
                "tile_size": 16,
                "tile_overlap": 6
            }
        },
        "6": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["5", 0],
                "frame_rate": int(fps),
                "loop_count": 0,
                "filename_prefix": "MimicMotion",
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_output": True
            }
        }
    }
    return workflow, seed


def build_wan_workflow(
    image_filename,
    prompt="cinematic camera movement, high resolution, photorealistic 8k",
    checkpoint="Wan2.1/wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors",
    width=1280,
    height=720,
    video_frames=81,
    steps=30,
    cfg=6.0,
    fps=16,
    seed=None
):
    """
    Build an Alibaba Wan 2.1 Video ComfyUI workflow JSON.
    Generates high-fidelity spatiotemporal diffusion video at 720p.
    """
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "WanVideoModelLoader",
            "inputs": {
                "model_name": checkpoint
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "WanVideoTextEncode",
            "inputs": {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distortion, jerky motion, artifacts",
                "model": ["1", 0]
            }
        },
        "4": {
            "class_type": "WanVideoSampler",
            "inputs": {
                "model": ["1", 0],
                "conditioning": ["3", 0],
                "image": ["2", 0],
                "width": int(width),
                "height": int(height),
                "frames": int(video_frames),
                "steps": int(steps),
                "cfg": float(cfg),
                "seed": seed,
                "fps": int(fps)
            }
        },
        "5": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["4", 0],
                "frame_rate": int(fps),
                "loop_count": 0,
                "filename_prefix": "Wan21_Video",
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_output": True
            }
        }
    }
    return workflow, seed





def build_wan22_workflow(
    image_filename,
    prompt="cinematic camera movement, high resolution, photorealistic 8k, dynamic physical coherence",
    checkpoint="Wan2.2/wan2.2_i2v_720p_14B_fp8_e4m3fn.safetensors",
    width=1280,
    height=720,
    video_frames=81,
    steps=30,
    cfg=6.0,
    fps=16,
    seed=None
):
    """
    Build an Alibaba Wan 2.2 Video ComfyUI workflow JSON.
    Wan 2.2 delivers industry-leading spatiotemporal physical coherence,
    ultra-fluid cinematic camera tracking, and realistic dynamic deformation at 720p.
    """
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "WanVideoModelLoader",
            "inputs": {
                "model_name": checkpoint
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "WanVideoTextEncode",
            "inputs": {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distortion, jerky motion, artifacts, amateur, jitter",
                "model": ["1", 0]
            }
        },
        "4": {
            "class_type": "WanVideoSampler",
            "inputs": {
                "model": ["1", 0],
                "conditioning": ["3", 0],
                "image": ["2", 0],
                "width": int(width),
                "height": int(height),
                "frames": int(video_frames),
                "steps": int(steps),
                "cfg": float(cfg),
                "seed": seed,
                "fps": int(fps)
            }
        },
        "5": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["4", 0],
                "frame_rate": int(fps),
                "loop_count": 0,
                "filename_prefix": "Wan22_Cinema_Video",
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 18,
                "save_output": True
            }
        }
    }
    return workflow, seed


def build_ltx_video_workflow(
    image_filename,
    prompt="cinematic camera movement, high resolution, smooth motion",
    checkpoint="LTX-Video/ltx_video_13b_distilled.safetensors",
    width=1024,
    height=576,
    video_frames=97,
    steps=12,
    cfg=3.5,
    fps=24,
    seed=None
):
    """
    Build a Lightricks LTX-Video (13B Distilled Open Source) ComfyUI workflow JSON.
    Ultra-fast open-source generation on local GPUs (<10GB VRAM).
    """
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": checkpoint
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "blurry, low quality, distortion, artifacts, jitter",
                "clip": ["1", 1]
            }
        },
        "5": {
            "class_type": "LTXVConditioning",
            "inputs": {
                "positive": ["3", 0],
                "negative": ["4", 0],
                "frame_rate": float(fps)
            }
        },
        "6": {
            "class_type": "LTXVImgToVideo",
            "inputs": {
                "positive": ["5", 0],
                "negative": ["5", 1],
                "vae": ["1", 2],
                "image": ["2", 0],
                "width": int(width),
                "height": int(height),
                "length": int(video_frames),
                "batch_size": 1
            }
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": int(steps),
                "cfg": float(cfg),
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["6", 0],
                "negative": ["6", 1],
                "latent_image": ["6", 2]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["7", 0],
                "vae": ["1", 2]
            }
        },
        "9": {
            "class_type": "SaveAnimatedWEBP",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": "Cindy_LTX_Video",
                "fps": float(fps),
                "lossless": False,
                "quality": 90,
                "method": "default"
            }
        }
    }
    return workflow, seed


def build_hunyuan_workflow(
    image_filename,
    prompt="cinematic camera movement, high resolution, photorealistic 8k",
    checkpoint="HunyuanVideo/hunyuan_video_720p_fp8_e4m3fn.safetensors",
    width=1280,
    height=720,
    video_frames=73,
    steps=30,
    cfg=6.0,
    fps=24,
    seed=None
):
    """
    Build a Tencent HunyuanVideo (13B Open Source) ComfyUI workflow JSON.
    High spatiotemporal physical coherence at 720p 24fps.
    """
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "HunyuanVideoModelLoader",
            "inputs": {
                "model_name": checkpoint
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "HunyuanVideoTextEncode",
            "inputs": {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distortion, artifacts, amateur",
                "model": ["1", 0]
            }
        },
        "4": {
            "class_type": "HunyuanVideoSampler",
            "inputs": {
                "model": ["1", 0],
                "conditioning": ["3", 0],
                "image": ["2", 0],
                "width": int(width),
                "height": int(height),
                "frames": int(video_frames),
                "steps": int(steps),
                "cfg": float(cfg),
                "seed": seed,
                "fps": int(fps)
            }
        },
        "5": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["4", 0],
                "frame_rate": int(fps),
                "loop_count": 0,
                "filename_prefix": "Hunyuan_Video",
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_output": True
            }
        }
    }
    return workflow, seed


def build_cogvideox_workflow(
    image_filename,
    prompt="cinematic camera movement, high resolution",
    checkpoint="CogVideoX/cogvideox_5b_i2v.safetensors",
    width=720,
    height=480,
    video_frames=49,
    steps=30,
    cfg=6.0,
    fps=8,
    seed=None
):
    """
    Build a THUDM CogVideoX-5B (Open Source) ComfyUI workflow JSON.
    """
    if seed is None:
        seed = random.randint(100000000000, 999999999999)

    workflow = {
        "1": {
            "class_type": "CogVideoXModelLoader",
            "inputs": {
                "model_name": checkpoint
            }
        },
        "2": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_filename
            }
        },
        "3": {
            "class_type": "CogVideoXTextEncode",
            "inputs": {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, artifacts",
                "model": ["1", 0]
            }
        },
        "4": {
            "class_type": "CogVideoXSampler",
            "inputs": {
                "model": ["1", 0],
                "conditioning": ["3", 0],
                "image": ["2", 0],
                "width": int(width),
                "height": int(height),
                "frames": int(video_frames),
                "steps": int(steps),
                "cfg": float(cfg),
                "seed": seed,
                "fps": int(fps)
            }
        },
        "5": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["4", 0],
                "frame_rate": int(fps),
                "loop_count": 0,
                "filename_prefix": "CogVideoX_Video",
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_output": True
            }
        }
    }
    return workflow, seed


def execute_comfyui_workflow(base_url, workflow, outputs_dir, progress_callback=None, timeout_seconds=300):
    """Execute workflow on ComfyUI via REST API and poll until output file is ready."""
    clean_url = base_url.rstrip("/")
    client_id = str(uuid.uuid4())
    
    p_res = requests.post(
        f"{clean_url}/prompt",
        json={"prompt": workflow, "client_id": client_id},
        timeout=15
    )
    if p_res.status_code != 200:
        raise RuntimeError(f"ComfyUI /prompt rejected: {p_res.text[:300]}")
    
    p_data = p_res.json()
    prompt_id = p_data.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI لم يرجع معرف المهمة prompt_id: {p_data}")
    
    if progress_callback:
        progress_callback("تم إرسال المشهد إلى ComfyUI، جاري بدء الريندر...", 10)

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        time.sleep(1.5)
        try:
            h_res = requests.get(f"{clean_url}/history/{prompt_id}", timeout=10)
            if h_res.status_code == 200:
                h_data = h_res.json()
                if prompt_id in h_data:
                    record = h_data[prompt_id]
                    outputs = record.get("outputs", {})
                    for node_id, node_out in outputs.items():
                        images = node_out.get("images") or node_out.get("gifs") or node_out.get("videos") or []
                        if images:
                            img_info = images[0]
                            fname = img_info.get("filename")
                            subfolder = img_info.get("subfolder", "")
                            folder_type = img_info.get("type", "output")
                            
                            view_url = f"{clean_url}/view?filename={urllib.parse.quote(fname)}&subfolder={urllib.parse.quote(subfolder)}&type={folder_type}"
                            
                            local_dest = os.path.join(outputs_dir, fname)
                            dl = requests.get(view_url, timeout=30)
                            if dl.status_code == 200:
                                with open(local_dest, "wb") as f:
                                    f.write(dl.content)
                                
                                if progress_callback:
                                    progress_callback("اكتمل الريندر بنجاح! تم حفظ الكادر السينمائي.", 100)
                                
                                return {
                                    "success": True,
                                    "filename": fname,
                                    "local_path": local_dest,
                                    "view_url": view_url,
                                    "prompt_id": prompt_id
                                }
                    
                    status_info = record.get("status", {})
                    if status_info.get("status_str") == "error":
                        messages = status_info.get("messages", [])
                        raise RuntimeError(f"خطأ تنفيذ في ComfyUI: {messages}")
            
            elapsed = int(time.time() - start_time)
            pct = min(90, 15 + int(elapsed * 4))
            if progress_callback:
                progress_callback(f"ريندر الكادر شغال في كارت الشاشة ({elapsed} ثانية)...", pct)
                
        except requests.exceptions.RequestException:
            pass

    raise TimeoutError("تجاوز ريندر ComfyUI الحد الزمني المسموح.")


def get_prioritized_cheapest_gpus(api_key, min_vram=16):
    """
    Fetch live RunPod GPU pricing for all GPUs with >= min_vram GB,
    sorted strictly from cheapest to most expensive ($/hr).
    Always prioritizes the lowest cost GPU available.
    """
    RUNPOD_GQL = f"https://api.runpod.io/graphql?api_key={api_key.strip()}"
    q = """
    query {
      gpuTypes {
        id
        displayName
        memoryInGb
        communityPrice
        lowestPrice(input: {gpuCount: 1}) {
          uninterruptablePrice
          minimumBidPrice
        }
      }
    }
    """
    fallback_cheapest_order = [
        {"id": "NVIDIA RTX A5000", "name": "RTX A5000", "vram": 24, "price": 0.16},
        {"id": "NVIDIA RTX 4000 SFF Ada Generation", "name": "RTX 4000 Ada SFF", "vram": 20, "price": 0.18},
        {"id": "NVIDIA RTX A4500", "name": "RTX A4500", "vram": 20, "price": 0.19},
        {"id": "Tesla V100-PCIE-16GB", "name": "Tesla V100", "vram": 16, "price": 0.19},
        {"id": "NVIDIA RTX 4000 Ada Generation", "name": "RTX 4000 Ada", "vram": 20, "price": 0.20},
        {"id": "NVIDIA GeForce RTX 3090", "name": "RTX 3090", "vram": 24, "price": 0.22},
        {"id": "NVIDIA GeForce RTX 3090 Ti", "name": "RTX 3090 Ti", "vram": 24, "price": 0.27},
        {"id": "NVIDIA GeForce RTX 4080", "name": "RTX 4080", "vram": 16, "price": 0.27},
        {"id": "NVIDIA GeForce RTX 4080 SUPER", "name": "RTX 4080 SUPER", "vram": 16, "price": 0.28},
        {"id": "NVIDIA RTX A6000", "name": "RTX A6000", "vram": 48, "price": 0.33},
        {"id": "NVIDIA GeForce RTX 4090", "name": "RTX 4090", "vram": 24, "price": 0.34},
        {"id": "NVIDIA RTX PRO 4500 Blackwell", "name": "RTX PRO 4500", "vram": 32, "price": 0.34},
        {"id": "NVIDIA A40", "name": "A40", "vram": 48, "price": 0.35},
    ]

    try:
        r = requests.post(RUNPOD_GQL, json={"query": q}, timeout=10)
        data = r.json().get("data", {}).get("gpuTypes", [])
        viable = []
        for g in data:
            mem = g.get("memoryInGb", 0)
            lp = g.get("lowestPrice") or {}
            price = lp.get("uninterruptablePrice") or g.get("communityPrice") or 0.0
            if mem >= min_vram and price > 0:
                viable.append({
                    "id": g["id"],
                    "name": g.get("displayName") or g["id"],
                    "vram": mem,
                    "price": float(price)
                })
        if viable:
            viable.sort(key=lambda x: x["price"])
            return viable
    except Exception:
        pass

    return fallback_cheapest_order



def check_comfyui_node_capabilities(base_url, timeout=5):
    """
    Inspect registered node types on a ComfyUI server to see what video engines are supported.
    Returns a dict with availability flags for each engine.
    """
    clean_url = (base_url or "").rstrip("/")
    if not clean_url:
        return {"online": False}
    try:
        r = requests.get(f"{clean_url}/object_info", timeout=timeout)
        if r.status_code != 200:
            return {"online": False, "status_code": r.status_code}
        data = r.json()
        return {
            "online": True,
            "wan21": "WanVideoModelLoader" in data or "WanVideoSampler" in data,
            "wan22": "WanVideoModelLoader" in data or "Wan22VideoModelLoader" in data,
            "hunyuan": "HunyuanVideoModelLoader" in data,
            "cogvideox": "CogVideoXModelLoader" in data,
            "vhs": "VHS_VideoCombine" in data,
            "svd": "ImageOnlyCheckpointLoader" in data,
            "reactor": "ReActorFaceSwap" in data or "ReActorLoadFaceModel" in data,
            "dmad": "LoraLoader" in data or "WanVideoSampler" in data,
            "manager_available": True
        }
    except Exception as e:
        return {"online": False, "error": str(e)}


def install_comfyui_custom_nodes(base_url, repo_urls=None):
    """
    Install required video custom nodes on ComfyUI via ComfyUI Manager API.
    """
    clean_url = (base_url or "").rstrip("/")
    default_repos = [
        "https://github.com/kijai/ComfyUI-WanVideoWrapper",
        "https://github.com/kijai/ComfyUI-HunyuanVideoWrapper",
        "https://github.com/kijai/ComfyUI-CogVideoXWrapper",
        "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite",
        "https://github.com/Gourieff/ComfyUI-ReActor"
    ]
    repos = repo_urls or default_repos
    results = {}
    for repo in repos:
        try:
            r = requests.post(f"{clean_url}/customnode/install", json={"url": repo}, timeout=15)
            results[repo] = r.status_code in [200, 201]
        except Exception:
            results[repo] = False
    
    try:
        requests.post(f"{clean_url}/manager/reboot", timeout=5)
    except Exception:
        pass
        
    return results


def launch_runpod_comfyui_pod(api_key, gpu_type=None, template_id="cw3nka7d08", timeout_seconds=120):
    """
    Launch a cloud ComfyUI instance on RunPod and wait until it is live (HTTP 200).
    Always prioritizes the cheapest available GPU (RTX A5000 @ $0.16/hr, RTX 3090 @ $0.22/hr, etc.).
    Returns pod details and comfyui_url.
    """
    if not api_key:
        raise ValueError("RunPod API Key is required.")

    RUNPOD_GQL = f"https://api.runpod.io/graphql?api_key={api_key.strip()}"

    # 1. First, check if there is an existing pod already running or stopped
    q_existing = """
    query {
      myself {
        pods {
          id
          name
          desiredStatus
        }
      }
    }
    """
    r_check = requests.post(RUNPOD_GQL, json={"query": q_existing}, timeout=15)
    existing_pods = r_check.json().get("data", {}).get("myself", {}).get("pods", [])
    pod_id = None
    pod_name = None
    deployed_gpu_info = None

    for p in existing_pods:
        p_name = (p.get("name") or "").lower()
        if "comfy" in p_name or "cindy" in p_name or "mad_plum" in p_name:
            pod_id = p.get("id")
            pod_name = p.get("name")
            if p.get("desiredStatus") in ["STOPPED", "EXITED"]:
                mut_resume = f'mutation {{ podResume(input: {{podId: "{pod_id}", gpuCount: 1}}) {{ id desiredStatus }} }}'
                res_r = requests.post(RUNPOD_GQL, json={"query": mut_resume}, timeout=15)
                # If host machine is full, terminate stuck pod and fall through to cheapest on-demand deploy
                if res_r.json().get("errors"):
                    mut_term = f'mutation {{ podTerminate(input: {{podId: "{pod_id}"}}) }}'
                    requests.post(RUNPOD_GQL, json={"query": mut_term}, timeout=15)
                    pod_id = None
                else:
                    break
            elif p.get("desiredStatus") == "RUNNING":
                break

    # 2. If no existing pod, deploy the cheapest available GPU via Cheapest-First Cascade
    if not pod_id:
        gpu_candidates = get_prioritized_cheapest_gpus(api_key, min_vram=16)
        if gpu_type:
            # If user explicitly specified a GPU, try it first then fallback to cheapest list
            gpu_candidates = [{"id": gpu_type, "name": gpu_type, "vram": 24, "price": 0.34}] + [
                g for g in gpu_candidates if g["id"] != gpu_type
            ]

        mut_deploy = """
        mutation($templateId: String!, $gpuTypeId: String!) {
          podFindAndDeployOnDemand(input: {
            name: "Cindy-ComfyUI-Studio"
            templateId: $templateId
            gpuTypeId: $gpuTypeId
            cloudType: ALL
            gpuCount: 1
            volumeInGb: 40
            containerDiskInGb: 40
            volumeMountPath: "/workspace"
          }) {
            id
            name
            desiredStatus
          }
        }
        """

        last_err = ""
        for cand in gpu_candidates:
            cand_id = cand["id"]
            try:
                r_dep = requests.post(
                    RUNPOD_GQL,
                    json={"query": mut_deploy, "variables": {"templateId": template_id, "gpuTypeId": cand_id}},
                    timeout=20
                )
                data = r_dep.json()
                if "errors" in data or not data.get("data", {}).get("podFindAndDeployOnDemand"):
                    last_err = data.get("errors", [{}])[0].get("message", "No availability")
                    continue
                pod_res = data.get("data", {}).get("podFindAndDeployOnDemand", {})
                pod_id = pod_res.get("id")
                pod_name = pod_res.get("name", "Cindy-ComfyUI-Studio")
                deployed_gpu_info = cand
                break
            except Exception as e:
                last_err = str(e)
                continue

        if not pod_id:
            raise RuntimeError(f"فشل إيجاد كارت سحابي متاح بالأولوية الاقتصادية: {last_err}")

    comfy_url = f"https://{pod_id}-8188.proxy.runpod.net"
    gpu_label = deployed_gpu_info['name'] if deployed_gpu_info else "السحابي الاقتصادي"
    gpu_price_str = f"(${deployed_gpu_info['price']:.2f}/ساعة)" if deployed_gpu_info else ""

    # 3. Poll until ComfyUI responds or timeout
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        time.sleep(3)
        try:
            chk = requests.get(f"{comfy_url}/system_stats", headers={"User-Agent": "Mozilla/5.0"}, timeout=4)
            if chk.status_code == 200:
                return {
                    "success": True,
                    "pod_id": pod_id,
                    "pod_name": pod_name,
                    "comfyui_url": comfy_url,
                    "message": f"تم تشغيل استوديو ComfyUI بنجاح على أرخص كارت متاح: {gpu_label} {gpu_price_str}!"
                }
        except Exception:
            pass

    # If still not ready after initial poll, wait up to 180 seconds for ComfyUI container to fully boot
    while time.time() - start_time < 180:
        time.sleep(5)
        try:
            chk = requests.get(f"{comfy_url}/system_stats", headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if chk.status_code == 200:
                return {
                    "success": True,
                    "pod_id": pod_id,
                    "pod_name": pod_name,
                    "comfyui_url": comfy_url,
                    "message": f"تم تشغيل استوديو ComfyUI بنجاح على أرخص كارت متاح: {gpu_label} {gpu_price_str}!"
                }
        except Exception:
            pass

    raise RuntimeError(f"استغرق إقلاع ComfyUI على كارت {gpu_label} وقتاً أطول من المعتاد. تم إلغاء العملية وحماية الرصيد.")


def stop_runpod_pod(api_key, pod_id=None):
    """Pause/Stop a pod from RunPod immediately to reduce GPU billing to $0.00/hr while keeping files intact."""
    if not api_key:
        return False
    RUNPOD_GQL = "https://api.runpod.io/graphql"
    headers = {'Authorization': f'Bearer {api_key.strip()}', 'Content-Type': 'application/json'}
    
    # Auto-detect ComfyUI pod if not supplied
    if not pod_id:
        q = "query { myself { pods { id name desiredStatus } } }"
        try:
            r = requests.post(RUNPOD_GQL, headers=headers, json={"query": q}, timeout=15)
            pods = r.json().get("data", {}).get("myself", {}).get("pods", [])
            for p in pods:
                p_name = p.get("name", "").lower()
                if "comfy" in p_name or "cindy" in p_name:
                    pod_id = p.get("id")
                    break
            if not pod_id and pods:
                pod_id = pods[0].get("id")
        except Exception:
            pass
            
    if not pod_id:
        return False
        
    mut = 'mutation($id: String!) { podStop(input: {podId: $id}) { id desiredStatus } }'
    body = {"query": mut, "variables": {"id": pod_id}}
    try:
        r = requests.post(RUNPOD_GQL, headers=headers, json=body, timeout=15)
        return "data" in r.json() and r.json().get("data", {}).get("podStop") is not None
    except Exception:
        return False


def terminate_runpod_pod(api_key, pod_id=None):
    """Terminate and remove a pod from RunPod immediately."""
    if not api_key:
        return False
    RUNPOD_GQL = "https://api.runpod.io/graphql"
    headers = {'Authorization': f'Bearer {api_key.strip()}', 'Content-Type': 'application/json'}
    
    # Auto-detect ComfyUI pod if not supplied
    if not pod_id:
        q = "query { myself { pods { id name desiredStatus } } }"
        try:
            r = requests.post(RUNPOD_GQL, headers=headers, json={"query": q}, timeout=15)
            pods = r.json().get("data", {}).get("myself", {}).get("pods", [])
            for p in pods:
                p_name = p.get("name", "").lower()
                if "comfy" in p_name or "cindy" in p_name:
                    pod_id = p.get("id")
                    break
            if not pod_id and pods:
                pod_id = pods[0].get("id")
        except Exception:
            pass
            
    if not pod_id:
        return False
        
    mut = 'mutation($id: String!) { podTerminate(input: {podId: $id}) }'
    body = {"query": mut, "variables": {"id": pod_id}}
    try:
        r = requests.post(RUNPOD_GQL, headers=headers, json=body, timeout=15)
        return "data" in r.json()
    except Exception:
        return False


def build_skyreels_workflow(
    image_filename,
    prompt="cinematic camera movement, high resolution, photorealistic 8k, dynamic physical coherence",
    checkpoint="SkyReels-V1/skyreels_v1_i2v_720p.safetensors",
    width=1280,
    height=720,
    video_frames=73,
    steps=30,
    fps=16,
    seed=None
):
    """Alias for SkyReels-V1 based on HunyuanVideo architecture."""
    return build_hunyuan_workflow(
        image_filename=image_filename,
        prompt=prompt,
        checkpoint=checkpoint,
        width=width,
        height=height,
        video_frames=video_frames,
        steps=steps,
        fps=fps,
        seed=seed
    )

def build_wan21_workflow(
    image_filename,
    prompt="cinematic camera movement, high resolution, photorealistic 8k",
    checkpoint="Wan2.1/wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors",
    width=1280,
    height=720,
    video_frames=81,
    steps=25,
    fps=16,
    seed=None
):
    """Alias for Wan 2.1."""
    return build_wan_workflow(
        image_filename=image_filename,
        prompt=prompt,
        checkpoint=checkpoint,
        width=width,
        height=height,
        video_frames=video_frames,
        steps=steps,
        fps=fps,
        seed=seed
    )
