import cindy_radar
import cindy_storyboard
VIDEO_JOBS = {}
# -*- coding: utf-8 -*-

"""

CINDY AI - 2026 Cutting-Edge Multi-Cloud Execution Server

Direct API Execution:

- Kling 3.0 / 4.0 & 1.5 Pro

- MiniMax H3 / H3 Max

- ByteDance Seedance 2.5

- FLUX 3 Max & FLUX.1 Schnell/Dev/Pro

- Wan 2.7 / Wan 3.0 & 2.1

- Google Veo 3.1 & Google Imagen 3 (Direct API)

- Luma Dream Machine & Ray 2

- MMAudio v2 & Clarity Upscaler

"""



import http.server

import socketserver

import asyncio

import concurrent.futures

import subprocess

import json

import os

import re

import sys

import time

import base64

import threading

import urllib.parse

import requests

import io

import zipfile

import runpod_trainer

from cindy_pricing import build_daily_pricing_report


import comfyui_client

try:

    from PIL import Image

except ImportError:

    Image = None



sys.stdout.reconfigure(encoding='utf-8')



PORT = 8765

HOST = "127.0.0.1"

BASE_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director"

OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

SECRETS_FILE = os.path.join(BASE_DIR, "cindy_secrets.json")

LORAS_FILE = os.path.join(BASE_DIR, "cindy_loras.json")

LORAS_DIR = os.path.join(OUTPUTS_DIR, "loras")

os.makedirs(LORAS_DIR, exist_ok=True)

LORA_TRAINING_JOBS = {}



os.makedirs(OUTPUTS_DIR, exist_ok=True)



def _lock_secrets_acl():

    """Restrict cindy_secrets.json on Windows so only the current user, SYSTEM, and Administrators can read it."""

    if os.name == 'nt' and os.path.exists(SECRETS_FILE):

        user = os.environ.get('USERNAME', '')

        if user:

            try:

                subprocess.run(

                    ['icacls', SECRETS_FILE, '/inheritance:r',

                     '/grant:r', f'{user}:(R,W)', 'SYSTEM:(F)', 'Administrators:(F)'],

                    capture_output=True, timeout=5

                )

            except Exception:

                pass



_lock_secrets_acl()



def get_model_prompt_rules(model_name, mode='video'):
    m = (model_name or '').lower()
    
    # 1. Alibaba Wan 2.1 & Wan 2.2 (Video)
    if 'wan' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR ALIBABA WAN 2.1 / 2.2:\n"
            "- Sequential linear storytelling: 'First..., then..., while the camera... Finally...'\n"
            "- Describe tangible physical interactions, fluid dynamics (rain, smoke, fabric flutter), and material lighting.\n"
            "- Strictly NO quality buzzwords ('8k, masterpiece, photorealistic, cinematic'). Describe real physical details.\n"
            "- State steady camera trajectory (e.g. 'smooth tracking shot following subject at eye level')."
        )
    # 2. Tencent HunyuanVideo (13B Open-Source Video)
    elif 'hunyuan' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR TENCENT HUNYUANVIDEO (13B):\n"
            "- Continuous, cohesive English prose in a single descriptive paragraph.\n"
            "- Describe the subject, action, environment, lighting, and camera behavior as one seamless filmic narrative.\n"
            "- Explicitly specify camera motion: 'cinematic slow push-in', 'locked static shot', or 'smooth tracking'.\n"
            "- Strictly NO brackets, tags, or comma lists. Keep it fluid and vividly filmic."
        )
    # 3. ByteDance Seedance 2.5 (30s Single-Pass Narrative & 50 Multimodal References)
    elif 'seedance' in m or 'bytedance' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR BYTEDANCE SEEDANCE 2.5:\n"
            "- Seedance 2.5 is a 30-second single-pass narrative powerhouse supporting up to 50 multimodal references (30 images, 10 videos, 10 audios) and native synchronized sound.\n"
            "- MULTI-REFERENCE BINDING: Bind references directly using explicit handles:\n"
            "  * Use '@Image1' for protagonist appearance, face, and clothing.\n"
            "  * Use '@Image2' for second character / antagonist / supporting actor.\n"
            "  * Use '@Image3' for location environment, architecture, or lighting aesthetic.\n"
            "  * Use '@Video1' for motion choreography and camera trajectory guidance.\n"
            "- 30-SECOND CONTINUOUS SCENE BLOCKING: Structure the 30-second continuous take into clear sequential beats (Beat 1: Establishing & approach, Beat 2: Dynamic kinetic escalation and dialogue, Beat 3: Climactic resolution), maintaining absolute identity and anatomical consistency.\n"
            "- NATIVE AUDIO & SENSORY DYNAMICS: Describe synchronized sound effects, dialogue rhythm, and environmental acoustics alongside physical movement.\n"
            "- Strictly NO empty quality buzzwords ('8k, masterpiece'); use tangible physical details, explicit entity handles, and cinematic camera trajectory."
        )
    # 4. Google Veo 3.1 Cinematic & Fast (Video)
    elif 'veo' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR GOOGLE VEO 3.1 (Cinematic / Fast):\n"
            "- Hollywood cinematographic grammar: [Shot Type & Framing] + [Lens & Depth of Field] + [Subject & Action] + [Lighting & Color Grade] + [Camera Trajectory].\n"
            "- Use authentic cinema specs: 'Establishing wide shot, 35mm anamorphic lens, f/1.8 shallow depth of field, warm golden hour practical lighting with volumetric haze, slow cinematic dolly-in at 24fps'.\n"
            "- Emphasize temporal transitions and realistic lens flares."
        )
    # 5. Kling AI Suite (1.5 / 1.6 Pro / Motion Control / O1 Edit)
    elif 'kling' in m:
        if 'motion control' in m or 'motion-control' in m:
            return (
                "CRITICAL MODEL PROMPT RULES FOR KLING MOTION CONTROL (1080p):\n"
                "- Motion capture transfer from driving video onto character reference.\n"
                "- Prompt formula: 'Perform precise 1080p motion capture transfer from driving choreography to the character. Preserve exact facial structure, clothing textures, and proportions while perfectly matching the driving video\'s head turns, body gestures, and camera angle trajectory without artifacts.'\n"
                "- Keep character identity locked."
            )
        elif 'o1' in m or 'video-to-video' in m:
            return (
                "CRITICAL MODEL PROMPT RULES FOR KLING O1 VIDEO-TO-VIDEO EDIT:\n"
                "- Video restyling and delta modification.\n"
                "- State the style or environment transformation clearly: 'Transform scene lighting from daytime to dark rainy midnight with vibrant neon reflections. Preserve original character motion, timing, and camera path completely.'\n"
                "- State what to change vs what to preserve."
            )
        else:
            return (
                "CRITICAL MODEL PROMPT RULES FOR KLING AI (v1.5 / v1.6 Pro):\n"
                "- Structured cinematic blocks: [Camera Movement]: ..., [Lighting]: ..., [Subject & Action]: ..., [Atmosphere & Details]: ...\n"
                "- Restrict to ONE single clear camera direction (e.g. slow dolly in, steady pan right). Avoid conflicting multi-moves.\n"
                "- Emphasize facial realism, eye focus, and physical body dynamics."
            )
    # 6. Luma Ray 2 & Dream Machine
    elif 'luma' in m or 'ray' in m:
        if 'modify' in m:
            return (
                "CRITICAL MODEL PROMPT RULES FOR LUMA RAY 2 MODIFY (Video-to-Video):\n"
                "- Video restyling and texture modification.\n"
                "- Prompt: 'Restyle video to [target aesthetic, e.g. 1970s 35mm film grain, warm golden hour tint, cyberpunk neon atmosphere]. Keep original camera movement trajectory and character actions locked while updating textures and lighting.'\n"
            )
        else:
            return (
                "CRITICAL MODEL PROMPT RULES FOR LUMA RAY 2 & DREAM MACHINE:\n"
                "- Luma specializes in 3D spatial camera motion and continuous trajectory.\n"
                "- Use explicit 3D camera vector verbs: 'camera orbits 90 degrees around subject', 'dolly zoom (vertigo effect)', 'crane shot rising from ground level to high angle', 'smooth continuous tracking shot'.\n"
                "- For I2V: Describe how the initial frame evolves smoothly in motion and camera angle without mutating anatomy."
            )
    # 7. MiniMax Hailuo (H3 Lite / H3 Max Turbo)
    elif 'minimax' in m or 'hailuo' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR MINIMAX HAILUO:\n"
            "- Master of human acting, nuanced micro-expressions, facial emotion, breathing, and dramatic beats.\n"
            "- Include sensory tactile details (wind rustling fabric, ambient reflections on skin, subtle gaze shifts).\n"
            "- Strictly zero quality filler words."
        )
    # 8. Runway Gen-3 Alpha (Video)
    elif 'runway' in m or 'gen-3' in m or 'gen3' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR RUNWAY GEN-3 ALPHA:\n"
            "- Structure with bracketed technical tags: [Camera]: ..., [Lighting]: ..., [Subject & Movement]: ...\n"
            "- Specify real lens focal lengths and cinematic setups (e.g. '35mm anamorphic, f/2.0, natural motion blur, continuous lighting, volumetric haze')."
        )
    # 9. Mischief-1 (Fast Kinetic & Action Video)
    elif 'mischief' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR MISCHIEF-1 (Kinetic Action & Physics):\n"
            "- Hyper-velocity physical action, explosive stunts, and dynamic camera choreography.\n"
            "- Describe fast kinetic movement, motion blur, particle effects (smoke, sparks, water splash), and rapid tracking."
        )
    # 10. Qwen-Image-Edit-2511 (Alibaba 20B Instruction Image Editing)
    elif 'qwen' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR ALIBABA QWEN-IMAGE-EDIT-2511:\n"
            "- Instruction-driven semantic and camera editing engine.\n"
            "- Formulate as a direct, clear directorial command: 'Change camera angle to low-angle dramatic profile', 'Change jacket to worn black leather', 'Add wet rain reflections on the ground and skin'.\n"
            "- Crucial: Explicitly state what to preserve ('Preserve facial identity, expression, and core lighting atmosphere').\n"
            "- Bilingual support: Responds accurately to English or Arabic instructions.\n"
            "- Avoid generic quality buzzwords; focus strictly on delta modifications."
        )
    # 11. Ideogram v2 (Image & Typography)
    elif 'ideogram' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR IDEOGRAM V2 (Image & Typography):\n"
            "- Industry standard for typography and embedded graphic text.\n"
            "- When text is required, put the exact text in quotation marks: The text \"EXACT TEXT\" written in [neon script / vintage serif / bold typography].\n"
            "- Describe layout composition, graphic hierarchy, color palette, and art direction style."
        )
    # 12. Recraft v3 (Image & Design)
    elif 'recraft' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR RECRAFT V3:\n"
            "- Specializes in clean architectural, product, vector, and editorial design.\n"
            "- Specify clean material shaders, edge crispness, studio lighting setup (key, fill, rim light), and art direction palette.\n"
            "- Keep lighting crisp and subject proportions exact."
        )
    # 13. Google Nano Banana / Imagen 3 (Image)
    elif 'banana' in m or 'imagen' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR GOOGLE NANO BANANA / IMAGEN 3:\n"
            "- Rich, descriptive natural language describing a complete visual scene.\n"
            "- Detail subject features, atmosphere, color palette, lighting temperature, and medium.\n"
            "- Strictly avoid quality buzzwords ('photorealistic, trending, 8k'); describe realistic textures, lighting reflections, and depth instead."
        )
    # 14. FLUX.1 (Dev / Schnell / Pro Ultra - Image)
    elif 'flux' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR FLUX.1 (Dev / Schnell / Pro Ultra):\n"
            "- Real candid 35mm film photograph: 'A raw 35mm photograph of [subject], shot on Kodak Portra 400, 50mm f/1.4 lens, natural film grain, authentic skin textures, raw cinematic lighting'.\n"
            "- Strictly NO AI tropes like 'masterpiece, trending on artstation, 8k, ultra-detailed'. Describe real tangible visual elements directly."
        )
    # 15. THUDM CogVideoX-5B (Video)
    elif 'cogvideo' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR THUDM COGVIDEOX-5B:\n"
            "- Compact, focused physical action description (within 50-80 words).\n"
            "- Direct subject actions and stable camera trajectory."
        )
    # 16. Stability SVD-XT (Image-to-Video)
    elif 'svd' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR STABILITY SVD-XT (Image-to-Video):\n"
            "- Keep motion subtle and elegant: gentle ambient movement, breathing, wind blowing hair/fabric, subtle camera push-in.\n"
            "- Avoid radical scene transformations that cause warping."
        )
    # 17. Stability SDXL & SD 3.5 Large (Image)
    elif 'sd' in m or 'sdxl' in m or 'stable' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR STABLE DIFFUSION (SDXL / SD 3.5 Large):\n"
            "- Direct descriptive phrasing: Subject + Environment + Lighting setup + Composition style."
        )

    # 19. LatentSync (Lip Sync)
    elif 'latentsync' in m or 'lip' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR LATENTSYNC (Lip Synchronization):\n"
            "- Focus on clear facial framing, natural lip articulation, and frontal lighting."
        )
    # 20. MMAudio (Sound Design & Foley)
    elif 'mmaudio' in m or 'audio' in m or 'sound' in m:
        return (
            "CRITICAL MODEL PROMPT RULES FOR MMAUDIO (Cinematic Sound Design & Foley):\n"
            "- Describe sensory sound layers: Foreground Foley (footsteps, fabric) + Ambient Environmental sound + Acoustic Space (reverberant hall, car interior).\n"
            "- Focus on physical sound effects and atmospheric presence."
        )
    else:
        return f"CRITICAL MODEL PROMPT RULES FOR {model_name}:\n- Tailor phrasing specifically to {model_name}'s standard format and avoid generic quality clutter."

def load_secrets():

    if os.path.exists(SECRETS_FILE):

        try:

            with open(SECRETS_FILE, 'r', encoding='utf-8') as f:

                return json.load(f)

        except Exception as e:

            print("Error reading secrets file:", e)

    return {}



def save_secrets(data):

    try:

        with open(SECRETS_FILE, 'w', encoding='utf-8') as f:

            json.dump(data, f, ensure_ascii=False, indent=2)

        _lock_secrets_acl()

        return True

    except Exception as e:

        print("Error saving secrets file:", e)

        return False



def _redact_secrets(text):

    """Ensure raw API keys never leak in error messages or logs."""

    if not text:

        return ""

    out = str(text)

    try:

        sec = load_secrets()

        for v in sec.values():

            if isinstance(v, str) and len(v) >= 8 and v in out:

                out = out.replace(v, "[REDACTED_KEY]")

    except Exception:

        pass

    out = re.sub(r'([?&]key=)[A-Za-z0-9_\-\.]+', r'\1[REDACTED]', out)

    return out



def _detect_magic_media(raw_bytes, orig_name=''):
    """Inspect binary magic bytes or fallback to verified media extensions."""
    if not raw_bytes or len(raw_bytes) < 4:
        return None, None
    if raw_bytes.startswith(b'\xff\xd8\xff'):
        return 'image', 'jpg'
    if raw_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image', 'png'
    if raw_bytes[:4] == b'RIFF' and len(raw_bytes) >= 12 and raw_bytes[8:12] == b'WEBP':
        return 'image', 'webp'
    if raw_bytes.startswith((b'GIF87a', b'GIF89a')):
        return 'image', 'gif'
    if b'ftyp' in raw_bytes[:64] or b'moov' in raw_bytes[:64]:
        return 'video', 'mp4'
    if raw_bytes.startswith(b'\x1a\x45\xdf\xa3'):
        return 'video', 'webm'
    if raw_bytes[:4] == b'RIFF' and len(raw_bytes) >= 12 and raw_bytes[8:12] == b'WAVE':
        return 'audio', 'wav'
    if raw_bytes.startswith(b'ID3') or (len(raw_bytes) > 2 and raw_bytes[0] == 0xff and (raw_bytes[1] & 0xe0) == 0xe0):
        return 'audio', 'mp3'
    if raw_bytes.startswith(b'OggS'):
        return 'audio', 'ogg'
    if raw_bytes.startswith(b'fLaC'):
        return 'audio', 'flac'
    
    # Safe extension fallback
    ext = (orig_name.rsplit('.', 1)[-1] if '.' in orig_name else '').lower()
    if ext in ('jpg', 'jpeg'):
        return 'image', 'jpg'
    elif ext == 'png':
        return 'image', 'png'
    elif ext == 'webp':
        return 'image', 'webp'
    elif ext in ('mp4', 'm4v', 'mov'):
        return 'video', 'mp4'
    elif ext in ('webm', 'mkv'):
        return 'video', 'webm'
    elif ext in ('wav', 'wave'):
        return 'audio', 'wav'
    elif ext in ('mp3', 'm4a', 'aac', 'ogg', 'flac'):
        return 'audio', ext
    return None, None

def _safe_output_path(filename):

    """Resolve a filename strictly inside OUTPUTS_DIR, blocking any path traversal or illegal characters."""

    if not filename:

        return None

    base = os.path.basename(str(filename).split('?')[0].split('#')[0])

    if not re.match(r'^[A-Za-z0-9._\-]+$', base) or '..' in base:

        return None

    full = os.path.realpath(os.path.join(OUTPUTS_DIR, base))

    out_root = os.path.realpath(OUTPUTS_DIR)

    if not full.startswith(out_root + os.sep):

        return None

    return full

def load_loras():

    if not os.path.exists(LORAS_FILE):

        return []

    try:

        with open(LORAS_FILE, 'r', encoding='utf-8') as f:

            return json.load(f)

    except Exception:

        return []



def save_loras(loras_list):

    try:

        with open(LORAS_FILE, 'w', encoding='utf-8') as f:

            json.dump(loras_list, f, ensure_ascii=False, indent=2)

        return True

    except Exception:

        return False





def _upload_lora_to_fal(local_filepath):

    secrets = load_secrets()

    fal_key = secrets.get('fal_api_key', '')

    if not fal_key or not os.path.exists(local_filepath):

        return None

    try:

        fname = os.path.basename(local_filepath)

        init_headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json", "Accept": "application/json"}

        init_res = requests.post(

            "https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",

            headers=init_headers,

            json={"file_name": fname, "content_type": "application/octet-stream"},

            timeout=25

        )

        if init_res.status_code == 200:

            init_data = init_res.json()

            up_url = init_data.get('upload_url')

            file_url = init_data.get('file_url')

            with open(local_filepath, "rb") as fh:

                put_res = requests.put(up_url, data=fh, headers={"Content-Type": "application/octet-stream"}, timeout=300)

            if put_res.status_code in (200, 201):

                return file_url

    except Exception as e:

        print(f"[LoRA Fal CDN Upload Error] {e}")

    return None



def _register_trained_lora(job):

    loras = load_loras()

    new_entry = {

        "id": job["id"],

        "name": job["model_name"],

        "trigger_word": job["trigger_word"],

        "type": "style" if job.get("is_style") else "character",

        "weights_url": job.get("weights_url"),

        "local_file": job.get("local_file"),

        "file_size": job.get("file_size", 0),

        "steps": job.get("steps", 1000),

        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),

        "engine": job.get("engine", "runpod"),

        "description": f"Model {job['model_name']} trained via RunPod GPU ({job.get('gpu_display', 'RTX 4090')})"

    }

    loras.insert(0, new_entry)

    save_loras(loras)



def _safe_lora_path(filename):

    if not filename: return None

    base = os.path.basename(str(filename).split('?')[0].split('#')[0])

    if not re.match(r'^[A-Za-z0-9._\-]+$', base) or '..' in base:

        return None

    full = os.path.realpath(os.path.join(LORAS_DIR, base))

    loras_root = os.path.realpath(LORAS_DIR)

    if not full.startswith(loras_root + os.sep):

        return None

    return full





def mask_token(token):

    if not token or len(token) < 8:

        return "غير مضاف"

    return token[:6] + "..." + token[-4:]



def _cross_lingual_cinematic_transmute(text, mode='image'):
    """
    Cross-Lingual Cinematographic Semantic Transmutation Engine (CCSTE).
    Transmutes directorial prompts in Arabic, French, and Spanish into
    production-calibrated cinematic English prompts with lens, lighting,
    and motion specifications for FLUX, Wan, and Kling.
    """
    if not text:
        return text

    lexicon = {
        # Arabic Cinema Terms
        'كلب جولدن': 'golden retriever puppy', 'جولدن': 'golden retriever', 'كلب': 'dog',
        'صغير': 'puppy' if ('كلب' in text or 'جرو' in text) else 'small', 'جرو': 'puppy',
        'قطة': 'cat', 'قط': 'cat', 'قط صغير': 'kitten',
        'يجري': 'running playfully', 'يركض': 'sprinting with joyful energy', 'يمشي': 'walking gracefully',
        'حديقة': 'lush green garden', 'حديقه': 'lush green garden', 'مشمسة': 'sun-drenched with golden rays',
        'مشمس': 'sunlit', 'شمس': 'sunlight',
        'سيارة': 'sleek sports car', 'عربية': 'car', 'كلاسيكية': 'vintage classic', 'حمراء': 'deep crimson red',
        'شارع': 'urban street', 'شوارع': 'cinematic streets', 'ليل': 'nighttime with atmospheric neon reflections',
        'ليلا': 'at night with volumetric lights', 'ليلاً': 'at night with atmospheric neon glow',
        'فتاة': 'graceful young woman', 'بنت': 'young woman', 'رجل': 'distinguished man', 'شاب': 'young man',
        'طفل': 'young child', 'فستان': 'elegant dress', 'أزرق': 'sapphire blue',
        'بحر': 'serene turquoise ocean', 'شاطئ': 'golden sand beach', 'غروب': 'golden hour sunset',
        'شروق': 'sunrise with warm dawn mist', 'غابة': 'ancient mystical forest with tall pine trees',
        'جبل': 'epic snow-capped mountain peak', 'جبال': 'rugged dramatic mountains',
        'صحراء': 'vast cinematic desert dunes', 'رمال': 'golden rippling sands',
        'مدينة': 'futuristic cyberpunk city skyline', 'سماء': 'dramatic cloudscape sky',
        'مطر': 'cinematic rain with glistening puddles', 'عاصفة': 'dramatic storm atmosphere',
        'طائرة': 'airplane soaring through clouds', 'سفينة': 'majestic ship on rolling waves',
        'سينمائي': 'cinematic', 'سينمائية': 'cinematic', 'لقطة': 'photographic master shot',
        'لقطة عامة': 'wide establishing shot', 'لقطة قريبة': 'intimate close-up shot',
        'لقطة متوسطة': 'medium cinematic shot', 'لقطة تتبع': 'cinematic tracking shot',
        'بورتريه': 'intimate character portrait', 'إضاءة': 'dramatic chiaroscuro lighting',

        # French Directorial Terms
        'plan d ensemble': 'wide establishing master shot',
        'plan general': 'wide cinematic master shot',
        'plan moyen': 'medium character shot',
        'plan americain': 'american cowboy medium shot',
        'gros plan': 'intimate close-up portrait',
        'tres gros plan': 'extreme close-up detail shot',
        'plongee': 'high angle overhead perspective shot',
        'contre plongee': 'dramatic low-angle hero shot',
        'travelling': 'fluid cinematic tracking shot',
        'panoramique': 'smooth cinematic pan',
        'lumiere naturelle': 'soft natural ambient lighting',
        'contre jour': 'dramatic backlight silhouette with golden rim lighting',
        'flou d arriere plan': 'shallow depth of field, creamy bokeh',
        'homme': 'distinguished man',
        'femme': 'elegant woman',
        'fille': 'young woman',
        'garcon': 'young man',
        'enfant': 'young child',
        'chien': 'dog',
        'chat': 'cat',
        'voiture': 'sleek automobile',
        'pluie': 'heavy cinematic rain with wet asphalt reflections',
        'nuit': 'nighttime with volumetric neon glow',
        'jour': 'daytime with crisp natural sunlight',
        'soleil': 'golden hour sunlight',
        'foret': 'ancient mystical pine forest',
        'plage': 'golden sand beach and tranquil ocean waves',
        'desert': 'vast sweeping sand dunes',
        'ville': 'futuristic neon metropolis',
        'rue': 'atmospheric urban cobblestone street',
        'marchant': 'walking gracefully',
        'courant': 'running dynamically with motion blur',
        'sombre': 'moody dark chiaroscuro lighting',
        'cinematique': 'cinematic 8k masterpiece',
        'lumiere': 'volumetric atmospheric lighting',

        # Spanish Directorial Terms
        'plano general': 'wide cinematic establishing master shot',
        'plano entero': 'full length character shot',
        'plano medio': 'medium cinematic shot',
        'plano americano': 'cowboy medium shot, knees up',
        'primer plano': 'dramatic intimate close-up shot',
        'primerisimo primer plano': 'extreme close-up portrait',
        'plano cenital': 'overhead bird eye view shot',
        'plano picado': 'high angle perspective shot',
        'plano contrapicado': 'dramatic low-angle hero perspective',
        'paneo': 'smooth cinematic horizontal pan',
        'luz natural': 'soft natural ambient lighting',
        'contraluz': 'dramatic rim lighting and backlight silhouette',
        'profundidad de campo': 'shallow depth of field with cinematic bokeh',
        'mujer': 'elegant woman',
        'chica': 'young woman',
        'chico': 'young man',
        'nino': 'young child',
        'perro': 'dog',
        'gato': 'cat',
        'coche': 'sleek automobile',
        'auto': 'sleek sports car',
        'lluvia': 'heavy cinematic rain with glistening puddles',
        'noche': 'atmospheric night with neon reflections',
        'dia': 'bright sunny day with crisp shadows',
        'sol': 'golden sunlight with warm lens flares',
        'bosque': 'deep mystical pine forest',
        'playa': 'golden sand beach with turquoise waves',
        'desierto': 'vast cinematic sand dunes',
        'ciudad': 'cyberpunk metropolis skyline',
        'calle': 'moody urban cobblestone street',
        'caminando': 'walking with steady cadence',
        'corriendo': 'running with dynamic energy',
        'oscuro': 'dark moody chiaroscuro lighting',
        'cinematografico': 'cinematic 8k masterpiece',
        'luz': 'dramatic volumetric light'
    }

    normalized = text
    diacritic_map = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'à': 'a', 'â': 'a', 'ä': 'a',
        'î': 'i', 'ï': 'i', 'ô': 'o', 'ö': 'o', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n', 'á': 'a', 'í': 'i', 'ó': 'o', 'ú': 'u', "'": ' '
    }
    for char, rep in diacritic_map.items():
        normalized = normalized.replace(char, rep)

    working_text = normalized.lower()
    for phrase, replacement in lexicon.items():
        if phrase in working_text:
            working_text = working_text.replace(phrase, replacement)

    tokens = text.split()
    translated_tokens = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens):
            pair = f"{tokens[i]} {tokens[i+1]}"
            if pair in lexicon:
                translated_tokens.append(lexicon[pair])
                i += 2
                continue
        token = tokens[i].strip('،.!,?')
        if token in lexicon:
            translated_tokens.append(lexicon[token])
        elif re.search(r'[؀-ۿ]', token):
            pass
        else:
            translated_tokens.append(token)
        i += 1

    subject = " ".join(translated_tokens).strip() or working_text.strip() or "cinematic subject"

    if mode == 'video':
        return f"A cinematic sequence of {subject}, shot on 35mm lens, atmospheric lighting, dynamic natural motion, photorealistic 8k"
    return f"A detailed cinematic photograph of {subject}, shot on 35mm prime lens, volumetric natural lighting, photorealistic 8k"


def _local_arabic_to_cinematic_english(text, mode='image'):
    return _cross_lingual_cinematic_transmute(text, mode=mode)

BRIDGE_TASKS = []

BRIDGE_RESULTS = []

BRIDGE_ACKS = {}

BRIDGE_STATE = {"last_poll": 0.0, "flow_open": False}



# --- Security: only the Studio page (same origin) and the Flow Bridge extension may talk to this server ---

ALLOWED_ORIGINS = {f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"}

ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}   # blocks DNS-rebinding

EXTENSION_PATHS = ('/api/bridge/', '/api/status', '/api/tts')           # what the extension is allowed to call



def get_full_models_catalog():

    return {

        "video_models": [

            {"id": "fal-ai/minimax/h3-lite", "name": "1. MiniMax H3 Lite [الأرخص ~$0.04]", "tag": "⚡ فائق السرعة وأرخص فيديو لتجارب اللقطات المتعددة", "type": "video"},

            {"id": "fal-ai/wan/v2.1/t2v-14b", "name": "2. Wan 2.1 (Alibaba 14B) [اقتصادي ~$0.05]", "tag": "💎 أرخص وأقوى نموذج فيديو بمحاكاة فيزيائية طبيعية", "type": "video"},

            {"id": "fal-ai/hunyuan-video", "name": "3. Tencent HunyuanVideo (13B) [ثابت ~$0.06]", "tag": "🎬 مفتوح المصدر بثبات فيزيائي فائق وعدم اهتزاز المشهد", "type": "video"},

            {"id": "fal-ai/cogvideox-5b", "name": "4. CogVideoX-5B (THUDM) [سينمائي ~$0.06]", "tag": "🎥 نموذج سينمائي 3D VAE عالي الدقة واقتصادي", "type": "video"},

            {"id": "fal-ai/tbc/mischief-1/image-to-video", "name": "5. Mischief-1 Image-to-Video [أكشن ~$0.10]", "tag": "🔥 بطل الأكشن والمؤثرات البصرية الديناميكية الفائقة", "type": "video"},

            {"id": "fal-ai/kling-video/v1/standard/text-to-video", "name": "6. Kling AI Standard [متوسط ~$0.12]", "tag": "سريع واقتصادي للقطات الاختبارية والفيزياء", "type": "video"},

            {"id": "fal-ai/luma-dream-machine", "name": "7. Luma Ray 2 & Dream Machine [متوسط ~$0.12]", "tag": "🌊 حركة تدفقية وانتقالات مكانية ودوران ناعم", "type": "video"},

            {"id": "fal-ai/minimax/video-01", "name": "8. MiniMax H3 / Hailuo [شخصيات ~$0.15]", "tag": "⚡ بطل الحركة السريعة والانفجارات والمطاردات", "type": "video"},

            {"id": "fal-ai/blackforestlabs/flux-3-max/image-to-video", "name": "9. Flux 3 Max Image-to-Video [احترافي ~$0.25]", "tag": "🌟 أعلى دقة تحريك فوتوغرافي واقعي من الكي فريم", "type": "video"},

            {"id": "fal-ai/minimax/h3-max-turbo/reference-to-video", "name": "10. MiniMax H3 Max Turbo [مرجع وجه ~$0.25]", "tag": "🎯 قفل هوية الشخصية المرجعية مع أوامر الكاميرا [Brackets]", "type": "video"},

            {"id": "fal-ai/kling-video/v1.5/pro/text-to-video", "name": "11. Kling 1.6 & 2.5 Pro [هوليوودي 1080p ~$0.35]", "tag": "👑 ملك الواقعية البشرية والفيزياء مع صوت مدمج", "type": "video"}

        ],

        "image_keyframe_models": [

            {"id": "fal-ai/flux/schnell", "name": "FLUX.1 Schnell", "tag": "أسرع إطار مفتاحي فوري (ثانيتان)", "type": "image"},

            {"id": "fal-ai/flux/dev", "name": "FLUX.1 Dev", "tag": "أعلى دقة تفاصيل سينمائية 1080p", "type": "image"},

            {"id": "fal-ai/flux-pro/v1.1-ultra", "name": "FLUX 1.1 Pro Ultra", "tag": "جودة تصوير فوتوغرافي خام 2K RAW", "type": "image"},

            {"id": "google/imagen-3", "name": "Google Imagen 3 (Direct API)", "tag": "محرك جوجل الرائد المباشر بحسابك", "type": "image"},

            {"id": "fal-ai/recraft-v3", "name": "Recraft v3", "tag": "تصميم دقيق وواقعية متفوقة", "type": "image"},

            {"id": "fal-ai/ideogram/v2", "name": "Ideogram v2", "tag": "دقة استثنائية في كتابة الحروف والخطوط", "type": "image"}

        ],

        "audio_and_tools": [

            {"id": "fal-ai/mmaudio-v2", "name": "MMAudio v2", "tag": "توليد مؤثرات وموسيقى متزامنة مع حركة الفيديو", "type": "audio"},

            {"id": "fal-ai/clarity-upscaler", "name": "Clarity 4K Upscaler", "tag": "رفع دقة الفيديو والصور لجودة 4K خرافية", "type": "tool"}

        ]

    }



def get_intelligence_report():

    return {

        "report_title": "تقرير رادار تطور أحدث أدوات ونماذج الفيديو بالذكاء الاصطناعي (AI Video Radar 2026)",

        "updated_at": "تحديث مباشر شامل (2026)",

        "author": "سيندي (Cindy) - المساعدة الإخراجية الذكية (1st AD)",

        "executive_summary": "ملخص مبدئي غير محقَّق بالكامل — راجع المصادر الرسمية: Kling مع الصوت المدمج، MiniMax Hailuo، Seedance، Wan، بالتوازي مع Google Veo 3.1.",

        "top_models": [

            {"name": "Kling 3.0 / 4.0 Pro", "category": "الأقوى في الواقعية البشرية والفيزياء ودقة 1080p", "strengths": "توليد الصوت المدمج، ضبط إطار البداية والنهاية، وموشن براش متطور بدون تشوه.", "best_for": "الأفلام، الحوارات، والإعلانات الواقعية."},

            {"name": "MiniMax H3 / H3 Max", "category": "بطل الحركة الديناميكية والأكشن بدقة 2K", "strengths": "استجابة خارقة للمطاردات والرياح والانفجارات وتوليد الصوت المتزامن.", "best_for": "الأكشن، الخيال العلمي، والمشاهد السريعة."},

            {"name": "Google Veo 3.1 & Imagen 3", "category": "محركات جوجل الرائدة المباشرة", "strengths": "دقة 4K وصوت حواري متزامن وتوليد مباشر عبر API.", "best_for": "الإنتاج المتكامل."}

        ]

    }



class CindySecureHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, directory=BASE_DIR, **kwargs)



    def _origin_ok(self, is_post=False):

        origin = self.headers.get('Origin') or ''

        clean_path = (self.path or '').split('?')[0]

        # Allow Chrome Extension requests to /api/bridge/* and /api/status even when Chrome sets Sec-Fetch-Site: cross-site

        if clean_path.startswith(EXTENSION_PATHS):

            if origin.startswith('chrome-extension://'):

                return True

            if not origin:

                referer = self.headers.get('Referer') or ''

                if not referer or referer.startswith('chrome-extension://') or any(referer.startswith(o) for o in ALLOWED_ORIGINS):

                    return True

        sec_site = (self.headers.get('Sec-Fetch-Site') or '').lower()

        if sec_site == 'cross-site':

            return False

        if origin:

            if origin in ALLOWED_ORIGINS:

                return True

            return False

        # When Origin header is absent on POST, block cross-origin form submissions by checking Referer if Sec-Fetch-Site is present

        if is_post and sec_site and sec_site not in ('same-origin', 'none'):

            return False

        referer = self.headers.get('Referer') or ''

        if referer and not any(referer.startswith(o + '/') or referer == o for o in ALLOWED_ORIGINS):

            return False

        return True



    def _guard(self, is_post=False):

        """Reject foreign hosts/origins. Returns True when the request may proceed."""

        if self.headers.get('Host', '') not in ALLOWED_HOSTS or not self._origin_ok(is_post=is_post):

            self.send_error_response(403, "Forbidden origin")

            return False

        return True



    def end_headers(self):

        origin = self.headers.get('Origin')

        if origin and self._origin_ok():

            self.send_header('Access-Control-Allow-Origin', origin)

            self.send_header('Vary', 'Origin')

            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Cindy-Client')

        self.send_header('X-Content-Type-Options', 'nosniff')

        self.send_header('X-Frame-Options', 'DENY')

        self.send_header('Referrer-Policy', 'no-referrer')

        self.send_header('Cross-Origin-Resource-Policy', 'same-origin')

        self.send_header('Cache-Control', 'no-store')

        clean_path = (self.path or '').split('?')[0]

        if clean_path.startswith('/outputs/'):

            self.send_header('Content-Security-Policy', "default-src 'none'; img-src 'self'; media-src 'self'; style-src 'unsafe-inline'; sandbox")

        super().end_headers()



    def log_message(self, fmt, *args):

        pass  # no request logging (privacy: prompts never hit the console/log)



    def do_OPTIONS(self):

        if not self._guard():

            return

        self.send_response(204)

        self.end_headers()



    def do_GET(self):

        if not self._guard():

            return

        if self.path == '/api/tts/voices':
            try:
                import cindy_local_tts
                self.send_json_response(200, {"voices": cindy_local_tts.list_voices()})
            except Exception as e:
                self.send_json_response(500, {"error": str(e)})
            return

        if self.path.startswith('/api/tts'):
            self.handle_tts()
            return



        if self.path == '/api/status':

            secrets = load_secrets()

            fal_key = secrets.get('fal_api_key', '')

            gemini_key = secrets.get('gemini_api_key', '')

            self.send_json_response(200, {

                "status": "online",

                "fal_key_active": bool(fal_key),

                "fal_key_masked": mask_token(fal_key),

                "gemini_key_active": bool(gemini_key),

                "gemini_key_masked": mask_token(gemini_key),

                "message": "محرك سيندي للتنفيذ الفعلي متصل بقاعدة النماذج الأحدث 2026"

            })

            return



        elif self.path == '/api/vault/status':

            secrets = load_secrets()

            vault_status = {}

            for k, v in secrets.items():

                if k.endswith('_key'):

                    svc = k.replace('_api_key', '')

                    vault_status[svc] = {"configured": bool(v), "masked": mask_token(v)}

                elif k.endswith('_url'):

                    svc = k.replace('_url', '')

                    vault_status[svc] = {"configured": bool(v), "url": v}

            self.send_json_response(200, vault_status)

            return



        elif self.path == '/api/models/catalog':

            catalog = get_full_models_catalog()

            self.send_json_response(200, catalog)

            return

        elif self.path == '/api/blender/latest_guide' or self.path == '/api/previs/latest':

            self.handle_latest_blender_guide()

            return



        elif self.path == '/api/research_report':

            report = get_intelligence_report()

            self.send_json_response(200, report)

            return



        elif self.path.startswith('/api/bridge/poll') or self.path == '/api/bridge/pending_task':

            parsed = urllib.parse.urlparse(self.path)

            qs = urllib.parse.parse_qs(parsed.query)

            BRIDGE_STATE['last_poll'] = time.time()

            if 'flow_open' in qs:

                BRIDGE_STATE['flow_open'] = (qs['flow_open'][0] == '1')

            if BRIDGE_TASKS:

                task = BRIDGE_TASKS.pop(0)

                self.send_json_response(200, {"has_task": True, "task": task})

            else:

                self.send_json_response(200, {"has_task": False})

            return



        elif self.path.startswith('/api/bridge/status'):

            alive = (time.time() - BRIDGE_STATE.get('last_poll', 0.0)) < 6.0

            self.send_json_response(200, {

                "alive": alive,

                "flow_open": BRIDGE_STATE.get('flow_open', False),

                "acks": BRIDGE_ACKS,

                "results_count": len(BRIDGE_RESULTS),

                "latest_result": BRIDGE_RESULTS[-1] if BRIDGE_RESULTS else None

            })

            return



        elif self.path == '/api/bridge/results':

            self.send_json_response(200, {"results": BRIDGE_RESULTS})

            return



        elif self.path == '/api/lora/list':

            self.handle_lora_list()

            return



        elif self.path.startswith('/api/lora/job_status'):

            self.handle_lora_job_status()

            return



        elif self.path.startswith('/api/lora/download'):

            self.handle_lora_download()

            return



        elif self.path.startswith('/api/comfyui/video_status'):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            job_id = qs.get('job_id', [''])[0]
            job = VIDEO_JOBS.get(job_id, {'status': 'not_found', 'message': 'المهمة غير موجودة'})
            self.send_json_response(200, job)
            return

        elif self.path == '/api/comfyui/node_status':
            secrets = load_secrets()
            url = secrets.get('local_comfyui_url', '').strip()
            caps = comfyui_client.check_comfyui_node_capabilities(url)
            self.send_json_response(200, caps)
            return

        elif self.path == '/api/comfyui/status':

            self.handle_comfyui_status()

            return



        elif self.path == '/api/runpod/status':

            self.handle_runpod_status()

            return



        elif self.path == '/api/radar/trends' or self.path.startswith('/api/radar/trends'):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            force = (qs.get('force', ['false'])[0].lower() == 'true')
            secrets = load_secrets()
            data = cindy_radar.get_latest_cinema_trends(force_refresh=force, secrets=secrets)
            self.send_json_response(200, {"success": True, "radar": data})
            return
        elif self.path == '/api/storyboard/list':
            data = cindy_storyboard.load_storyboards()
            self.send_json_response(200, {"success": True, "storyboards": data.get("projects", [])})
            return
        elif self.path == '/api/pricing/daily' or self.path.startswith('/api/pricing/daily'):
            self.handle_pricing_daily(force_refresh=False)
            return

        elif self.path == '/api/pricing/refresh' or self.path.startswith('/api/pricing/refresh'):
            self.handle_pricing_daily(force_refresh=True)
            return

        elif self.path == '/api/wallet/status':

            self.handle_wallet_status()

            return



        elif self.path.startswith('/api/edit_media/poll'):

            self.handle_edit_media_poll()

            return



        elif self.path.startswith('/api/download'):

            self.handle_media_download()

            return



        else:

            # Static files: allow-list only (never serve cindy_secrets.json, *.py, memory, etc.)

            clean = self.path.split('?')[0].split('#')[0]

            if clean in ('/cinema_bg_4.jpg', '/cinema_bg_1.jpg', '/cinema_bg_2.jpg', '/cinema_bg_3.jpg'):
                img_path = os.path.join(BASE_DIR, clean.lstrip('/'))
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(content)))
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(content)
                    return

            if clean in ('/', '/index.html'):

                html_path = os.path.join(BASE_DIR, 'index.html')

                if os.path.exists(html_path):

                    with open(html_path, 'rb') as f:

                        content = f.read()

                    self.send_response(200)

                    self.send_header('Content-Type', 'text/html; charset=utf-8')

                    self.send_header('Content-Length', str(len(content)))

                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')

                    self.send_header('Pragma', 'no-cache')

                    self.send_header('Expires', '0')

                    self.end_headers()

                    self.wfile.write(content)

                    return

                return super().do_GET()

            if clean.startswith('/outputs/'):

                rel = clean[len('/outputs/'):]

                if _safe_output_path(rel):

                    return super().do_GET()

            self.send_error_response(404, "Not found")



    def do_POST(self):

        if not self._guard(is_post=True):

            return

        try:

            content_length = int(self.headers.get('Content-Length', 0))

        except ValueError:

            self.send_error_response(400, "Invalid Content-Length")

            return

        max_bytes = 150 * 1024 * 1024 if self.path in ('/api/upload', '/api/bridge/complete_task', '/api/lora/train') else 2 * 1024 * 1024

        if content_length < 0 or content_length > max_bytes:

            self.send_error_response(413, "Payload Too Large")

            return

        body = self.rfile.read(content_length).decode('utf-8', errors='replace') if content_length > 0 else '{}'

        try:

            payload = json.loads(body)

        except:

            payload = {}



        if self.path == '/api/previs/generate':
            self.handle_generate_previs(payload)
            return

        elif self.path == '/api/tts/voice-convert':
            audio_b64 = payload.get('audio_base64', '').strip()
            audio_mime = payload.get('audio_mime', 'audio/webm')
            voice = payload.get('voice', 'cindy_flash_aoede').strip()
            speed = float(payload.get('speed', 1.0))
            lang = payload.get('lang', 'ar')

            if not audio_b64:
                self.send_error_response(400, "Audio data is required")
                return

            try:
                raw_input_audio = base64.b64decode(audio_b64)
                transcription = ""
                secrets = load_secrets()
                gemini_key = secrets.get('gemini_api_key', '').strip()

                # 1. Transcribe the Director's human vocal performance using Gemini
                if gemini_key:
                    for model_cand in ('gemini-2.5-flash-preview-tts', 'gemini-3.8-flash-lite-tts'):
                        try:
                            t_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_cand}:generateContent?key={gemini_key}"
                            t_body = {
                                "contents": [{
                                    "parts": [
                                        {"text": (
                                            "You are an expert film audio supervisor and dialect coach. "
                                            "Carefully transcribe all spoken words in this audio verbatim. "
                                            "Preserve and denote any audible emotional acting cues, sighs, laughs, choked cries, or whispered expressions in parentheses like: (تنهيدة عميقة), (ضحكة ساخرة), (sigh), (gasp). "
                                            "Return ONLY the plain transcription text with parenthetical cues, no extra conversational preamble."
                                        )},
                                        {"inlineData": {"mimeType": audio_mime, "data": audio_b64}}
                                    ]
                                }]
                            }
                            resp = requests.post(t_url, json=t_body, timeout=15)
                            if resp.status_code == 200:
                                t_text = resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                if t_text and t_text.strip():
                                    transcription = t_text.strip()
                                    break
                        except Exception as e_tr:
                            print(f"[Transcribe Warning {model_cand}]:", e_tr)

                if not transcription:
                    transcription = "أداء تمثيلي بشري مباشر من المخرج" if lang == 'ar' else "Direct human vocal performance from the director"

                # 2. Resynthesize with the chosen actor voice
                audio_bytes = None
                if voice.startswith('gemini_') or voice in ('cindy_flash_aoede', 'cindy_flash_masri'):
                    if gemini_key:
                        voice_name_map = {
                            'gemini_aoede': 'Aoede',
                            'gemini_puck': 'Puck',
                            'gemini_charon': 'Charon',
                            'gemini_kore': 'Kore',
                            'gemini_fenrir': 'Fenrir',
                            'cindy_flash_aoede': 'Aoede',
                            'cindy_flash_masri': 'Aoede'
                        }
                        chosen_voice_name = voice_name_map.get(voice, 'Aoede')
                        phonetic_prompt = (
                            "You are a professional film voice actor replicating this performance: "
                            "ACT OUT and vocally perform all emotional stage directions in parentheses with lifelike cinematic depth: "
                            f"{transcription}"
                        )
                        if voice in ('cindy_flash_aoede', 'cindy_flash_masri') or any(c in transcription for c in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'):
                            phonetic_prompt = (
                                "You are a master Egyptian cinema voice actor. "
                                "Speak in an authentic, natural Cairo Egyptian colloquial accent (Masri). "
                                "Perform with the exact raw human feeling and dramatic emotion: "
                                f"{transcription}"
                            )

                        for model_ep in ('gemini-2.5-flash-preview-tts', 'gemini-3.8-flash-lite-tts'):
                            try:
                                g_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_ep}:generateContent?key={gemini_key}"
                                g_body = {
                                    "contents": [{"parts": [{"text": phonetic_prompt}]}],
                                    "generationConfig": {
                                        "responseModalities": ["AUDIO"],
                                        "speechConfig": {
                                            "voiceConfig": {
                                                "prebuiltVoiceConfig": {"voiceName": chosen_voice_name}
                                            }
                                        }
                                    }
                                }
                                resp = requests.post(g_url, json=g_body, timeout=12)
                                if resp.status_code == 200:
                                    b64_raw = resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("inlineData", {}).get("data", "")
                                    if b64_raw:
                                        raw_aud = base64.b64decode(b64_raw)
                                        audio_bytes = self._ensure_wav_bytes(raw_aud, sample_rate=24000)
                                        break
                            except Exception as ex_gem:
                                print(f"[Gemini Flash TTS error]: {ex_gem}")

                if not audio_bytes:
                    import cindy_local_tts
                    audio_bytes = cindy_local_tts.synthesize(transcription, voice_id=voice, speed=speed)

                if not audio_bytes or len(audio_bytes) < 500:
                    self.send_error_response(500, "Failed to resynthesize audio with selected actor")
                    return

                ts = int(time.time())
                fname = f"voice_converted_{ts}.wav"
                fpath = os.path.join(OUTPUTS_DIR, fname)
                with open(fpath, 'wb') as fh:
                    fh.write(audio_bytes)

                self.send_json_response(200, {
                    "success": True,
                    "filename": fname,
                    "url": f"/outputs/{fname}",
                    "voice": voice,
                    "transcription": transcription,
                    "message": "تم تحويل أدائك البشري إلى الممثل الصوتي بنجاح!"
                })
            except Exception as e:
                self.send_error_response(500, f"Error converting voice performance: {str(e)}")
            return

        elif self.path == '/api/tts/generate':
            text = payload.get('text', '').strip()
            voice = payload.get('voice', 'auto').strip()
            speed = float(payload.get('speed', 1.0))
            if not text:
                self.send_error_response(400, "Text is required")
                return
            try:
                audio_bytes = None
                
                # Check if Google Gemini Native Flash TTS is requested:
                if voice.startswith('gemini_') or voice in ('cindy_flash_aoede', 'cindy_flash_masri'):
                    secrets = load_secrets()
                    gemini_key = secrets.get('gemini_api_key', '').strip()
                    if gemini_key:
                        voice_name_map = {
                            'gemini_aoede': 'Aoede',
                            'gemini_puck': 'Puck',
                            'gemini_charon': 'Charon',
                            'gemini_kore': 'Kore',
                            'gemini_fenrir': 'Fenrir',
                            'cindy_flash_aoede': 'Aoede',
                            'cindy_flash_masri': 'Aoede'
                        }
                        chosen_voice_name = voice_name_map.get(voice, 'Aoede')
                        # Enhanced Cinematic Acting Director Instruction:
                        # Instructs Gemini Flash TTS to genuinely act out parenthetical cues (e.g. sighs, laughter, choked sobbing)
                        phonetic_prompt = (
                            "You are a professional film voice actor. "
                            "ACT OUT and vocally perform any emotion cues written in parentheses (such as sighs, sarcastic chuckles, choked crying, breathless gasps, trembling fear, groans) "
                            f"with genuine human cinematic realism: {text}"
                        )
                        if voice in ('cindy_flash_aoede', 'cindy_flash_masri') or any(c in text for c in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'):
                            phonetic_prompt = (
                                "You are a master Egyptian cinema voice actor. "
                                "Speak in an authentic, natural Cairo Egyptian colloquial accent (Masri). "
                                "Directly act out and vocally perform all emotional stage directions in parentheses "
                                "(مثل: التنهيدة، الضحكة الساخرة، الشحتفة والبكاء، الرعشة، التأوه، الغضب) "
                                f"with raw, lifelike human emotion and theatrical pacing: {text}"
                            )
                            
                        for model_ep in ('gemini-2.5-flash-preview-tts', 'gemini-3.8-flash-lite-tts'):
                            try:
                                g_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_ep}:generateContent?key={gemini_key}"
                                g_body = {
                                    "contents": [{"parts": [{"text": phonetic_prompt}]}],
                                    "generationConfig": {
                                        "responseModalities": ["AUDIO"],
                                        "speechConfig": {
                                            "voiceConfig": {
                                                "prebuiltVoiceConfig": {"voiceName": chosen_voice_name}
                                            }
                                        }
                                    }
                                }
                                resp = requests.post(g_url, json=g_body, timeout=12)
                                if resp.status_code == 200:
                                    b64_raw = resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("inlineData", {}).get("data", "")
                                    if b64_raw:
                                        raw_aud = base64.b64decode(b64_raw)
                                        audio_bytes = self._ensure_wav_bytes(raw_aud, sample_rate=24000)
                                        break
                            except Exception as ex_gem:
                                print(f"[Gemini Flash TTS error]: {ex_gem}")
                                
                if not audio_bytes:
                    import cindy_local_tts
                    audio_bytes = cindy_local_tts.synthesize(text, voice_id=voice, speed=speed)
                if not audio_bytes or len(audio_bytes) < 500:
                    self.send_error_response(500, "Failed to generate audio")
                    return
                ts = int(time.time())
                fname = f"voice_acting_{ts}.wav"
                fpath = os.path.join(OUTPUTS_DIR, fname)
                with open(fpath, 'wb') as fh:
                    fh.write(audio_bytes)
                self.send_json_response(200, {
                    "success": True,
                    "filename": fname,
                    "url": f"/outputs/{fname}",
                    "voice": voice,
                    "text": text,
                    "message": "تم توليد الأداء الصوتي بنجاح محلياً!"
                })
            except Exception as e:
                self.send_error_response(500, f"Error generating speech: {str(e)}")
            return

        if self.path == '/api/bridge/debug':

            # Local-only diagnostics: control labels of the Flow page (no page text), appended to a local file.

            try:

                with open(os.path.join(BASE_DIR, 'bridge_debug.jsonl'), 'a', encoding='utf-8') as fh:

                    fh.write(json.dumps(payload, ensure_ascii=False) + '\n')

            except Exception:

                pass

            self.send_json_response(200, {"success": True})

            return

        if self.path in ('/api/bridge/send_task', '/api/bridge/enqueue'):

            BRIDGE_TASKS.append(payload)

            self.send_json_response(200, {"success": True, "message": "تم إدراج المهمة للجسر بنجاح"})

            return

        elif self.path == '/api/bridge/ack':

            tid = payload.get('task_id', '')

            if tid:

                BRIDGE_ACKS[tid] = payload.get('result', {})

            self.send_json_response(200, {"success": True})

            return

        elif self.path == '/api/bridge/complete_task':

            ts = int(time.time() * 1000)

            payload['completed_at'] = ts

            def _save_data_url(u, idx=0):

                if isinstance(u, str) and u.startswith('data:') and ';base64,' in u:

                    header, b64data = u.split(';base64,', 1)

                    raw = base64.b64decode(b64data)

                    m_type, ext = _detect_magic_media(raw)

                    if not ext:

                        return ''

                    fname = f"flow_media_{ts}_{idx}.{ext}"

                    fpath = _safe_output_path(fname)

                    if fpath:

                        with open(fpath, 'wb') as fh:

                            fh.write(raw)

                        return f"/outputs/{fname}"

                return u



            if isinstance(payload.get('images'), list):

                new_imgs = []

                for idx, im in enumerate(payload['images']):

                    if isinstance(im, dict) and im.get('url'):

                        new_imgs.append({"url": _save_data_url(im['url'], idx + 1)})

                if new_imgs:

                    payload['images'] = new_imgs

                    payload['url'] = new_imgs[0]['url']

            elif payload.get('url'):

                payload['url'] = _save_data_url(payload['url'], 1)



            BRIDGE_RESULTS.append(payload)

            self.send_json_response(200, {"success": True, "media": payload, "message": "تم استلام النتيجة من جوجل فلو"})

            return

        elif self.path == '/api/storyboard/breakdown':
            script_text = str(payload.get('script_text', '')).strip()
            notes = str(payload.get('director_notes', '')).strip()
            if not script_text:
                self.send_error_response(400, "Script text is required")
                return
            secrets = load_secrets()
            breakdown = cindy_storyboard.breakdown_script_with_ai(script_text, notes, secrets)
            self.send_json_response(200, {"success": True, "breakdown": breakdown})
            return
        elif self.path == '/api/storyboard/render_frame':
            prompt = str(payload.get('prompt', '')).strip()
            aspect = str(payload.get('aspect_ratio', '16:9')).strip()
            if not prompt:
                self.send_error_response(400, "Visual prompt is required")
                return
            secrets = load_secrets()
            fal_key = secrets.get('fal_api_key', '').strip()
            try:
                frame_url = cindy_storyboard.render_storyboard_frame(prompt, aspect, fal_key)
                self.send_json_response(200, {"success": True, "frame_url": frame_url})
            except Exception as e:
                self.send_error_response(500, f"Frame render failed: {str(e)}")
            return
        elif self.path == '/api/storyboard/save':
            project = payload.get('project')
            if not project:
                self.send_error_response(400, "Project data is required")
                return
            store = cindy_storyboard.load_storyboards()
            # replace or append
            projects = store.get('projects', [])
            p_id = project.get('id') or f"proj_{int(time.time())}"
            project['id'] = p_id
            project['updated_at'] = int(time.time())
            existing = [p for p in projects if p.get('id') == p_id]
            if existing:
                idx = projects.index(existing[0])
                projects[idx] = project
            else:
                projects.insert(0, project)
            store['projects'] = projects
            cindy_storyboard.save_storyboards(store)
            self.send_json_response(200, {"success": True, "project": project})
            return
        elif self.path == '/api/pricing/refresh':
            self.handle_pricing_daily(force_refresh=True)

        elif self.path == '/api/vault/update':

            self.handle_vault_update(payload)

        elif self.path == '/api/vault/test_key':

            self.handle_vault_test_key(payload)

        elif self.path == '/api/chat':

            self.handle_chat(payload)

        elif self.path == '/api/execute' or self.path == '/api/generate':

            self.handle_universal_execute(payload)

        elif self.path == '/api/critique':

            self.handle_critique(payload)

        elif self.path == '/api/upload':

            self.handle_media_upload(payload)

        elif self.path == '/api/analyze_media':

            self.handle_analyze_media(payload)

        elif self.path.startswith('/api/edit_media/poll'):

            self.handle_edit_media_poll()

        elif self.path == '/api/comfyui/connect':

            self.handle_comfyui_connect(payload)

        elif self.path == '/api/comfyui/launch':

            self.handle_comfyui_launch(payload)

        elif self.path == '/api/comfyui/stop':

            self.handle_comfyui_stop(payload)

        elif self.path == '/api/comfyui/generate':

            self.handle_comfyui_generate(payload)

        elif self.path == '/api/comfyui/install_nodes':
            secrets = load_secrets()
            url = secrets.get('local_comfyui_url', '').strip()
            if not url:
                self.send_error_response(400, "يرجى ربط سيرفر ComfyUI أولاً.")
                return
            res = comfyui_client.install_comfyui_custom_nodes(url)
            self.send_json_response(200, {"success": True, "results": res, "message": "تم إرسال أوامر تثبيت حزم الـ Nodes إلى ComfyUI وجاري إعادة تشغيل السيرفر."})
            return

        elif self.path == '/api/comfyui/generate_video':

            self.handle_comfyui_generate_video(payload)

        elif self.path == '/api/comfyui/liveportrait' or self.path == '/api/comfyui/motion_control':

            self.handle_comfyui_motion_control(payload)

        elif self.path == '/api/comfyui/latentsync':

            self.handle_comfyui_latentsync(payload)

        elif self.path == '/api/runpod/train':

            self.handle_runpod_train(payload)

        elif self.path == '/api/runpod/terminate_all':

            self.handle_runpod_terminate_all()

        elif self.path == '/api/runpod/status':

            self.handle_runpod_status()

        elif self.path == '/api/edit_media':

            self.handle_edit_media(payload)

        elif self.path == '/api/translate_prompt':

            self.handle_translate_prompt(payload)

        elif self.path == '/api/lora/train':

            self.handle_lora_train(payload)

        elif self.path == '/api/lora/execute':

            self.handle_lora_execute(payload)

        elif self.path == '/api/lora/import':

            self.handle_lora_import(payload)

        elif self.path == '/api/lora/upload':

            self.handle_lora_upload(payload)

        elif self.path == '/api/lora/delete':

            self.handle_lora_delete(payload)

        else:

            self.send_error_response(404, "Endpoint not found.")



    def handle_vault_update(self, payload):

        service = payload.get('service', '').strip()

        key_value = payload.get('key_value', '').strip()

        if not service:

            self.send_error_response(400, "Service name required.")

            return



        secrets = load_secrets()

        if service.endswith('_url'):
            field_name = service
        elif service.startswith('local_'):
            field_name = f"{service}_url"
        else:
            field_name = f"{service}_api_key"

        secrets[field_name] = key_value

        success = save_secrets(secrets)

        if success:

            self.send_json_response(200, {

                "success": True,

                "service": service,

                "masked": mask_token(key_value),

                "message": f"تم حفظ وتأمين مفتاح {service} محلياً بنجاح!"

            })

        else:

            self.send_error_response(500, "فشل حفظ المفتاح.")



    def handle_vault_test_key(self, payload):

        service = payload.get('service', 'fal')

        secrets = load_secrets()

        key = secrets.get(f"{service}_api_key", "")



        if not key:

            self.send_error_response(400, "المفتاح غير متوفر في الخزنة.")

            return



        if service == 'fal':

            headers = {"Authorization": f"Key {key}"}

            try:

                r = requests.get("https://fal.run/fal-ai/flux/schnell", headers=headers, timeout=10)

                if r.status_code not in [401, 403]:

                    self.send_json_response(200, {"success": True, "message": "مفتاح Fal.ai متصل وصحيح بنسبة 100%!"})

                else:

                    self.send_error_response(401, "مفتاح Fal.ai غير صالح.")

            except Exception as e:

                self.send_error_response(500, f"خطأ اتصال: {e}")

        elif service == 'gemini':

            url = "https://generativelanguage.googleapis.com/v1beta/models"

            try:

                r = requests.get(url, headers={"x-goog-api-key": key}, timeout=10)

                if r.status_code == 200:

                    self.send_json_response(200, {"success": True, "message": "مفتاح Google Gemini / Flow متصل ويعمل بنجاح!"})

                else:

                    self.send_error_response(r.status_code, f"خطأ في مفتاح Google: {r.text[:150]}")

            except Exception as e:

                self.send_error_response(500, f"خطأ اتصال: {e}")

        elif service == 'runpod':
            try:
                r = requests.post('https://api.runpod.io/graphql', headers={'Authorization': f'Bearer {key}'}, json={'query': 'query { myself { clientBalance } }'}, timeout=8)
                if r.status_code == 200 and 'data' in r.json():
                    bal = r.json().get('data', {}).get('myself', {}).get('clientBalance', 0.0)
                    self.send_json_response(200, {"success": True, "message": f"مفتاح RunPod متصل وصحيح! الرصيد المتاح: ${bal:.2f}"})
                else:
                    self.send_error_response(401, "مفتاح RunPod غير صالح.")
            except Exception as e:
                self.send_error_response(500, f"خطأ اتصال RunPod: {e}")
        else:

            self.send_json_response(200, {"success": True, "message": f"مفتاح {service} مسجل في الخزنة."})



    def _translate_text_to_english(self, text, mode='image'):
        # Cross-Lingual Semantic Transmutation - supports Arabic, French, Spanish, and English
        if not text:
            return text
        is_ar = bool(re.search(r'[؀-ۿ]', text))
        is_fr_or_es = bool(re.search(r'[àâäéèêëîïôöùûüçñáíóúÁÉÍÓÚÑÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]', text)) or any(w in text.lower().split() for w in ['plan', 'gros', 'homme', 'femme', 'pluie', 'nuit', 'plano', 'primer', 'mujer', 'hombre', 'lluvia', 'noche', 'coche'])
        if not (is_ar or is_fr_or_es):
            return text
        return _cross_lingual_cinematic_transmute(text, mode=mode)

    def _to_egyptian_phonetic_tts(self, text):
        """
        Converts Arabic text into phonetic Cairo Egyptian Colloquial (العامية المصرية القاهرية)
        so TTS engines pronounce Qaf as a glottal stop (همزة) in colloquial words,
        Thaa/Thal as Taa/Zay/Seen, and use natural Egyptian vowelization instead of Fusha.
        """
        if not text:
            return text
        s = text
        # 1. Multi-word and Fusha-to-Masri phrase replacements
        phrase_replacements = [
            ("ثلاثي الأبعاد", "ثري دي"),
            ("ثلاثية الأبعاد", "ثري دي"),
            ("سأقوم بـ", "هعمل "),
            ("سأقوم", "هعمل"),
            ("سنقوم بـ", "هنعمل "),
            ("سنقوم", "هنعمل"),
            ("قول لي", "أُولّي"),
            ("قولي لي", "أُولّي"),
            ("زي ما", "زَيّ ما"),
            ("على طول", "عَلَى طُول"),
            ("خطوة بخطوة", "خَطْوَة بخَطْوَة"),
            ("ميديم تو", "مِيدْيَم تُو"),
            ("كلوز أب", "كْلُوز أَب"),
            ("وايد شوت", "وَايْد شُوت"),
            ("ويب بان", "وِيب بَان"),
        ]
        for old, new in phrase_replacements:
            s = s.replace(old, new)

        # 2. Whole-word phonetic Cairo Egyptian replacements (Qaf -> Hamza, Thaa -> Taa/Seen, etc.)
        word_map = {
            "الآن": "دِلْوَأْتِي",
            "دلوقتي": "دِلْوَأْتِي",
            "الوقت": "الوَأْت",
            "وقت": "وَأْت",
            "فوراً": "عَلَى طُول",
            "فورا": "عَلَى طُول",
            "حسناً": "تَمَام",
            "حسنا": "تَمَام",
            "جداً": "جِدًّا",
            "جدا": "جِدًّا",
            "أيضاً": "كَمَان",
            "أيضا": "كَمَان",
            "هكذا": "كِدَه",
            "كده": "كِدَه",
            "لماذا": "لِيه",
            "ماذا": "إيه",
            "هذا": "دَه",
            "هذه": "دِي",
            "الذي": "الْلِي",
            "التي": "الْلِي",
            "اللي": "الْلِي",
            "ثانيتين": "سَانْيِتِين",
            "ثانية": "سَانْيَة",
            "الثانية": "السَّانْيَة",
            "ثاني": "تَانِي",
            "الثاني": "التَّانِي",
            "ثلاثة": "تَلَاتَة",
            "ثلاث": "تَلَت",
            "ممثل": "مُمَسِّل",
            "الممثل": "المُمَسِّل",
            "الممثلين": "المُمَسِّلِين",
            "قول": "أُول",
            "القطعات": "الأَطَعَات",
            "قطعات": "أَطَعَات",
            "القطعة": "الأَطْعَة",
            "قطعة": "أَطْعَة",
            "نقطع": "نِئْطَع",
            "اقطع": "إئْطَع",
            "يقطع": "يِئْطَع",
            "قطع": "أَطْع",
            "القريبة": "الأُرَيِّبَة",
            "قريبة": "أُرَيِّبَة",
            "القريب": "الأُرَيِّب",
            "قريب": "أُرَيِّب",
            "يقرب": "يِأَرَّب",
            "بيقرب": "بِيأَرَّب",
            "تتقرب": "تِتْأَرَّب",
            "قرب": "أَرَّب",
            "وقفلت": "وَأَفَلْت",
            "قفلت": "أَفَلْت",
            "قفلنا": "أَفَلْنَا",
            "نقفل": "نِأْفِل",
            "اقفل": "إأْفِل",
            "يقفل": "يِأْفِل",
            "قفل": "أَفْل",
            "ضيق": "ضَيَّأ",
            "ضيقة": "ضَيَّأَة",
            "الضيق": "الضَّيَّأ",
            "الضيقة": "الضَّيَّأَة",
            "واقف": "وَائِف",
            "واقفة": "وَائْفَة",
            "واقفين": "وَائْفِين",
            "يوقف": "يُؤَف",
            "توقف": "تُؤَف",
            "قاعد": "آعِد",
            "قاعدة": "آعْدَة",
            "قاعدين": "آعْدِين",
            "قدام": "أُدَّام",
            "قدامك": "أُدَّامَك",
            "قدامه": "أُدَّامُه",
            "أمام": "أُدَّام",
            "فوق": "فُوء",
            "قبل": "أَبْل",
            "تقدر": "تِئْدَر",
            "نقدر": "نِئْدَر",
            "أقدر": "أَئْدَر",
            "دقيقة": "دِئِيئَة",
            "دقايق": "دَآيِئ",
            "حقيقي": "حَئِيئِي",
            "الحقيقة": "الحَئِيئَة",
            "طريقة": "طَرِيئَة",
            "الطريقة": "الطَّرِيئَة",
            "يبقى": "يِبْأَى",
            "تبقى": "تِبْأَى",
            "هيبقى": "هَيِبْأَى",
            "هتبقى": "هَتِبْأَى",
            "بقى": "بَأَى",
            "سامعاك": "سَمْعَاك",
            "سمعاك": "سَمْعَاك",
            "معاك": "مَعَاك",
            "جاهزة": "جَاهْزَة",
            "حضرتك": "حَضْرِتَك",
            "لحضرتك": "لِحَضْرِتَك",
            "ظبطت": "ظَبَّطْت",
            "ظبطتلك": "ظَبَّطْتِلَك",
            "نظبط": "نِظَبَّط",
            "بالظبط": "بِالظَّبْط",
            "بالضبط": "بِالظَّبْط",
            "علشان": "عَلَشَان",
            "عشان": "عَشَان",
            "كويس": "كْوَيِّس",
            "عايز": "عَايِز",
            "عايزة": "عَايْزَة",
            "تحب": "تِحِبّ",
            "نجرب": "نِجَرَّب",
            "أستاذنا": "أُسْتَاذْنَا",
        }
        for w_old, w_new in word_map.items():
            s = re.sub(rf'(?<![\w\u0600-\u06FF]){re.escape(w_old)}(?![\w\u0600-\u06FF])', w_new, s)
        return s

    def _ensure_wav_bytes(self, raw_bytes, sample_rate=24000):
        import struct
        if not raw_bytes:
            return b""
        if raw_bytes[:4] == b'RIFF':
            return raw_bytes
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + len(raw_bytes),
            b'WAVE',
            b'fmt ',
            16,
            1,
            1,
            sample_rate,
            sample_rate * 2,
            2,
            16,
            b'data',
            len(raw_bytes)
        )
        return header + raw_bytes

    def handle_tts(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        raw_text = (qs.get('text', [''])[0] or '').strip()
        if not raw_text:
            self.send_error_response(400, "Text is required")
            return

        clean_text = re.sub(r'[*#_`]', '', raw_text).strip()
        voice_id = (qs.get('voice', ['auto'])[0] or 'auto').strip()
        is_arabic = bool(re.search(r'[؀-ۿ]', clean_text))
        lang = 'ar' if is_arabic else 'en'
        phonetic_text = self._to_egyptian_phonetic_tts(clean_text[:380]) if is_arabic else clean_text[:380]
        audio_data = None
        content_type = 'audio/mpeg'

        # 1. If a specific local Voice Studio actor (e.g. am_adam, piper_ar_kareem) was explicitly chosen:
        if voice_id not in ('auto', '', 'salma', 'ar-EG-SalmaNeural', 'en-US-JennyNeural', 'cindy-eg'):
            try:
                import cindy_local_tts
                local_wav = cindy_local_tts.synthesize(clean_text[:400], voice_id=voice_id)
                if local_wav and len(local_wav) >= 1000:
                    self.send_response(200)
                    self.send_header('Content-Type', 'audio/wav')
                    self.send_header('Content-Length', str(len(local_wav)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(local_wav)
                    return
            except Exception as e:
                print("[Local TTS Explicit Voice Warning]", e)

        # 2. Primary Voice for Cindy (Arabic): Google Gemini Native TTS (Aoede - 100% Authentic Cairo Egyptian Colloquial)
        if is_arabic:
            secrets = load_secrets()
            gemini_key = secrets.get('gemini_api_key', '').strip()
            if gemini_key:
                for tts_model in ('gemini-3.8-flash-lite-tts', 'gemini-2.5-flash-preview-tts'):
                    try:
                        g_tts_url = f"https://generativelanguage.googleapis.com/v1beta/models/{tts_model}:generateContent?key={gemini_key}"
                        tts_prompt = (
                            f"Speak in a warm, natural Cairo Egyptian colloquial accent (Masri): {phonetic_text}"
                        )
                        tts_body = {
                            "contents": [{"parts": [{"text": tts_prompt}]}],
                            "generationConfig": {
                                "responseModalities": ["AUDIO"],
                                "speechConfig": {
                                    "voiceConfig": {
                                        "prebuiltVoiceConfig": {"voiceName": "Aoede"}
                                    }
                                }
                            }
                        }
                        g_resp = requests.post(g_tts_url, json=tts_body, timeout=9)
                        if g_resp.status_code == 200:
                            inl = (
                                g_resp.json()
                                .get("candidates", [{}])[0]
                                .get("content", {})
                                .get("parts", [{}])[0]
                                .get("inlineData", {})
                            )
                            b64_aud = inl.get("data", "")
                            if b64_aud:
                                raw_aud = base64.b64decode(b64_aud)
                                if len(raw_aud) > 1000:
                                    wav_bytes = self._ensure_wav_bytes(raw_aud, sample_rate=24000)
                                    self.send_response(200)
                                    self.send_header('Content-Type', 'audio/wav')
                                    self.send_header('Content-Length', str(len(wav_bytes)))
                                    self.send_header('Access-Control-Allow-Origin', '*')
                                    self.send_header('Cache-Control', 'public, max-age=86400')
                                    self.end_headers()
                                    self.wfile.write(wav_bytes)
                                    return
                    except Exception as e:
                        print(f"[Gemini Egyptian TTS {tts_model} Warning]", e)

        # 3. Multi-Lingual Studio Neural Voices (Arabic, English, French, Spanish)
        req_lang = (qs.get('lang', ['auto'])[0] or 'auto').strip().lower()
        if req_lang == 'auto':
            if is_arabic:
                req_lang = 'ar'
            elif bool(re.search(r'[àâäéèêëîïôöùûüç]', clean_text)):
                req_lang = 'fr'
            elif bool(re.search(r'[ñáíóú]', clean_text)):
                req_lang = 'es'
            else:
                req_lang = 'en'

        voice_map = {
            'ar': 'ar-EG-SalmaNeural',
            'en': 'en-US-JennyNeural',
            'fr': 'fr-FR-DeniseNeural',
            'es': 'es-ES-ElviraNeural'
        }
        chosen_voice = voice_map.get(req_lang, 'ar-EG-SalmaNeural' if is_arabic else 'en-US-JennyNeural')

        try:
            import edge_tts
            voice = chosen_voice
            async def _run():
                comm = edge_tts.Communicate(phonetic_text, voice, rate="+4%", pitch="+0Hz")
                buf = io.BytesIO()
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        buf.write(chunk["data"])
                return buf.getvalue()
            audio_data = asyncio.run(_run())
        except Exception as e:
            print("[Edge Neural TTS Warning]", e)

        # 3. Fal.ai Unified Audio / Voice Pipeline (Zero standalone ElevenLabs key needed)

        # 4. Fallback to high-quality Arabic/English Neural voice (NEVER fallback to robotic Google Translate)
        if not audio_data or len(audio_data) < 500:
            for fb_voice in (['ar-SA-ZariyahNeural', 'ar-DZ-AminaNeural'] if is_arabic else ['en-US-AriaNeural']):
                try:
                    import edge_tts
                    async def _run_fb():
                        comm = edge_tts.Communicate(phonetic_text, fb_voice, rate="+4%", pitch="+0Hz")
                        buf = io.BytesIO()
                        async for chunk in comm.stream():
                            if chunk["type"] == "audio":
                                buf.write(chunk["data"])
                        return buf.getvalue()
                    audio_data = asyncio.run(_run_fb())
                    if audio_data and len(audio_data) >= 500:
                        break
                except Exception as e:
                    print(f"[Edge Neural TTS Fallback {fb_voice} Warning]", e)

        if audio_data and len(audio_data) >= 500:
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Content-Length', str(len(audio_data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            self.wfile.write(audio_data)
            return

        self.send_error_response(500, "TTS generation failed")

    def handle_latest_blender_guide(self):
        b_dir = os.path.join(OUTPUTS_DIR, "blender_guides")
        if not os.path.exists(b_dir):
            self.send_json_response(200, {"success": True, "has_guide": False, "message": "لم يتم تصدير أي توجيه أو معاينة ثلاثية الأبعاد بعد"})
            return

        result_json_path = os.path.join(b_dir, "latest_previs_result.json")
        engine_result = {}
        if os.path.exists(result_json_path):
            try:
                with open(result_json_path, "r", encoding="utf-8") as fh:
                    engine_result = json.load(fh)
            except Exception:
                engine_result = {}

        mp4_files = [f for f in os.listdir(b_dir) if f.endswith(".mp4")]
        video_url = engine_result.get("video_url", "")
        has_video = bool(video_url)
        if not has_video and mp4_files:
            mp4_files.sort(key=lambda x: os.path.getmtime(os.path.join(b_dir, x)), reverse=True)
            video_url = f"/outputs/blender_guides/{mp4_files[0]}"
            has_video = True

        engine_stills = engine_result.get("stills", [])
        stills = [f for f in os.listdir(b_dir) if f.endswith(".jpg") and "depth" not in f.lower()]
        stills.sort(key=lambda x: os.path.getmtime(os.path.join(b_dir, x)), reverse=True)

        if engine_stills:
            rgb_url = engine_stills[-1].get("url", "") or (f"/outputs/blender_guides/{stills[0]}" if stills else "")
            storyboard_urls = [s.get("url") for s in engine_stills if s.get("url")]
        else:
            rgb_url = f"/outputs/blender_guides/{stills[0]}" if stills else ""
            storyboard_urls = [f"/outputs/blender_guides/{f}" for f in stills[:6]]

        depth_files = [f for f in os.listdir(b_dir) if "depth" in f.lower() and f.endswith(".jpg")]
        depth_url = f"/outputs/blender_guides/{depth_files[0]}" if depth_files else rgb_url

        meta = engine_result.get("meta", {})
        if not meta:
            meta = {
                "lens_focal_length_mm": engine_result.get("lens_focal_length_mm", 50.0),
                "frame": engine_result.get("frame", 192),
                "duration_sec": engine_result.get("duration_sec", 8.0),
                "resolution": [960, 540],
                "shot_type": engine_result.get("title", "3D Pre-vis Scene")
            }

        self.send_json_response(200, {
            "success": True,
            "has_guide": bool(rgb_url or has_video),
            "has_video": has_video,
            "video_url": video_url,
            "rgb_url": rgb_url,
            "depth_url": depth_url,
            "meta": meta,
            "storyboard": storyboard_urls,
            "stills_detail": engine_stills
        })

    def handle_generate_previs(self, payload):
        import subprocess
        blender_exe = r"D:\Blender\blender.exe"
        script_path = os.path.join(BASE_DIR, "cindy_previs_engine.py")
        b_dir = os.path.join(OUTPUTS_DIR, "blender_guides")
        os.makedirs(b_dir, exist_ok=True)
        spec_path = os.path.join(b_dir, "current_previs_spec.json")

        if not os.path.exists(blender_exe):
            self.send_error_response(500, f"Blender executable not found at {blender_exe}")
            return

        incoming_spec = payload.get("previs_spec") or payload.get("spec")
        if incoming_spec and isinstance(incoming_spec, dict):
            try:
                with open(spec_path, "w", encoding="utf-8") as fh:
                    json.dump(incoming_spec, fh, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[PREVIS] Warning saving incoming spec: {e}")

        try:
            cmd = [blender_exe, "--background", "--python", script_path]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if proc.returncode != 0:
                self.send_error_response(500, f"Blender render error: {proc.stderr[:300]}")
                return

            self.handle_latest_blender_guide()
        except Exception as e:
            self.send_error_response(500, f"Previs generation failed: {str(e)}")


    def _download_and_extract_reel(self, url):
        """
        Downloads a reel/short/video from Instagram, TikTok, YouTube Shorts, or direct video URL,
        saves it in outputs/reels/, and extracts keyframes (Start, Middle, Peak, End) for cinematic analysis.
        """
        import yt_dlp
        reels_dir = os.path.join(OUTPUTS_DIR, "reels")
        os.makedirs(reels_dir, exist_ok=True)
        ts_id = int(time.time())
        out_template = os.path.join(reels_dir, f"reel_{ts_id}.%(ext)s")

        # 1. Direct MP4 check
        if url.lower().endswith(('.mp4', '.mov', '.webm', '.mkv')):
            try:
                import urllib.request
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                mp4_path = os.path.join(reels_dir, f"reel_{ts_id}.mp4")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    with open(mp4_path, "wb") as f_out:
                        f_out.write(resp.read())
                return self._process_downloaded_reel_file(mp4_path, f"/outputs/reels/reel_{ts_id}.mp4")
            except Exception as e:
                print(f"[Direct Video Download Warning]: {e}")

        # 2. yt-dlp downloader
        ydl_opts = {
            'outtmpl': out_template,
            'format': 'mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 80 * 1024 * 1024, # 80MB max
            'socket_timeout': 15,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # Ensure actual extension if converted
                if not os.path.exists(filename):
                    base_no_ext = os.path.splitext(filename)[0]
                    for candidate in [f"{base_no_ext}.mp4", f"{base_no_ext}.mkv", f"{base_no_ext}.webm"]:
                        if os.path.exists(candidate):
                            filename = candidate
                            break
                if os.path.exists(filename):
                    rel_url = f"/outputs/reels/{os.path.basename(filename)}"
                    return self._process_downloaded_reel_file(filename, rel_url)
        except Exception as e:
            print(f"[yt-dlp Reel Download Warning]: {e}")
        return None

    def _process_downloaded_reel_file(self, video_path, video_url):
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"video_url": video_url, "frames_b64": [], "composite_b64": "", "duration": 0}

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        duration = round(total_frames / max(fps, 1.0), 1)

        # Pick 3 key moments: 15% (Start/Setup), 50% (Mid/Climax), 85% (Ending/Framing)
        fractions = [0.15, 0.50, 0.85] if total_frames > 10 else [0.5]
        frames = []
        for frac in fractions:
            f_idx = int(total_frames * frac)
            cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
            ret, frame = cap.read()
            if ret and frame is not None:
                # Resize to standard analysis resolution (320x180)
                small = cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA)
                frames.append(small)
        cap.release()

        composite_b64 = ""
        if frames:
            import numpy as np
            # Stitch horizontally side-by-side
            composite = np.hstack(frames)
            _, buf = cv2.imencode('.jpg', composite, [cv2.IMWRITE_JPEG_QUALITY, 80])
            composite_b64 = "data:image/jpeg;base64," + base64.b64encode(buf).decode('ascii')

        return {
            "video_url": video_url,
            "composite_b64": composite_b64,
            "duration": duration,
            "frames_count": len(frames)
        }

    def handle_chat(self, payload):
        """
        Cindy Chat Assistant, 1st Assistant Director (1st AD) & 3D Pre-vis Architect:
        Dedicated to serving The Film Director (أستاذنا المخرج).
        Converses naturally, NEVER gets stuck on an old scene, and generates a fresh or updated
        parametric 3D Pre-vis spec strictly based on what the Director is saying right now.
        Powered by Google Gemini 3.5 Flash (Zero Fal.ai cost).
        """
        user_msg = (payload.get('message') or '').strip()
        history = payload.get('history', [])
        reset_scene = bool(payload.get('reset_scene', False))

        # --- REEL / SHORT / VIDEO URL AUTO-DOWNLOAD & ANALYSIS ---
        reel_info = None
        extracted_urls = re.findall(r'https?://[^\s<>"\'`]+', user_msg)
        is_reel_link = False
        if extracted_urls:
            first_url = extracted_urls[0]
            if any(domain in first_url.lower() for domain in ['instagram.com', 'tiktok.com', 'youtube.com/shorts', 'youtu.be', 'facebook.com', 'fb.watch', 'vimeo.com', '.mp4', '.mov', '.webm']):
                is_reel_link = True
                try:
                    reel_info = self._download_and_extract_reel(first_url)
                except Exception as ex:
                    print(f"[Reel Auto-download Exception]: {ex}")
        current_model = payload.get('current_model') or payload.get('model') or 'Wan 2.1 (Alibaba 14B)'
        current_mode = payload.get('current_mode') or payload.get('mode') or 'video'
        aspect_ratio = payload.get('aspect_ratio', '16:9')
        app_lang = (payload.get('lang') or payload.get('app_lang') or 'ar').strip().lower()

        if not user_msg:
            self.send_error_response(400, "Message is required")
            return

        secrets = load_secrets()
        gemini_key = secrets.get('gemini_api_key', '').strip()

        b_dir = os.path.join(OUTPUTS_DIR, "blender_guides")
        os.makedirs(b_dir, exist_ok=True)
        spec_path = os.path.join(b_dir, "current_previs_spec.json")

        if reset_scene and os.path.exists(spec_path):
            try:
                os.remove(spec_path)
            except Exception:
                pass

        # Only include previous scene spec if there is active conversation history in this session!
        # This prevents Cindy from ever being "stuck" on an old pre-made scene when the Director starts talking.
        active_session_spec = None
        if isinstance(history, list) and len(history) > 1 and os.path.exists(spec_path) and not reset_scene:
            try:
                with open(spec_path, "r", encoding="utf-8") as fh:
                    active_session_spec = json.load(fh)
            except Exception:
                active_session_spec = None

        engine_rules = get_model_prompt_rules(current_model, current_mode)
        scene_context_str = (
            f"PREVIOUS SCENE SPEC IN THIS CONVERSATION (modify ONLY if the Director is asking to adjust it; if the Director is describing a new scene or new idea, build a brand-new spec from scratch!):\n{json.dumps(active_session_spec, ensure_ascii=False)}\n\n"
            if active_session_spec else
            "NO PREVIOUS SCENE IS LOCKED: Start fresh and listen 100% to what the Director wants right now. Do NOT mention or fall back to any old scene.\n\n"
        )

        sys_inst = (
            "You are Cindy (سيندي), an elite First Assistant Director (1st AD), Director of Photography (DP), "
            "and 3D Pre-vis Architect working directly with The Film Director (أستاذنا المخرج / أستاذ إيهاب).\n"
            "CRITICAL BEHAVIORAL RULES:\n"
            "1. NEVER be stuck on a previous or pre-made scene! Listen 100% to what the Director is saying right now.\n"
            "2. ADAPTIVE CONVERSATIONAL LANGUAGE & INTELLIGENT OVERRIDE HIERARCHY:\n"
            "   - DEFAULT BASELINE: Speak strictly in the UI language selected by the Director ('" + app_lang + "').\n"
            "   - INTENTIONAL DIRECTOR OVERRIDE (توقع وتجاوب ذكي):\n"
            "     * If the Director explicitly writes or asks in a different language than the UI (e.g. UI is in Arabic but the Director specifically addresses you in French or English, or asks 'Réponds-moi en français' / 'Can we speak English?'), adapt intelligently and reply in that requested language!\n"
            "     * Otherwise, ALWAYS maintain the selected UI language as the golden standard for all replies and spoken audio.\n"
            "   - Dialect styles per language:\n"
            "     * Arabic: Authentic Egyptian film set dialect (لغة البلاتوه في مصر: الكادر، الضربة الدرامية، الشاريو، العدسة، البلوكينج).\n"
            "     * English: Professional Hollywood 1st AD / DP film terminology.\n"
            "     * French: Professional French cinema terminology (découpage, cadrage, travelling, focale).\n"
            "     * Spanish: Professional Spanish cinema terminology (puesta en escena, encuadre, plano).\n"
            "3. EXPERT TOOL & MODEL RECOMMENDATION (ترشيح الأداة والموديل الأنسب بذكاء فوري):\n"
            "   - If the Director asks you to recommend a tool or model (e.g. 'اقترحيلي أداة مناسبة', 'ايه أحسن موديل للقطة دي', 'أعمل دي بإيه؟'):\n"
            "     * Direct and sharp recommendation: name the exact tool on Fal.ai, explain why it fits the shot/edit artistically, state its estimated cost clearly in Egyptian pounds/dollars, and give him the optimal prompt.\n"
            "     * Match criteria:\n"
            "       - قفل ملامح الشخصية مع لورا: MiniMax H3 I2V LoRA (~$0.25) أو LTX-2.3 22B Cinema LoRA (~$0.18).\n"
            "       - مزامنة الشفاه مع الصوت العربي: Sync Lipsync 2.0 (~$0.05 / 5s) أو MuseTalk (~$0.03).\n"
            "       - تحكم مداري وحركة كاميرا 3D: MiniMax Camera Controls (~$0.25) أو PixVerse V6 (~$0.18).\n"
            "       - درافت سريع ورخيص: Alibaba Wan 2.1 ($0.03) أو MiniMax H3 Lite ($0.04).\n"
            "       - نقل حركة الممثل من فيديو مرجعي: Kling Motion Control 1080p ($0.63).\n"
            "       - كادر بداية ونهاية: Kling 1.6 Pro I2V ($0.49) أو Luma Ray 2 I2V ($0.50).\n"
            "       - رفع جودة فيديو لـ 4K: Topaz Video Upscale (~$0.12).\n"
            "       - تعديل صور وكوادر مع لورا: FLUX 3 Klein Edit LoRA (~$0.012) أو Qwen Image 2512 LoRA (~$0.035).\n"
            "       - استكشاف ديكور ثلاثي الأبعاد لايف: LingBot-World 2.0 أو ABot-World-0.\n"
            "     * In `shot`, always set `suggested_model` to that recommended tool so he can execute it with 1-click!\n"
            "4. When should you set `should_render_previs`?\n"
            "   - If the Director is chatting, greeting, asking a question, complaining, or brainstorming without giving a concrete scene/adjustment yet: set `should_render_previs: false` and `has_shot: false`, and converse naturally with him like a smart human 1st AD!\n"
            "   - If the Director describes a scene, camera choreography, or asks for a specific adjustment to the current scene: set `should_render_previs: true`, break down the beats clearly in `reply`, and output the complete `previs_spec` matching his exact words!\n\n"
            "3D PRE-VIS ENGINE SCHEMA (`cindy_previs_engine.py`):\n"
            "- Stage coordinates: Room/Street X from -4.0 to +4.0, Y from -3.2 to +3.2, Floor Z=0.0.\n"
            "- Directorial Articulated Poses in actor keyframes: `STAND`, `WALK`, `KNEEL`, `CROUCH`, `SIT`.\n"
            "- Directorial Props supported: `dog` (animal proxy with body, head, snout, ears, 4 legs, tail), `streetlamp`, `car`, `chair`, `table`.\n"
            "- `environment.type`: `street`, `room`, `corridor`, `alley`.\n"
            "- `previs_spec` format:\n"
            "  {\n"
            '    "title": "Scene title",\n'
            '    "duration_sec": 7.0,\n'
            '    "fps": 24,\n'
            '    "environment": {"type": "street", "has_lamp_post": true},\n'
            '    "props": [\n'
            '      {"id": "dog_1", "type": "dog", "name": "Small Brown Dog", "pos": [0.0, -0.6, 0.0], "color": [0.45, 0.28, 0.15], "scale": 1.0, "look_at": [0.0, 0.5, 0.5]}\n'
            '    ],\n'
            '    "actors": [\n'
            '      {"id": "actor_1", "name": "Abdelaziz", "color": [0.85, 0.45, 0.2], "height_m": 1.82, "keyframes": [{"time_sec": 0.0, "pos": [0.0, 2.0, 0.0], "look_at": [0.0, -0.6, 0.3], "pose": "WALK"}, {"time_sec": 3.5, "pos": [0.0, 0.2, 0.0], "look_at": [0.0, -0.6, 0.25], "pose": "KNEEL"}]}\n'
            '    ],\n'
            '    "camera_beats": [\n'
            '      {"time_sec": 0.0, "name": "Beat 1", "framing": "FULL_BODY_ACTOR_1", "lens_mm": 35, "transition": "SMOOTH"},\n'
            '      {"time_sec": 3.5, "name": "Beat 2", "framing": "MEDIUM_TWO", "lens_mm": 40, "transition": "SMOOTH"}\n'
            '    ]\n'
            "  }\n"
            "- Supported `framing` values in `camera_beats`:\n"
            "  `BIRDS_EYE_OVERHEAD`, `HIGH_ANGLE_ON_ACTOR`, `LOW_ANGLE_HERO`, `FACE_CLOSE_UP`, `FACE_CLOSE_UP_ACTOR_2`, "
            "`EXTREME_CLOSE_UP_ACTOR_1`, `EXTREME_CLOSE_UP_ACTOR_2`, `DOOR_ENTRANCE`, `MEDIUM_TWO`, `TIGHT_MEDIUM_TWO`, "
            "`OTS_1_TO_2`, `OTS_2_TO_1`, `FULL_BODY_ACTOR_1`, `FULL_BODY_ACTOR_2`, `ORBIT_LEFT`, `ORBIT_RIGHT`, `WIDE_MASTER`, "
            "or `CUSTOM` (with `cam_pos: [x,y,z]` and `look_at: [x,y,z]`).\n"
            "- `transition` in `camera_beats`: `SMOOTH` (continuous camera motion), `WHIP` (fast whip pan), or `CUT` (instant 1-frame editorial cut).\n\n"
            f"{scene_context_str}"
            f"TARGET AI VIDEO/IMAGE MODEL RULES ({current_model}, mode={current_mode}):\n{engine_rules}\n\n"
            f"PRIMARY UI LANGUAGE: {app_lang.upper()} (Default unless the Director explicitly chose to write/request another language in their message)\n\n"
            "OUTPUT STRICT JSON ONLY:\n"
            "{\n"
            '  "reply": "Your natural, intelligent 1st AD response (matching the primary UI language, or matching the Director explicit language override if they wrote in another language)",\n'
            '  "should_render_previs": true or false,\n'
            '  "previs_spec": { ... complete 3D scene spec if should_render_previs is true, else null ... },\n'
            '  "has_shot": true or false,\n'
            '  "shot": {\n'
            '    "title": "Arabic shot title",\n'
            '    "notes": "Arabic directorial notes",\n'
            '    "prompt": "Master English cinematic prompt",\n'
            f'    "suggested_model": "{current_model}",\n'
            f'    "mode": "{current_mode}"\n'
            '  },\n'
            '  "voice_text": "Spoken concise version of your reply in 1-2 natural sentences strictly in the selected target language (' + app_lang + ')",\n'
            "}"
        )

        # If a Reel / Short was downloaded, perform visual analysis via Fal Any-LLM Vision to feed visual grounding into Cindy!
        reel_visual_analysis = ""
        if reel_info and reel_info.get("composite_b64"):
            try:
                secrets = load_secrets()
                fal_key = secrets.get('fal_api_key', '')
                if fal_key:
                    vision_prompt = (
                        "You are Cindy (1st AD and DP). Here is a 3-frame sequence (Start, Mid, End) extracted from a reel downloaded for the Director. "
                        "Critique: 1) Camera framing & movement 2) Lighting & mood 3) Visual storytelling elements. "
                        "State which model on Fal.ai (e.g. Wan 2.1, Kling Motion Control, PixVerse V6, MiniMax) can recreate or adapt this shot."
                    )
                    v_headers = {'Authorization': f'Key {fal_key}', 'Content-Type': 'application/json'}
                    v_body = {
                        'prompt': vision_prompt,
                        'image_url': reel_info['composite_b64'],
                        'model': 'google/gemini-2.5-flash-lite'
                    }
                    v_resp = requests.post('https://fal.run/fal-ai/any-llm/vision', headers=v_headers, json=v_body, timeout=14)
                    if v_resp.status_code == 200:
                        reel_visual_analysis = v_resp.json().get('output', '')
            except Exception as v_err:
                print(f"[Reel Vision Grounding Warning]: {v_err}")

        contents = []
        if isinstance(history, list):
            for h in history[-10:]:
                role = "user" if h.get("role") == "user" else "model"
                txt = (h.get("text") or "").strip()
                if txt and txt != user_msg:
                    contents.append({"role": role, "parts": [{"text": txt}]})

        augmented_user_msg = user_msg
        if reel_info and reel_info.get("video_url"):
            augmented_user_msg += (
                f"\n\n[نظام سيندي الذكي قام بتنزيل الفيديو/الريل بنجاح وعرضه على الشاشة: {reel_info['video_url']}]"
                f"\n[مدة الريل: {reel_info.get('duration', 0)} ثوان]"
            )
            if reel_visual_analysis:
                augmented_user_msg += (
                    f"\n[الفحص البصري لإطارات الريل (تحليل الكادرات والإضاءة وحركة الكاميرا):\n{reel_visual_analysis}\n]"
                    f"\nتوجيه لسيندي: اشرحي للمخرج ما تم استخراجه من هذا الريل فنياً وإخراجياً، واقترحي له خطة تنفيذية أو إعادة توليد لقطة مماثلة بالأدوات المتاحة!"
                )
        elif is_reel_link and not reel_info:
            augmented_user_msg += "\n\n[ملاحظة تقنية: تم محاولة تنزيل الرابط لكن المنصة تفرض تسجيل دخول أو الرابط خاص. اطلبي من المخرج رفع الفيديو يدوياً عبر زر 'رفع صورة / فيديو' إذا تعذر السحب المباشر]."

        contents.append({"role": "user", "parts": [{"text": augmented_user_msg}]})

        llm_parsed = None
        if gemini_key:
            for model_id in ["gemini-3.5-flash", "gemini-3.1-flash-lite"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={gemini_key}"
                    req_body = {
                        "systemInstruction": {"parts": [{"text": sys_inst}]},
                        "contents": contents,
                        "generationConfig": {
                            "temperature": 0.45,
                            "responseMimeType": "application/json",
                            "thinkingConfig": {"thinkingBudget": 0}
                        }
                    }
                    r = requests.post(url, json=req_body, timeout=22)
                    if r.status_code == 200:
                        resp_json = r.json()
                        cand_text = (
                            resp_json.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )
                        if cand_text:
                            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cand_text.strip(), flags=re.MULTILINE)
                            llm_parsed = json.loads(cleaned, strict=False)
                            break
                except Exception as e:
                    print(f"[CINDY-AD-LLM] {model_id} error: {e}")

        if llm_parsed and isinstance(llm_parsed, dict):
            should_render = bool(llm_parsed.get("should_render_previs", False))
            updated_spec = llm_parsed.get("previs_spec")
            if isinstance(updated_spec, dict) and (updated_spec.get("camera_beats") or updated_spec.get("beats")):
                try:
                    with open(spec_path, "w", encoding="utf-8") as fh:
                        json.dump(updated_spec, fh, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"[CINDY-AD-LLM] Error saving previs_spec: {e}")

            self.send_json_response(200, {
                "success": True,
                "reply": llm_parsed.get("reply") or "معاك يا أستاذنا المخرج، سامعاك وجاهزة لأي توجيه في المشهد.",
                "should_render_previs": should_render,
                "previs_spec": updated_spec if isinstance(updated_spec, dict) else None,
                "has_shot": bool(llm_parsed.get("has_shot", should_render)),
                "shot": llm_parsed.get("shot") if llm_parsed.get("has_shot", should_render) else None,
                "voice_text": llm_parsed.get("voice_text") or "أنا معاك يا أستاذنا وسامعة توجيهك.",
                "reel_video_url": reel_info.get("video_url") if reel_info else None,
                "reel_composite_b64": reel_info.get("composite_b64") if reel_info else None
            })
            return

        self.send_json_response(200, {
            "success": True,
            "reply": "أنا سامعاك يا أستاذنا المخرج ومعاك خطوة بخطوة. قول لي فكرة المشهد أو التعديل اللي تحب ننفذه دلوقتي.",
            "should_render_previs": False,
            "previs_spec": None,
            "has_shot": False,
            "shot": None,
            "voice_text": "أنا سامعاك يا أستاذنا المخرج ومعاك خطوة بخطوة."
        })

    def handle_translate_prompt(self, payload):

        text = str(payload.get('text', '')).strip()

        mode = payload.get('mode', 'image')

        if not text:

            self.send_json_response(200, {"success": True, "translated": "", "original": ""})

            return



        is_non_en = bool(re.search(r'[\u0600-\u06FFàâäéèêëîïôöùûüçñáíóúÁÉÍÓÚÑÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]', text)) or any(w in text.lower().split() for w in ['plan', 'gros', 'homme', 'femme', 'pluie', 'nuit', 'plano', 'primer', 'mujer', 'hombre', 'lluvia', 'noche', 'coche'])

        if not is_non_en:

            self.send_json_response(200, {

                "success": True,

                "translated": text,

                "original": text,

                "is_arabic": False

            })

            return



        translated_text = self._translate_text_to_english(text, mode=mode)

        self.send_json_response(200, {

            "success": True,

            "translated": translated_text,

            "original": text,

            "is_arabic": True

        })



    def handle_universal_execute(self, payload):
        if not payload.get('user_confirmed'):
            self.send_json_response(403, {
                "success": False,
                "error": "🛡️ حماية مالية: يتطلب تأكيداً يدوياً صريحاً من المخرج في الواجهة لتجنب أي خصم غير مقصود."
            })
            return

        service = payload.get('service', 'fal')

        # Robust extraction supporting mode/model/endpoint keys from index.html
        endpoint = payload.get('endpoint') or payload.get('model') or 'fal-ai/flux/schnell'

        prompt = payload.get('prompt', '')

        aspect_ratio = payload.get('aspect_ratio', 'landscape_16_9')

        raw_mode = (payload.get('mode') or payload.get('type') or '').strip().lower()

        # Enforce video/image detection by model endpoint FIRST so video models never get treated as static images
        video_indicators = ['ltx', 'wan', 'kling', 'minimax', 'hailuo', 'seedance', 'veo', 'ray-2', 'luma', 'runway', 'cogvideo', 'svd', 'pixverse', 'video', 'lipsync', 'musetalk', 'topaz']
        image_indicators = ['flux', 'banana', 'qwen-image', 'recraft', 'ideogram']
        if any(ind in endpoint.lower() for ind in video_indicators):
            model_type = 'video'
        elif any(ind in endpoint.lower() for ind in image_indicators):
            model_type = 'image'
        elif raw_mode in ('video', 'fal_video', 'i2v', 'v2v'):
            model_type = 'video'
        elif raw_mode in ('image', 'fal_image', 't2i'):
            model_type = 'image'
        else:
            model_type = payload.get('type', 'image')

        custom_params = payload.get('params', {})



        # Ensure prompt is in cinematic English via Cross-Lingual Transmutation

        prompt = self._translate_text_to_english(prompt, mode=model_type)



        secrets = load_secrets()



        # GOOGLE IMAGEN 3 DIRECT EXECUTION WITH RESILIENT FALLBACK

        if service == 'google' or 'imagen' in endpoint or 'gemini' in endpoint:

            if model_type == 'video':

                self.send_error_response(400, "نماذج Google Flow للفيديو (Veo / Omni) تعمل عبر «جسر فلو» باشتراكك: فعّل الإضافة وافتح تبويب Flow. أو اختر نسخة «عبر Fal» من القائمة (تُحتسب من رصيد Fal).")

                return

            gemini_key = secrets.get('gemini_api_key', '')

            fal_key = secrets.get('fal_api_key', '')

            sample_count = min(max(int(custom_params.get('num_images', 1)), 1), 4)



            # Fast path for Google Nano Banana / Nano Banana Pro (supports 1..4 batch images & exact aspect ratios natively)

            if fal_key and 'banana' in endpoint.lower():

                headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}

                ar_map_g = {'landscape_16_9': '16:9', 'portrait_9_16': '9:16', 'square_hd': '1:1', 'landscape_21_9': '21:9',

                            '16:9': '16:9', '9:16': '9:16', '1:1': '1:1', '21:9': '21:9'}

                ar_g = ar_map_g.get(aspect_ratio, '16:9')

                nb_ep = "fal-ai/nano-banana-pro" if "pro" in endpoint.lower() else "fal-ai/nano-banana"

                nb_body = {'prompt': prompt, 'aspect_ratio': ar_g, 'num_images': sample_count, 'output_format': 'jpeg'}

                try:

                    nb_res = requests.post(f"https://fal.run/{nb_ep}", headers=headers, json=nb_body, timeout=60)

                    if nb_res.status_code == 200:

                        data = nb_res.json()

                        imgs = data.get('images', [])

                        images_list = [{"url": im.get('url', '')} for im in imgs if im.get('url')]

                        if images_list:

                            self.send_json_response(200, {

                                "success": True,

                                "media_type": "image",

                                "url": images_list[0]['url'],

                                "images": images_list,

                                "endpoint": "Google Nano Banana Pro" if "pro" in nb_ep else "Google Nano Banana",

                                "prompt": prompt,

                                "message": f"تم توليد {len(images_list)} صور بنجاح عبر محرك Google Nano Banana!"

                            })

                            return

                except Exception:

                    pass



            google_success = False

            if gemini_key:

                # Attempt modern Gemini image generation or Imagen endpoints

                for test_model in ['gemini-3.1-flash-image-preview', 'gemini-3-pro-image', 'gemini-2.5-flash-image']:

                    try:

                        g_url = f"https://generativelanguage.googleapis.com/v1beta/models/{test_model}:generateContent"

                        req_body = {

                            "contents": [{"parts": [{"text": f"Generate a high resolution cinematic photograph: {prompt}"}]}]

                        }

                        r = requests.post(g_url, headers={"x-goog-api-key": gemini_key}, json=req_body, timeout=20)

                        if r.status_code == 200:

                            data = r.json()

                            candidates = data.get('candidates', [])

                            if candidates:

                                parts = candidates[0].get('content', {}).get('parts', [])

                                images_list = []

                                ts = int(time.time())

                                for idx, p in enumerate(parts):

                                    if 'inlineData' in p and 'data' in p['inlineData']:

                                        b64 = p['inlineData']['data']

                                        fname = f"google_gemini_{ts}_{idx+1}.jpg"

                                        fpath = os.path.join(OUTPUTS_DIR, fname)

                                        with open(fpath, "wb") as fh:

                                            fh.write(base64.b64decode(b64))

                                        images_list.append({"url": f"/outputs/{fname}"})

                                if images_list:

                                    self.send_json_response(200, {

                                        "success": True,

                                        "media_type": "image",

                                        "url": images_list[0]["url"],

                                        "images": images_list,

                                        "endpoint": f"Google {test_model}",

                                        "prompt": prompt,

                                        "message": f"تم توليد {len(images_list)} صور بنجاح عبر {test_model}!"

                                    })

                                    return

                    except Exception:

                        pass



            # If Google API quota exceeded (429) or deprecated (404), seamlessly use Nano Banana / FLUX on Fal

            if fal_key:

                headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}

                ar_map_g = {'landscape_16_9': '16:9', 'portrait_9_16': '9:16', 'square_hd': '1:1', 'landscape_21_9': '21:9',

                            '16:9': '16:9', '9:16': '9:16', '1:1': '1:1', '21:9': '21:9'}

                ar_g = ar_map_g.get(aspect_ratio, '16:9')

                if 'banana' in endpoint.lower():

                    nb_ep = "fal-ai/nano-banana-pro" if "pro" in endpoint.lower() else "fal-ai/nano-banana"

                    nb_body = {'prompt': prompt, 'aspect_ratio': ar_g, 'num_images': sample_count, 'output_format': 'jpeg'}

                    try:

                        nb_res = requests.post(f"https://fal.run/{nb_ep}", headers=headers, json=nb_body, timeout=60)

                        if nb_res.status_code == 200:

                            data = nb_res.json()

                            imgs = data.get('images', [])

                            images_list = [{"url": im.get('url', '')} for im in imgs if im.get('url')]

                            if images_list:

                                self.send_json_response(200, {

                                    "success": True,

                                    "media_type": "image",

                                    "url": images_list[0]['url'],

                                    "images": images_list,

                                    "endpoint": "Google Nano Banana (توليد مباشر)",

                                    "prompt": prompt,

                                    "message": f"تم توليد {len(images_list)} صور بنجاح عبر محرك Google Nano Banana!"

                                })

                                return

                    except Exception:

                        pass



                req_body = {

                    'prompt': prompt,

                    'image_size': 'landscape_16_9' if ('16_9' in aspect_ratio or '16:9' in aspect_ratio) else 'square',

                    'num_images': sample_count,

                    'enable_safety_checker': False

                }

                try:

                    res = requests.post("https://fal.run/fal-ai/flux/schnell", headers=headers, json=req_body, timeout=60)

                    if res.status_code == 200:

                        data = res.json()

                        imgs = data.get('images', [])

                        images_list = [{"url": im.get('url', '')} for im in imgs if im.get('url')]

                        primary_url = images_list[0]['url'] if images_list else ''

                        self.send_json_response(200, {

                            "success": True,

                            "media_type": "image",

                            "url": primary_url,

                            "images": images_list,

                            "endpoint": "FLUX.1 Schnell (بديل سينمائي تلقائي - نظراً لقيود كوتا جوجل)",

                            "prompt": prompt,

                            "message": f"تم توليد {len(images_list)} صور فورياً بدقة سينمائية فائقة عبر FLUX.1!"

                        })

                        return

                    else:

                        self.send_error_response(res.status_code, f"خطأ في توليد البديل: {res.text[:200]}")

                        return

                except Exception as e:

                    self.send_error_response(500, f"خطأ في التنفيذ: {str(e)}")

                    return



            self.send_error_response(400, "لم نتمكن من التوليد: مفتاح جوجل تجاوز الحصة المجانية (Quota 429)، ومفتاح Fal.ai غير متوفر كبديل.")

            return



        # FAL.AI DIRECT EXECUTION

        fal_key = secrets.get('fal_api_key', '')

        if not fal_key:

            self.send_error_response(400, "مفتاح Fal.ai غير متوفر. يرجى إدخاله في الخزنة.")

            return



        headers = {

            "Authorization": f"Key {fal_key}",

            "Content-Type": "application/json"

        }



        # Map the Studio's display names to REAL Fal endpoints (verified to exist on the queue API).

        # Note: Fal hosts the closest published versions (e.g. Seedance v1 Pro, Kling 2.5 Turbo Pro, Hailuo 02 Pro).

        endpoint_mapping = {

            "flux-3-max-i2v": "blackforestlabs/flux-3-max/image-to-video",

            "Flux 3 Max Image-to-Video": "blackforestlabs/flux-3-max/image-to-video",

            "blackforestlabs/flux-3-max/image-to-video": "blackforestlabs/flux-3-max/image-to-video",
            "FLUX 3 Max Image-to-Video": "blackforestlabs/flux-3-max/image-to-video",
            "fal-ai/blackforestlabs/flux-3-max/image-to-video": "blackforestlabs/flux-3-max/image-to-video",
            "lightricks/ltx-2.5/reframe": "lightricks/ltx-2.5/reframe",
            "Lightricks LTX-2.5 Reframe": "lightricks/ltx-2.5/reframe",
            "fal-ai/lightricks/ltx-2.5/reframe": "lightricks/ltx-2.5/reframe",

            "mischief-1-i2v": "tbc/mischief-1/image-to-video",

            "Mischief-1 Image-to-Video": "tbc/mischief-1/image-to-video",

            "tbc/mischief-1/image-to-video": "tbc/mischief-1/image-to-video",

            "minimax-h3-turbo": "minimax/h3-max-turbo/reference-to-video",

            "MiniMax H3 Max Turbo": "minimax/h3-max-turbo/reference-to-video",

            "minimax/h3-max-turbo/reference-to-video": "minimax/h3-max-turbo/reference-to-video",

            "minimax-h3-lite": "fal-ai/minimax-video",

            "MiniMax H3 Lite": "fal-ai/minimax-video",

            "hunyuan-video": "fal-ai/hunyuan-video-image-to-video",

            "Tencent HunyuanVideo": "fal-ai/hunyuan-video-image-to-video",

            "hunyuan-video-i2v": "fal-ai/hunyuan-video/image-to-video",

            "cogvideox-5b": "fal-ai/cogvideox-5b",

            "CogVideoX-5B (THUDM)": "fal-ai/cogvideox-5b",

            "cogvideox-i2v": "fal-ai/cogvideox-5b/image-to-video",

            "wan-2.1": "fal-ai/wan-t2v",
            "Wan 2.1 Image-to-Video": "fal-ai/wan-i2v",
            "Wan 2.2 Image-to-Video": "fal-ai/wan-i2v",
            "Wan 2.2 (Alibaba 14B)": "fal-ai/wan-t2v",
            "wan-2.2": "fal-ai/wan-i2v",
            "Wan 2.1 (Alibaba 14B)": "fal-ai/wan-t2v",
            "Wan 3.0 (Alibaba)": "fal-ai/wan-t2v",
            "Kling Motion Control (1080p)": "fal-ai/kling-video/v3/standard/motion-control",
            "kling-motion-control": "fal-ai/kling-video/v3/standard/motion-control",
            "Kling 1.6 Pro Image-to-Video": "fal-ai/kling-video/v1.6/pro/image-to-video",
            "Luma Ray 2 Image-to-Video": "fal-ai/luma-dream-machine/ray-2/image-to-video",
            "Kling O1 Video-to-Video Edit": "fal-ai/kling-video/o1/video-to-video/edit",
            "Luma Ray 2 Modify": "fal-ai/luma-dream-machine/ray-2/modify",

            "kling-standard": "fal-ai/kling-video/v1/standard/text-to-video",

            "Kling AI Standard": "fal-ai/kling-video/v1/standard/text-to-video",

            "kling-3-pro": "fal-ai/kling-video/v1.5/pro/text-to-video",

            "Kling 4 / 3.0 Pro": "fal-ai/kling-video/v1.5/pro/text-to-video",

            "minimax-h3": "fal-ai/minimax/video-01",

            "MiniMax H3 Max": "fal-ai/minimax/video-01",

            "luma-ray2": "fal-ai/luma-dream-machine",

            "Luma Ray 2 & Dream Machine": "fal-ai/luma-dream-machine",

            "ByteDance Seedance 2.5": "bytedance/seedance-2.5/reference-to-video",
            "Seedance Image-to-Video": "bytedance/seedance-2.5/image-to-video",
            "bytedance/seedance-2.5": "bytedance/seedance-2.5/reference-to-video",
            "seedance-2.5": "bytedance/seedance-2.5/reference-to-video",
            "seedance": "fal-ai/bytedance/seedance/v1/pro/text-to-video",
            "Runway Gen-3 Alpha": "fal-ai/runway/gen3/turbo",
            "Runway Gen-3 I2V": "fal-ai/runway-gen3/turbo/image-to-video",
            "runway-gen3": "fal-ai/runway/gen3/turbo",

            "Google Veo 3.1 Cinematic": "fal-ai/veo3.1/image-to-video",

            "Google Veo 3.1 Fast": "fal-ai/veo3.1/image-to-video",

            "Google Veo 3.1 Lite": "fal-ai/veo3.1/image-to-video",

            "Gemini Omni Flash 1.1": "fal-ai/veo3.1/image-to-video",

            "flux-3-max": "fal-ai/flux/schnell",

            "flux-schnell": "fal-ai/flux/schnell",

            "flux-dev": "fal-ai/flux/dev",

            "flux-ultra": "fal-ai/flux-pro/v1.1-ultra",

            "recraft-v3": "fal-ai/recraft-v3",
            "fal-ai/qwen-image-edit-2511": "fal-ai/qwen-image-edit-2511",
            "qwen-image-edit-2511": "fal-ai/qwen-image-edit-2511",
            "Qwen-Image-Edit-2511": "fal-ai/qwen-image-edit-2511",
            "qwen-image-edit": "fal-ai/qwen-image-edit-2511",
            "qwen": "fal-ai/qwen-image-edit-2511",

            "ideogram-v2": "fal-ai/ideogram/v2",

            "mmaudio": "fal-ai/mmaudio-v2",
            "fal-ai/mmaudio-v2": "fal-ai/mmaudio-v2",

            # Lip-Sync & Dialogue Models
            "fal-ai/sync-lipsync": "fal-ai/sync-lipsync",
            "fal-ai/sync-lipsync/v2": "fal-ai/sync-lipsync/v2",
            "Sync Lipsync 2.0": "fal-ai/sync-lipsync",
            "fal-ai/musetalk": "fal-ai/musetalk",
            "MuseTalk LipSync": "fal-ai/musetalk",

            # Video + Actor LoRA Models
            "minimax/h3/image-to-video/lora": "minimax/h3/image-to-video/lora",
            "MiniMax H3 I2V LoRA": "minimax/h3/image-to-video/lora",
            "fal-ai/ltx-2.3-quality/image-to-video/lora": "fal-ai/ltx-2.3-quality/image-to-video/lora",
            "fal-ai/ltx-2.3-22b/image-to-video/lora": "fal-ai/ltx-2.3-22b/image-to-video/lora",
            "LTX-2.3 22B Cinema LoRA": "fal-ai/ltx-2.3-22b/image-to-video/lora",
            "fal-ai/ltx-2.3-22b/distilled/image-to-video/lora": "fal-ai/ltx-2.3-22b/distilled/image-to-video/lora",
            "LTX-2.3 Distilled Fast LoRA": "fal-ai/ltx-2.3-22b/distilled/image-to-video/lora",
            "fal-ai/ltxv-13b-098-distilled/image-to-video": "fal-ai/ltxv-13b-098-distilled/image-to-video",
            "fal-ai/ltx-video-13b-distilled/image-to-video": "fal-ai/ltx-video-13b-distilled/image-to-video",

            # Image & Edit LoRA Models
            "fal-ai/lora": "fal-ai/flux-lora",
            "fal-ai/flux-lora": "fal-ai/flux-lora",
            "fal-ai/krea-2/turbo/lora": "fal-ai/krea-2/turbo/lora",
            "Krea 2 Turbo LoRA": "fal-ai/krea-2/turbo/lora",
            "blackforestlabs/flux-3/klein/edit-image/lora": "blackforestlabs/flux-3/klein/edit-image/lora",
            "FLUX 3 Klein Edit LoRA": "blackforestlabs/flux-3/klein/edit-image/lora",
            "fal-ai/qwen-image-2512/lora": "fal-ai/qwen-image-2512/lora",
            "Qwen Image 2512 LoRA": "fal-ai/qwen-image-2512/lora",

            # Video Upscalers & Camera Control
            "fal-ai/topaz/upscale-video": "fal-ai/topaz/upscale-video",
            "Topaz Video Upscale": "fal-ai/topaz/upscale-video",
            "fal-ai/minimax-video": "fal-ai/minimax-video",
            "MiniMax Camera Controls": "fal-ai/minimax-video",
            "fal-ai/pixverse/v6": "fal-ai/pixverse/v6",
            "PixVerse V6 Cinematic": "fal-ai/pixverse/v6",

            # Interactive World Models
            "robbyant/lingbot-world-2": "robbyant/lingbot-world-2",
            "meshy/t2.5/image-to-3d": "meshy/t2.5/image-to-3d",
            "meshy/t2/image-to-3d": "meshy/t2/image-to-3d",
            "Meshy 2.5 Image-to-3D": "meshy/t2.5/image-to-3d",
            "Meshy 2.0 Image-to-3D": "meshy/t2/image-to-3d",
            "tripo3d/h3.1/image-to-3d": "tripo3d/h3.1/image-to-3d",
            "Tripo H3.1 Image-to-3D": "tripo3d/h3.1/image-to-3d",
            "alibaba/abot-world-0": "alibaba/abot-world-0",

            "Google Nano Banana": "fal-ai/nano-banana",

            "Google Nano Banana Pro": "fal-ai/nano-banana-pro",

        }

        target_endpoint = endpoint_mapping.get(endpoint, endpoint)

        if not (target_endpoint.startswith('fal-ai/') or '/' in target_endpoint) or '..' in target_endpoint:

            self.send_error_response(400, f"النموذج غير مدعوم عبر Fal: {endpoint}")

            return



        ar_map = {'landscape_16_9': '16:9', 'portrait_9_16': '9:16', 'square_hd': '1:1', 'landscape_21_9': '21:9',

                  '16:9': '16:9', '9:16': '9:16', '1:1': '1:1', '21:9': '21:9'}

        ar = ar_map.get(aspect_ratio, '16:9')



        if model_type in ('3d', 'model3d') or 'image-to-3d' in target_endpoint:
            ref_img = (custom_params.get('image_url') or payload.get('image_url') or '').strip()
            if not ref_img:
                img_files = sorted([f for f in os.listdir(OUTPUTS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and 'depth' not in f.lower()],
                                   key=lambda x: os.path.getmtime(os.path.join(OUTPUTS_DIR, x)), reverse=True)
                if img_files:
                    ref_img = f"/outputs/{img_files[0]}"
            if not ref_img:
                self.send_error_response(400, "يتطلب تحويل 3D صورة مرجعية أولاً.")
                return
            cloud_img = self._resolve_media_for_fal(ref_img, fal_key)
            req_body = {'image_url': cloud_img}
            try:
                submit_url = f"https://queue.fal.run/{target_endpoint}"
                sub_res = requests.post(submit_url, headers=headers, json=req_body, timeout=30)
                if sub_res.status_code in [200, 201, 202]:
                    q_data = sub_res.json()
                    st_url = q_data.get('status_url')
                    resp_url = q_data.get('response_url')
                    res = sub_res
                    for _ in range(60):
                        time.sleep(3)
                        p = requests.get(st_url, headers=headers, timeout=15)
                        if p.status_code == 200 and p.json().get('status') == 'COMPLETED':
                            res = requests.get(resp_url, headers=headers, timeout=15)
                            break
                    if res.status_code == 200:
                        data = res.json()
                        model_file = data.get('model_file', {}) or data.get('model', {}) or {}
                        glb_url = model_file.get('url') if isinstance(model_file, dict) else (data.get('glb_url') or data.get('mesh_url') or '')
                        
                        # Seamless Auto-Download to local blender_guides for instant Blender Motion Retargeting
                        local_glb_path = ""
                        if glb_url:
                            try:
                                b_dir = os.path.join(OUTPUTS_DIR, "blender_guides")
                                os.makedirs(b_dir, exist_ok=True)
                                target_save = os.path.join(b_dir, "latest_tripo_actor.glb")
                                glb_req = requests.get(glb_url, timeout=45)
                                if glb_req.status_code == 200:
                                    with open(target_save, "wb") as f_glb:
                                        f_glb.write(glb_req.content)
                                    local_glb_path = "/outputs/blender_guides/latest_tripo_actor.glb"
                                    print(f"[TRIPO AUTO-BIND] Saved 3D actor mesh to {target_save} ({len(glb_req.content)} bytes)")
                            except Exception as dl_err:
                                print(f"[TRIPO AUTO-BIND] Warning downloading GLB: {dl_err}")

                        self.send_json_response(200, {
                            "success": True,
                            "media_type": "3d",
                            "glb_url": glb_url,
                            "local_glb_path": local_glb_path,
                            "url": glb_url,
                            "data": data,
                            "message": "تم تحويل الكادر إلى مجسم 3D وربطه آلياً بمحرك حركة بلندر!"
                        })
                        return
                    else:
                        self.send_error_response(res.status_code, f"خطأ Meshy 3D: {res.text[:300]}")
                        return
                else:
                    self.send_error_response(sub_res.status_code, f"فشل تقديم طلب 3D: {sub_res.text[:300]}")
                    return
            except Exception as e:
                self.send_error_response(500, f"خطأ استدعاء Meshy 3D: {str(e)}")
                return

        elif model_type == 'image':

            num_images = min(max(int(custom_params.get('num_images', 1)), 1), 4)

            if 'qwen' in target_endpoint:
                ref_img = custom_params.get('image_url') or payload.get('image_url') or payload.get('source_url') or ''
                if ref_img:
                    cloud_ref = self._resolve_media_for_fal(ref_img, fal_key)
                    req_body = {
                        'prompt': prompt,
                        'image_urls': [cloud_ref],
                        'num_images': num_images,
                        'output_format': 'jpeg'
                    }
                else:
                    req_body = {
                        'prompt': prompt,
                        'num_images': num_images,
                        'output_format': 'jpeg'
                    }
            elif 'nano-banana' in target_endpoint:

                req_body = {

                    'prompt': prompt,

                    'aspect_ratio': ar,

                    'num_images': num_images,

                    'output_format': 'jpeg'

                }

            else:

                req_body = {

                    'prompt': prompt,

                    'image_size': aspect_ratio,

                    'num_images': num_images,

                    'enable_safety_checker': False

                }

                # Attach LoRA parameters if present (for fal-ai/flux-lora or any image LoRA)
                lora_url = (custom_params.get('lora_url') or '').strip()
                loras_list = custom_params.get('loras') or []
                if not lora_url and loras_list and isinstance(loras_list, list):
                    lora_url = (loras_list[0].get('path') or loras_list[0].get('url') or '').strip()
                if lora_url:
                    scale = float(custom_params.get('scale') or custom_params.get('lora_scale', 1.0))
                    req_body['loras'] = [{'path': lora_url, 'scale': scale}]



            try:
                # Use queue API for flux-lora or long image tasks to avoid timeouts
                if 'lora' in target_endpoint:
                    submit_url = f"https://queue.fal.run/{target_endpoint}"
                    sub_res = requests.post(submit_url, headers=headers, json=req_body, timeout=30)
                    if sub_res.status_code in [200, 201, 202]:
                        q_data = sub_res.json()
                        st_url = q_data.get('status_url')
                        resp_url = q_data.get('response_url')
                        res = sub_res
                        for _ in range(40):
                            time.sleep(2.5)
                            p = requests.get(st_url, headers=headers, timeout=15)
                            if p.status_code == 200 and p.json().get('status') == 'COMPLETED':
                                res = requests.get(resp_url, headers=headers, timeout=15)
                                break
                    else:
                        res = sub_res
                else:
                    res = requests.post(f"https://fal.run/{target_endpoint}", headers=headers, json=req_body, timeout=60)

                if res.status_code == 200:

                    data = res.json()

                    imgs = data.get('images', [])

                    images_list = [{"url": im.get('url', '')} for im in imgs if im.get('url')]

                    primary_url = images_list[0]['url'] if images_list else ''

                    self.send_json_response(200, {

                        "success": True,

                        "media_type": "image",

                        "url": primary_url,

                        "images": images_list,

                        "endpoint": target_endpoint,

                        "prompt": prompt,

                        "message": f"تم توليد {len(images_list)} صور فورياً بواسطة {target_endpoint}!"

                    })

                else:

                    self.send_error_response(res.status_code, f"خطأ في التوليد: {res.text[:300]}")

            except Exception as e:

                self.send_error_response(500, f"Execution Error: {str(e)}")



        elif model_type == 'video':

            try:

                dur = int(str(custom_params.get('duration', '5')))

            except ValueError:

                dur = 5

            camera_motion = (custom_params.get('camera_motion') or '').strip()
            quality_mode = custom_params.get('quality_mode', 'master')

            # Professional negative prompt and camera motion injection
            enhanced_prompt = prompt
            if camera_motion and camera_motion != 'none':
                enhanced_prompt = f"{enhanced_prompt}, {camera_motion}"

            req_body = {'prompt': enhanced_prompt}

            if quality_mode == 'master':
                # Inject professional stability and limb safety guards
                req_body['negative_prompt'] = custom_params.get('negative_prompt', 'distorted hands, missing fingers, extra fingers, deformed limbs, floating camera, uncontrolled drift, blurry, plastic skin, lowres')

            applied = dur

            ep = target_endpoint



            # 0. Dedicated ByteDance Seedance 2.5 (30s Single Pass & Multi-Reference)
            if 'seedance' in ep:
                applied = min(max(dur, 2), 30)
                multi_imgs = custom_params.get('image_urls') or []
                single_img = (custom_params.get('image_url') or '').strip()
                if not multi_imgs and single_img:
                    multi_imgs = [single_img]

                resolved_imgs = []
                if multi_imgs and isinstance(multi_imgs, list):
                    for m_img in multi_imgs[:30]:
                        if not m_img.startswith('http'):
                            u = upload_file_to_fal(m_img, fal_key) or m_img
                        else:
                            u = m_img
                        resolved_imgs.append(u)

                if resolved_imgs:
                    target_endpoint = "bytedance/seedance-2.5/reference-to-video"
                    req_body['image_urls'] = resolved_imgs
                    req_body['image_url'] = resolved_imgs[0]
                elif 'image-to-video' in ep:
                    target_endpoint = "bytedance/seedance-2.5/image-to-video"
                else:
                    # Text-to-Video fallback when no references are attached
                    target_endpoint = "fal-ai/bytedance/seedance/v1/pro/text-to-video"

                req_body.update({
                    'duration': applied,
                    'aspect_ratio': ar,
                    'generate_audio': True,
                    'resolution': custom_params.get('resolution', '720p')
                })

                # Check optional driving video or audio references for Seedance
                driv_vid = (custom_params.get('video_url') or '').strip()
                if driv_vid:
                    if not driv_vid.startswith('http'):
                        driv_vid = upload_file_to_fal(driv_vid, fal_key) or driv_vid
                    req_body['video_url'] = driv_vid
                driv_aud = (custom_params.get('audio_url') or '').strip()
                if driv_aud:
                    if not driv_aud.startswith('http'):
                        driv_aud = upload_file_to_fal(driv_aud, fal_key) or driv_aud
                    req_body['audio_url'] = driv_aud

            # 1. Handle Motion Control (Character Image + Driving Video)
            elif 'motion-control' in ep:
                char_img = (custom_params.get('image_url') or custom_params.get('character_image') or '').strip()
                driv_vid = (custom_params.get('video_url') or custom_params.get('driving_video') or '').strip()
                if not char_img or not driv_vid:
                    # Check outputs for latest character or driving video
                    if not char_img:
                        recent_imgs = sorted([f for f in os.listdir(OUTPUTS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))],
                                             key=lambda x: os.path.getmtime(os.path.join(OUTPUTS_DIR, x)), reverse=True)
                        if recent_imgs:
                            char_img = f"/outputs/{recent_imgs[0]}"
                    if not driv_vid:
                        recent_vids = sorted([f for f in os.listdir(OUTPUTS_DIR) if f.lower().endswith(('.mp4', '.mov', '.webm'))],
                                             key=lambda x: os.path.getmtime(os.path.join(OUTPUTS_DIR, x)), reverse=True)
                        if recent_vids:
                            driv_vid = f"/outputs/{recent_vids[0]}"

                if not char_img or not driv_vid:
                    self.send_error_response(400, "يتطلب نقل الحركة (Motion Control) كلاً من: صورة الشخصية (Character) وفيديو الحركة (Driving Video).")
                    return

                if not char_img.startswith('http'):
                    char_img = upload_file_to_fal(char_img, fal_key) or char_img
                if not driv_vid.startswith('http'):
                    driv_vid = upload_file_to_fal(driv_vid, fal_key) or driv_vid

                req_body = {
                    'image_url': char_img,
                    'video_url': driv_vid,
                    'character_orientation': custom_params.get('character_orientation', 'video')
                }
                if prompt:
                    req_body['prompt'] = prompt

            # 2. Handle Video-to-Video Edit & Reframe (Original Video + Text Prompt)
            elif any(k in ep for k in ['video-to-video', 'modify', 'reframe']):
                vid_input = (custom_params.get('video_url') or custom_params.get('source_video') or '').strip()
                if not vid_input:
                    recent_vids = sorted([f for f in os.listdir(OUTPUTS_DIR) if f.lower().endswith(('.mp4', '.mov', '.webm'))],
                                         key=lambda x: os.path.getmtime(os.path.join(OUTPUTS_DIR, x)), reverse=True)
                    if recent_vids:
                        vid_input = f"/outputs/{recent_vids[0]}"
                if not vid_input:
                    self.send_error_response(400, "يتطلب هذا النموذج (Reframe / Video Edit) رفع فيديو أصلي لمعالجته.")
                    return
                if not vid_input.startswith('http'):
                    vid_input = upload_file_to_fal(vid_input, fal_key) or vid_input
                req_body['video_url'] = vid_input
                if 'reframe' in ep:
                    target_ar = custom_params.get('aspect_ratio') or ar or '9:16'
                    req_body['aspect_ratio'] = target_ar

            # 3. Handle Video LoRA models (LTX 2.3 LoRA / MiniMax H3 LoRA)
            elif 'lora' in ep and model_type == 'video':
                lora_url = (custom_params.get('lora_url') or '').strip()
                loras_list = custom_params.get('loras') or []
                if not lora_url and loras_list and isinstance(loras_list, list):
                    lora_url = (loras_list[0].get('path') or loras_list[0].get('url') or '').strip()

                if not lora_url:
                    # Director did not attach a LoRA! Gracefully route to standard pristine LTX Video (T2V or I2V)
                    if 'ltx' in ep:
                        img_input = (custom_params.get('image_url') or '').strip()
                        if img_input:
                            target_endpoint = 'fal-ai/ltx-video-13b-distilled/image-to-video'
                            if not img_input.startswith('http'):
                                img_input = upload_file_to_fal(img_input, fal_key) or img_input
                            req_body['image_url'] = img_input
                        else:
                            target_endpoint = 'fal-ai/ltx-video-13b-distilled'
                        ep = target_endpoint
                    else:
                        target_endpoint = 'fal-ai/minimax-video'
                        ep = target_endpoint
                else:
                    # LoRA is present! Set loras array properly
                    req_body['loras'] = [{'path': lora_url, 'scale': float(custom_params.get('lora_scale', 1.0))}]
                    img_input = (custom_params.get('image_url') or '').strip()
                    if not img_input:
                        # Auto-find recent character portrait/render if available
                        img_files = sorted([f for f in os.listdir(OUTPUTS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and 'depth' not in f.lower()],
                                           key=lambda x: os.path.getmtime(os.path.join(OUTPUTS_DIR, x)), reverse=True)
                        if img_files:
                            img_input = f"/outputs/{img_files[0]}"
                    if img_input:
                        if not img_input.startswith('http'):
                            img_input = upload_file_to_fal(img_input, fal_key) or img_input
                        req_body['image_url'] = img_input

            # 4. Handle Image-to-Video (Start Frame + Optional End Frame) or T2V upgraded with attached image_url
            elif any(k in ep for k in ['image-to-video', 'reference-to-video', 'i2v']) or (custom_params.get('image_url') or '').strip():
                if ep == 'fal-ai/wan-t2v':
                    target_endpoint = 'fal-ai/wan-i2v'
                    ep = target_endpoint
                elif ep in ('fal-ai/kling-video/v1/standard/text-to-video', 'fal-ai/kling-video/v1.5/pro/text-to-video'):
                    target_endpoint = 'fal-ai/kling-video/v1.6/pro/image-to-video'
                    ep = target_endpoint
                elif ep == 'fal-ai/luma-dream-machine':
                    target_endpoint = 'fal-ai/luma-dream-machine/ray-2/image-to-video'
                    ep = target_endpoint
                elif ep == 'fal-ai/runway/gen3/turbo':
                    target_endpoint = 'fal-ai/runway-gen3/turbo/image-to-video'
                    ep = target_endpoint

                img_input = (custom_params.get('image_url') or '').strip()
                if not img_input:
                    img_files = sorted([f for f in os.listdir(OUTPUTS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and 'depth' not in f.lower()],
                                       key=lambda x: os.path.getmtime(os.path.join(OUTPUTS_DIR, x)), reverse=True)
                    if img_files:
                        img_input = f"/outputs/{img_files[0]}"
                if not img_input:
                    self.send_error_response(400, "هذا النموذج يتطلب صورة مرجعية كمدخل (Image-to-Video). يرجى توليد كادر أو رفع صورة للشخصية أولاً.")
                    return
                if not img_input.startswith('http'):
                    cloud_url = upload_file_to_fal(img_input, fal_key) or img_input
                else:
                    cloud_url = img_input
                req_body['image_url'] = cloud_url

                # Optional End Frame for supported models (Kling / Luma)
                end_img = (custom_params.get('end_image_url') or '').strip()
                if end_img:
                    if not end_img.startswith('http'):
                        cloud_end = upload_file_to_fal(end_img, fal_key) or end_img
                    else:
                        cloud_end = end_img
                    req_body['tail_image_url'] = cloud_end
                    req_body['end_frame_url'] = cloud_end

            # 5. Handle LipSync Models (Sync Labs 2.0 / MuseTalk)
            elif 'lipsync' in ep or 'musetalk' in ep:
                vid_input = (custom_params.get('video_url') or '').strip()
                aud_input = (custom_params.get('audio_url') or '').strip()
                if not vid_input or not aud_input:
                    self.send_error_response(400, "يتطلب مزامنة الشفاه (Lip-Sync) كلاً من: الفيديو الأساسي + ملف الصوت الحواري.")
                    return
                if not vid_input.startswith('http'):
                    vid_input = upload_file_to_fal(vid_input, fal_key) or vid_input
                if not aud_input.startswith('http'):
                    aud_input = upload_file_to_fal(aud_input, fal_key) or aud_input
                req_body['video_url'] = vid_input
                req_body['audio_url'] = aud_input

            # 6. Handle Video Upscale (Topaz / Super-resolution)
            elif 'upscale-video' in ep or 'topaz' in ep:
                vid_input = (custom_params.get('video_url') or '').strip()
                if not vid_input:
                    self.send_error_response(400, "يتطلب رفع دقة الفيديو (Topaz Upscale) تحديد فيديو المصدر.")
                    return
                if not vid_input.startswith('http'):
                    vid_input = upload_file_to_fal(vid_input, fal_key) or vid_input
                req_body['video_url'] = vid_input

            # 7. Handle MMAudio v2 or Audio-Attached Video Models
            elif 'mmaudio' in ep:
                vid_input = (custom_params.get('video_url') or '').strip()
                if vid_input:
                    if not vid_input.startswith('http'):
                        vid_input = upload_file_to_fal(vid_input, fal_key) or vid_input
                    req_body['video_url'] = vid_input

            if 'veo3' in ep:

                applied = min([4, 6, 8], key=lambda x: abs(x - dur))

                req_body.update({'duration': f"{applied}s", 'aspect_ratio': ar if ar in ('16:9', '9:16') else '16:9'})

            elif 'kling' in ep:

                applied = 10 if dur >= 8 else 5

                req_body.update({'duration': str(applied), 'aspect_ratio': ar if ar in ('16:9', '9:16', '1:1') else '16:9'})

            elif 'seedance' in ep:
                applied = min(max(dur, 2), 30)
                req_body.update({
                    'duration': applied,
                    'aspect_ratio': ar,
                    'generate_audio': True,
                    'resolution': custom_params.get('resolution', '720p')
                })
                multi_imgs = custom_params.get('image_urls') or []
                if multi_imgs and isinstance(multi_imgs, list):
                    resolved = []
                    for m_img in multi_imgs[:30]:
                        if not m_img.startswith('http'):
                            u = upload_file_to_fal(m_img, fal_key) or m_img
                        else:
                            u = m_img
                        resolved.append(u)
                    req_body['image_urls'] = resolved

            elif 'flux-3-max' in ep or 'flux-3' in ep:
                applied = min(max(dur, 5), 20)
                req_body.update({
                    'duration': applied,
                    'generate_audio': custom_params.get('generate_audio', True)
                })

            elif 'hailuo' in ep:

                applied = 10 if dur >= 8 else 6

                req_body.update({'duration': str(applied)})

            elif 'luma' in ep:

                applied = 9 if dur >= 8 else 5

                req_body.update({'duration': f"{applied}s", 'aspect_ratio': ar})

            elif 'wan' in ep:

                req_body.update({'aspect_ratio': ar if ar in ('16:9', '9:16', '1:1') else '16:9'})

            elif 'minimax' in ep:

                applied = 6  # video-01 is fixed length



            try:

                submit_url = f"https://queue.fal.run/{target_endpoint}"

                res = requests.post(submit_url, headers=headers, json=req_body, timeout=30)

                if res.status_code in [200, 201, 202]:

                    q_data = res.json()

                    status_url = q_data.get('status_url')

                    response_url = q_data.get('response_url')



                    video_url = None

                    for _ in range(120):  # up to ~8 minutes (server is threaded, so it never blocks the UI)

                        time.sleep(4)

                        poll_res = requests.get(status_url, headers=headers, timeout=15)

                        if poll_res.status_code == 200:

                            p_data = poll_res.json()

                            if p_data.get('status') == 'COMPLETED':

                                final_res = requests.get(response_url, headers=headers, timeout=15)

                                if final_res.status_code == 200:

                                    f_data = final_res.json()

                                    video_obj = f_data.get('video', {})

                                    video_url = video_obj.get('url') if isinstance(video_obj, dict) else f_data.get('video_url')

                                break

                            elif p_data.get('status') == 'FAILED':

                                self.send_error_response(500, f"فشل التوليد: {p_data.get('error')}")

                                return



                    if video_url:

                        self.send_json_response(200, {

                            "success": True,

                            "media_type": "video",

                            "url": video_url,

                            "endpoint": target_endpoint,

                            "applied_duration": applied,

                            "requested_duration": dur,

                            "prompt": prompt,

                            "message": f"تم توليد لقطة الفيديو ({applied}s) بنجاح عبر {target_endpoint}!"

                        })

                    else:

                        self.send_json_response(202, {

                            "success": True,

                            "pending": True,

                            "message": "طلب الفيديو قيد المعالجة السحابية وسيعرض فور اكتماله..."

                        })

                else:

                    self.send_error_response(res.status_code, f"خطأ في إرسال طلب الفيديو: {res.text[:300]}")

            except Exception as e:

                self.send_error_response(500, f"Error: {str(e)}")



    def handle_critique(self, payload):

        # If media URL or frame data is provided, run full Gemini Vision analysis directly

        if payload.get('url') or payload.get('frame_data_url'):

            return self.handle_analyze_media(payload)



        model = payload.get('model', 'Cinematic Model')

        critique = {

            "director": "Cindy (سيندي)",

            "camera_score": "—",

            "physics_score": "—",

            "lighting_score": "—",

            "overall_rating": "جاهز للفحص",

            "analysis": f"اكتمل التوليد بنجاح عبر '{model}'. اضغط زر «فحص ونقد اللقطة بالرؤية الذكية» لتشغيل فحص حقيقي بكسل-بكسل عبر محرك Google Gemini Vision.",

            "recommendations": [

                "استخدم الإطار الحالي كمرجع (Image-to-Video) لتثبيت الملامح في اللقطة التالية.",

                "اضغط «فحص ونقد اللقطة بالرؤية الذكية» لتحليل الكاميرا والإضاءة واستخراج برومبت التعديل آلياً."

            ],

            "discussion_questions": [

                "هل تفضل فحص اللقطة بالرؤية الذكية واقتراح تحسينات للإضاءة والكاميرا؟",

                "هل نعتمد هذه النتيجة وننتقل فوراً لتوليد اللقطة التالية؟"

            ]

        }

        self.send_json_response(200, critique)



    def handle_media_download(self):

        parsed = urllib.parse.urlparse(self.path)

        qs = urllib.parse.parse_qs(parsed.query)

        url = (qs.get('url', [''])[0] or '').strip()

        req_name = (qs.get('name', [''])[0] or '').strip()



        if not url:

            self.send_error_response(400, "رابط الوسائط مطلوب للتنزيل.")

            return



        raw_bytes = None

        content_type = 'application/octet-stream'

        ext = 'jpg'



        if url.startswith('/outputs/') or url.startswith('http://127.0.0.1:8765/outputs/') or url.startswith('http://localhost:8765/outputs/'):

            rel = url.split('/outputs/', 1)[1].split('?')[0].split('#')[0]

            fpath = _safe_output_path(rel)

            if not fpath or not os.path.isfile(fpath):

                self.send_error_response(404, "الملف غير موجود في مجلد المخرجات.")

                return

            with open(fpath, 'rb') as fh:

                raw_bytes = fh.read()

            ext = os.path.splitext(fpath)[1].lstrip('.').lower() or 'jpg'

        elif url.startswith('data:') and ';base64,' in url:

            header, b64data = url.split(';base64,', 1)

            raw_bytes = base64.b64decode(b64data)

            _, magic_ext = _detect_magic_media(raw_bytes)

            if not magic_ext:

                self.send_error_response(400, "محتوى الملف غير صالح.")

                return

            ext = magic_ext

        elif url.startswith('https://'):

            host = urllib.parse.urlparse(url).hostname or ''

            allowed_hosts = ('fal.media', 'fal.ai', 'googleapis.com', 'googleusercontent.com', 'gstatic.com')

            if not any(host == h or host.endswith('.' + h) for h in allowed_hosts):

                self.send_error_response(403, "النطاق غير مسموح للتنزيل بالنيابة.")

                return

            try:

                r = requests.get(url, timeout=60, allow_redirects=False, stream=True)

                if r.status_code in (301, 302, 303, 307, 308):

                    loc = r.headers.get('Location', '')

                    loc_host = urllib.parse.urlparse(loc).hostname or ''

                    if not loc.startswith('https://') or not any(loc_host == h or loc_host.endswith('.' + h) for h in allowed_hosts):

                        self.send_error_response(403, "إعادة التوجيه لنطاق خارجي غير مسموح بها.")

                        return

                    r = requests.get(loc, timeout=60, allow_redirects=False, stream=True)

                if r.status_code != 200:

                    self.send_error_response(r.status_code, "تعذر جلب الملف من الخادم السحابي.")

                    return

                chunks = []

                total_len = 0

                for chunk in r.iter_content(chunk_size=65536):

                    if chunk:

                        total_len += len(chunk)

                        if total_len > 120 * 1024 * 1024:

                            self.send_error_response(413, "حجم الملف يتجاوز الحد المسموح للتنزيل (120MB).")

                            return

                        chunks.append(chunk)

                raw_bytes = b''.join(chunks)

                _, magic_ext = _detect_magic_media(raw_bytes)

                ext = magic_ext or ('mp4' if url.lower().endswith('.mp4') else 'jpg')

                # Save a local backup in outputs/ automatically if genuine media

                if magic_ext:

                    backup_name = f"cindy_saved_{int(time.time() * 1000)}.{magic_ext}"

                    bf_path = _safe_output_path(backup_name)

                    if bf_path:

                        try:

                            with open(bf_path, 'wb') as bf:

                                bf.write(raw_bytes)

                        except Exception:

                            pass

            except Exception as e:

                self.send_error_response(500, f"خطأ أثناء التنزيل: {e}")

                return

        else:

            self.send_error_response(400, "صيغة الرابط غير مدعومة.")

            return



        mime_map = {

            'mp4': 'video/mp4',

            'webm': 'video/webm',

            'mov': 'video/quicktime',

            'png': 'image/png',

            'webp': 'image/webp',

            'gif': 'image/gif',

            'jpg': 'image/jpeg',

            'jpeg': 'image/jpeg'

        }

        content_type = mime_map.get(ext, 'application/octet-stream')

        safe_base = re.sub(r'[^A-Za-z0-9_\-]', '_', req_name) if req_name else f"Cindy_Studio_{int(time.time())}"

        if not safe_base.lower().endswith('.' + ext):

            safe_base = f"{safe_base}.{ext}"



        self.send_response(200)

        self.send_header('Content-Type', content_type)

        self.send_header('Content-Length', str(len(raw_bytes)))

        self.send_header('Content-Disposition', f'attachment; filename="{safe_base}"')

        self.end_headers()

        self.wfile.write(raw_bytes)



    def handle_media_upload(self, payload):

        data_url = payload.get('data_url', '')

        orig_name = payload.get('filename', 'upload')

        if not data_url or not data_url.startswith('data:') or ';base64,' not in data_url:

            self.send_error_response(400, "يرجى اختيار ملف صورة أو فيديو صالح للرفع.")

            return



        header, b64data = data_url.split(';base64,', 1)

        try:

            raw = base64.b64decode(b64data)

        except Exception:

            self.send_error_response(400, "ترميز الملف المرفوع غير صالح.")

            return



        media_type, ext = _detect_magic_media(raw, orig_name)

        if not media_type or not ext:

            self.send_error_response(400, "نوع الملف غير مدعوم أمنياً — يُسمح فقط بملفات الصور (JPG/PNG/WEBP/GIF) والفيديو (MP4/WEBM) والصوت (WAV/MP3) الحقيقية.")

            return



        ts = int(time.time() * 1000)

        safe_stem = re.sub(r'[^A-Za-z0-9_\-]', '_', os.path.splitext(orig_name)[0])[:32] or 'media'

        fname = f"upload_{ts}_{safe_stem}.{ext}"

        fpath = _safe_output_path(fname)

        if not fpath:

            self.send_error_response(400, "اسم الملف غير صالح.")

            return



        try:

            with open(fpath, 'wb') as fh:

                fh.write(raw)

        except Exception as e:

            self.send_error_response(500, f"فشل حفظ الملف المرفوع: {e}")

            return



        self.send_json_response(200, {

            "success": True,

            "url": f"/outputs/{fname}",

            "media_type": media_type,

            "filename": orig_name,

            "size_kb": round(len(raw) / 1024, 1),

            "message": f"تم رفع {'الفيديو' if media_type == 'video' else 'الصورة'} بنجاح وجاهز للمناقشة والتعديل!"

        })



    def _resolve_media_for_fal(self, media_url, fal_key):

        """Converts local /outputs/... or data: URI into a Fal CDN URL (or data URI fallback) so cloud models can read it."""

        if not media_url:

            return ''

        if media_url.startswith('https://'):

            return media_url



        raw_bytes = None

        mime = 'image/jpeg'

        fname = 'cindy_input.jpg'



        if media_url.startswith('data:') and ';base64,' in media_url:

            header, b64data = media_url.split(';base64,', 1)

            raw_bytes = base64.b64decode(b64data)

            mime = header.replace('data:', '').strip() or 'image/jpeg'

            ext = 'mp4' if 'video' in mime else ('png' if 'png' in mime else 'jpg')

            fname = f"cindy_input.{ext}"

        elif '/outputs/' in media_url:

            rel = media_url.split('/outputs/', 1)[1].split('?')[0].split('#')[0]

            fpath = _safe_output_path(rel)

            if fpath and os.path.isfile(fpath):

                with open(fpath, 'rb') as fh:

                    raw_bytes = fh.read()

                ext = os.path.splitext(fpath)[1].lstrip('.').lower() or 'jpg'

                fname = os.path.basename(fpath)

                mime = 'video/mp4' if ext in ('mp4', 'webm', 'mov') else ('image/png' if ext == 'png' else 'image/jpeg')



        if not raw_bytes:

            return media_url



        # Upload to Fal CDN v3 so both Image and Video endpoints receive a fast https://v3b.fal.media/... URL

        if fal_key:

            try:

                init_headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json", "Accept": "application/json"}

                init_res = requests.post(

                    "https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",

                    headers=init_headers,

                    json={"file_name": fname, "content_type": mime},

                    timeout=15

                )

                if init_res.status_code == 200:

                    init_data = init_res.json()

                    upload_url = init_data.get('upload_url')

                    file_url = init_data.get('file_url')

                    if upload_url and file_url:

                        put_res = requests.put(upload_url, data=raw_bytes, headers={"Content-Type": mime}, timeout=60)

                        if put_res.status_code in (200, 201):

                            return file_url

            except Exception:

                pass



        # Fallback to data URI

        return f"data:{mime};base64,{base64.b64encode(raw_bytes).decode('ascii')}"



    def handle_analyze_media(self, payload):

        url = payload.get('url', '')

        media_type = payload.get('media_type', 'image')

        question = (payload.get('question') or '').strip()

        frame_data_url = payload.get('frame_data_url', '')



        secrets = load_secrets()

        gemini_key = secrets.get('gemini_api_key', '')



        # Load image bytes (or extracted video keyframe bytes) for Gemini Vision analysis

        b64_img = ''

        img_mime = 'image/jpeg'

        if frame_data_url and ';base64,' in frame_data_url:

            h, b64_img = frame_data_url.split(';base64,', 1)

            img_mime = h.replace('data:', '').strip() or 'image/jpeg'

        elif url and url.startswith('data:') and ';base64,' in url:

            h, b64_img = url.split(';base64,', 1)

            img_mime = h.replace('data:', '').strip() or 'image/jpeg'

        elif url and '/outputs/' in url:

            rel = url.split('/outputs/', 1)[1].split('?')[0].split('#')[0]

            fpath = _safe_output_path(rel)

            if fpath and os.path.isfile(fpath):

                try:

                    with open(fpath, 'rb') as fh:

                        raw_b = fh.read()

                        b64_img = base64.b64encode(raw_b).decode('ascii')

                    img_mime = 'image/png' if fpath.lower().endswith('.png') else 'image/jpeg'

                except Exception:

                    pass

        elif url and url.startswith(('http://', 'https://')):

            try:

                r_img = requests.get(url, timeout=10)

                if r_img.status_code == 200 and len(r_img.content) < 15 * 1024 * 1024:

                    b64_img = base64.b64encode(r_img.content).decode('ascii')

                    ct = r_img.headers.get('content-type', 'image/jpeg').split(';')[0].strip()

                    img_mime = ct if 'image' in ct else 'image/jpeg'

            except Exception:

                pass



        # Compress/thumbnail image with PIL if large to prevent timeouts

        if b64_img and Image is not None:

            try:

                raw_bytes = base64.b64decode(b64_img)

                if len(raw_bytes) > 200 * 1024:

                    im = Image.open(io.BytesIO(raw_bytes))

                    im.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

                    buf = io.BytesIO()

                    if im.mode in ('RGBA', 'P'):

                        im = im.convert('RGB')

                    im.save(buf, format='JPEG', quality=85, optimize=True)

                    b64_img = base64.b64encode(buf.getvalue()).decode('ascii')

                    img_mime = 'image/jpeg'

            except Exception:

                pass



        user_q = question or ("حللي هذا الفيديو سينمائياً واقترحي كيف نعدله أو نحوله إلى لقطة سينمائية حركية" if media_type == 'video' else "حللي هذه الصورة سينمائياً واقترحي كيف نعدلها أو نحركها إلى فيديو 24fps")



        # 100% REAL GEMINI MULTIMODAL VISION ANALYSIS

        if gemini_key and b64_img:

            sys_instruction = (

                "You are Cindy (سيندي), an elite Hollywood visual director and Master AI Prompt Engineer. "

                "Examine the attached image or video frame in full cinematic depth. "

                "Critique the actual visual content seen in the image: subject composition, camera framing and lens angle, dynamic range, lighting distribution and color grading, and any defects or highlights. "

                "Respond ONLY with a valid JSON object matching this schema:\n"

                "{\n"

                '  "camera_score": "Rating out of 10 for camera work (e.g. 8.8/10)",\n'

                '  "lighting_score": "Rating out of 10 for lighting (e.g. 9.1/10)",\n'

                '  "physics_score": "Rating out of 10 for visual coherence (e.g. 8.9/10)",\n'

                '  "scene_summary": "Short Arabic sentence describing exactly what is seen in the image",\n'

                '  "analysis": "Comprehensive Arabic directorial critique analyzing camera framing, depth of field, lighting, composition, and answering the director request directly",\n'

                '  "edit_prompt": "Cohesive, high-end Hollywood cinematic English prompt to refine this scene or animate it into a 24fps motion shot",\n'

                '  "recommendations": ["Directorial recommendation 1 in Arabic", "Directorial recommendation 2 in Arabic"]\n'

                "}"

            )

            for v_model in ('gemini-3.5-flash-lite', 'gemini-flash-latest', 'gemini-3.1-flash-lite'):

                try:

                    g_url = f"https://generativelanguage.googleapis.com/v1beta/models/{v_model}:generateContent?key={gemini_key}"

                    req_body = {

                        "contents": [{

                            "parts": [

                                {"text": f"{sys_instruction}\n\nسؤال/طلب المخرج: {user_q}"},

                                {"inlineData": {"mimeType": img_mime, "data": b64_img}}

                            ]

                        }],

                        "generationConfig": {"responseMimeType": "application/json"}

                    }

                    r = requests.post(g_url, json=req_body, timeout=25)

                    if r.status_code == 200:

                        cand = r.json().get('candidates', [])

                        if cand:

                            txt = cand[0].get('content', {}).get('parts', [{}])[0].get('text', '')

                            parsed_json = json.loads(txt)

                            parsed_json["success"] = True

                            parsed_json["is_real_vision"] = True

                            parsed_json["vision_engine"] = f"Google {v_model} Vision"

                            self.send_json_response(200, parsed_json)

                            return

                except Exception:

                    continue



        # No fake fallback scores! Honest report to user as requested.

        self.send_json_response(200, {

            "success": False,

            "is_real_vision": False,

            "camera_score": "—",

            "physics_score": "—",

            "lighting_score": "—",

            "analysis": "تنبيه: لم نتمكن من فحص بكسلات المشهد بالرؤية الذكية. تأكد من تفعيل مفتاح Google في الخزنة وعرض/رفع ملف صورة أو فيديو صحيح.",

            "edit_prompt": "",

            "recommendations": []

        })



    def handle_edit_media(self, payload):
        if not payload.get('user_confirmed'):
            self.send_json_response(403, {
                "success": False,
                "error": "🛡️ حماية مالية: يتطلب تأكيداً يدوياً صريحاً من المخرج في الواجهة لتجنب أي خصم غير مقصود."
            })
            return

        source_url = payload.get('source_url', '')

        action = payload.get('action', 'edit_image')  # edit_image | image_to_video | edit_video | add_audio

        model = payload.get('model', 'fal-ai/nano-banana/edit')

        prompt = (payload.get('prompt') or '').strip()

        aspect_ratio = payload.get('aspect_ratio', 'landscape_16_9')

        duration = int(payload.get('duration', 5) or 5)

        num_images = min(max(int(payload.get('num_images', 1) or 1), 1), 4)



        if not source_url:

            self.send_error_response(400, "يرجى رفع أو اختيار صورة/فيديو أولاً للتعديل عليه.")

            return

        if not prompt:

            prompt = "Enhance cinematic lighting, photorealistic details, 35mm anamorphic depth of field"



        secrets = load_secrets()

        fal_key = secrets.get('fal_api_key', '')

        if not fal_key:

            self.send_error_response(400, "مفتاح Fal.ai مطلوب في الخزنة لتشغيل محركات التعديل والتحريك.")

            return



        # Convert local /outputs/... or data: URI to a cloud-accessible URL via Fal CDN

        cloud_media_url = self._resolve_media_for_fal(source_url, fal_key)

        headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}

        ar_map = {'landscape_16_9': '16:9', 'portrait_9_16': '9:16', 'square_hd': '1:1', 'landscape_21_9': '21:9',

                  '16:9': '16:9', '9:16': '9:16', '1:1': '1:1', '21:9': '21:9'}

        ar = ar_map.get(aspect_ratio, '16:9')



        # 1. IMAGE EDITING (Nano Banana Edit / Nano Banana Pro Edit / Flux Dev Image-to-Image)

        if action == 'edit_image':
            if 'qwen' in model:
                ep = 'fal-ai/qwen-image-edit-2511'
                req_body = {'prompt': prompt, 'image_urls': [cloud_media_url], 'num_images': num_images, 'aspect_ratio': ar, 'output_format': 'jpeg'}
            elif 'nano-banana' in model:

                ep = "fal-ai/nano-banana-pro/edit" if "pro" in model else "fal-ai/nano-banana/edit"

                req_body = {

                    "prompt": prompt,

                    "image_urls": [cloud_media_url],

                    "num_images": num_images,

                    "aspect_ratio": ar,

                    "output_format": "jpeg"

                }

            else:

                ep = "fal-ai/flux/dev/image-to-image"

                req_body = {

                    "prompt": prompt,

                    "image_url": cloud_media_url,

                    "strength": float(payload.get('strength', 0.75)),

                    "num_images": num_images,

                    "enable_safety_checker": False

                }



            try:

                res = requests.post(f"https://fal.run/{ep}", headers=headers, json=req_body, timeout=90)

                if res.status_code == 200:

                    data = res.json()

                    imgs = data.get('images', [])

                    images_list = [{"url": im.get('url', '')} for im in imgs if im.get('url')]

                    if images_list:

                        self.send_json_response(200, {

                            "success": True,

                            "media_type": "image",

                            "url": images_list[0]['url'],

                            "images": images_list,

                            "endpoint": ep,

                            "prompt": prompt,

                            "message": f"تم تعديل الصورة بنجاح عبر {ep}!"

                        })

                        return

                self.send_error_response(res.status_code, f"خطأ أثناء تعديل الصورة: {res.text[:250]}")

                return

            except Exception as e:

                self.send_error_response(500, f"خطأ اتصال أثناء تعديل الصورة: {e}")

                return



        # 2. IMAGE-TO-VIDEO OR VIDEO EDITING / AUDIO ADDITION (Async Queue Polling)

        if action == 'image_to_video':

            if 'veo' in model:

                ep = "fal-ai/veo3.1/image-to-video"

                applied = 4 if duration <= 4 else (6 if duration <= 6 else 8)

                req_body = {

                    "prompt": prompt,

                    "image_url": cloud_media_url,

                    "duration": f"{applied}s",

                    "aspect_ratio": ar if ar in ('16:9', '9:16') else '16:9',

                    "generate_audio": True

                }

            elif 'luma' in model or 'ray' in model:

                ep = "fal-ai/luma-dream-machine/ray-2/image-to-video"

                applied = 9 if duration >= 8 else 5

                req_body = {

                    "prompt": prompt,

                    "image_url": cloud_media_url,

                    "duration": f"{applied}s",

                    "aspect_ratio": ar

                }

            else:

                ep = "fal-ai/kling-video/v1.6/pro/image-to-video"

                applied = 10 if duration >= 8 else 5

                req_body = {

                    "prompt": prompt,

                    "image_url": cloud_media_url,

                    "duration": str(applied),

                    "aspect_ratio": ar if ar in ('16:9', '9:16', '1:1') else '16:9'

                }

        elif action == 'add_audio':

            ep = "fal-ai/mmaudio-v2"

            applied = min(max(duration, 4), 15)

            req_body = {

                "video_url": cloud_media_url,

                "prompt": prompt,

                "duration": applied

            }

        else:  # edit_video

            if 'luma' in model or 'ray' in model:

                ep = "fal-ai/luma-dream-machine/ray-2/modify"

                applied = duration

                req_body = {

                    "video_url": cloud_media_url,

                    "prompt": prompt,

                    "mode": "adhere_1"

                }

            else:

                ep = "fal-ai/kling-video/o1/video-to-video/edit"

                applied = duration

                req_body = {

                    "video_url": cloud_media_url,

                    "prompt": prompt,

                    "keep_audio": True

                }



        try:

            submit_url = f"https://queue.fal.run/{ep}"

            res = requests.post(submit_url, headers=headers, json=req_body, timeout=30)

            if res.status_code in (200, 201, 202):

                q_data = res.json()

                status_url = q_data.get('status_url')

                response_url = q_data.get('response_url')



                video_url = None

                for _ in range(120):

                    time.sleep(4)

                    poll_res = requests.get(status_url, headers=headers, timeout=15)

                    if poll_res.status_code == 200:

                        p_data = poll_res.json()

                        if p_data.get('status') == 'COMPLETED':

                            # Try to extract URL from p_data directly first

                            video_url = _extract_media_url(p_data)

                            if not video_url and response_url:

                                try:

                                    final_res = requests.get(response_url, headers=headers, timeout=25)

                                    if final_res.status_code == 200:

                                        f_data = final_res.json()

                                        video_url = _extract_media_url(f_data)

                                except Exception as err:

                                    print("[Edit Media] Error fetching response_url:", err)

                            break

                        elif p_data.get('status') == 'FAILED':

                            self.send_error_response(500, f"فشل تعديل/تحريك اللقطة: {p_data.get('error')}")

                            return



                if video_url:

                    self.send_json_response(200, {

                        "success": True,

                        "media_type": "video",

                        "url": video_url,

                        "endpoint": ep,

                        "applied_duration": applied,

                        "prompt": prompt,

                        "message": f"تم إنتاج الفيديو بنجاح عبر {ep}!"

                    })

                else:

                    self.send_json_response(202, {

                        "success": True,

                        "pending": True,

                        "status_url": status_url,

                        "response_url": response_url,

                        "endpoint": ep,

                        "prompt": prompt,

                        "message": "الطلب لا يزال قيد المعالجة السحابية في طابور الريندر..."

                    })

            else:

                self.send_error_response(res.status_code, f"خطأ من المحرك السحابي ({ep}): {res.text[:250]}")

        except Exception as e:

            self.send_error_response(500, f"خطأ أثناء معالجة الفيديو: {e}")



    def send_json_response(self, code, data):

        body = json.dumps(data, ensure_ascii=False).encode('utf-8')

        self.send_response(code)

        self.send_header('Content-Type', 'application/json; charset=utf-8')

        self.send_header('Content-Length', str(len(body)))

        self.end_headers()

        self.wfile.write(body)



    def send_error_response(self, code, msg):

        safe_msg = _redact_secrets(msg)

        body = json.dumps({"success": False, "error": safe_msg}, ensure_ascii=False).encode('utf-8')

        self.send_response(code)

        self.send_header('Content-Type', 'application/json; charset=utf-8')

        self.send_header('Content-Length', str(len(body)))

        self.end_headers()

        self.wfile.write(body)







    def handle_lora_list(self):

        loras = load_loras()

        active = {k: v for k, v in LORA_TRAINING_JOBS.items() if v.get('status') in ('IN_QUEUE', 'IN_PROGRESS')}

        self.send_json_response(200, {

            "success": True,

            "loras": loras,

            "active_jobs": active

        })



    def handle_lora_job_status(self):

        parsed = urllib.parse.urlparse(self.path)

        qs = urllib.parse.parse_qs(parsed.query)

        job_id = (qs.get('id', [''])[0] or '').strip()

        job = LORA_TRAINING_JOBS.get(job_id)

        if not job:

            self.send_error_response(404, "معرف مهمة التدريب غير موجود.")

            return

        self.send_json_response(200, {"success": True, "job": job})



    def handle_lora_download(self):

        parsed = urllib.parse.urlparse(self.path)

        qs = urllib.parse.parse_qs(parsed.query)

        lora_id = (qs.get('id', [''])[0] or '').strip()

        filename = (qs.get('file', [''])[0] or '').strip()



        # Find in registry or active memory

        loras = load_loras()

        match = next((l for l in loras if l.get('id') == lora_id), None)

        if not match and lora_id in LORA_TRAINING_JOBS:

            match = LORA_TRAINING_JOBS[lora_id]

        

        target_path = None

        target_url = None

        dl_name = f"{lora_id}.safetensors"



        if match:

            dl_name = f"{match.get('trigger_word', 'lora')}_weights.safetensors"

            if match.get('local_file'):

                target_path = _safe_lora_path(match['local_file'])

            target_url = match.get('weights_url') or match.get('url')

        elif filename:

            target_path = _safe_lora_path(filename)

            dl_name = os.path.basename(filename)



        if target_path and os.path.isfile(target_path):

            try:

                file_size = os.path.getsize(target_path)

                self.send_response(200)

                self.send_header('Content-Type', 'application/octet-stream')

                self.send_header('Content-Disposition', f'attachment; filename="{dl_name}"')

                self.send_header('Content-Length', str(file_size))

                self.send_header('Access-Control-Allow-Origin', '*')

                self.send_header('Accept-Ranges', 'bytes')

                self.end_headers()

                with open(target_path, 'rb') as fh:

                    while True:

                        chunk = fh.read(1024 * 1024)

                        if not chunk:

                            break

                        self.wfile.write(chunk)

                return

            except Exception as e:

                self.send_error_response(500, f"Error reading file: {e}")

                return



        if target_url and target_url.startswith('https://'):

            try:

                r = requests.get(target_url, stream=True, timeout=120)

                if r.status_code == 200:

                    self.send_response(200)

                    self.send_header('Content-Type', 'application/octet-stream')

                    self.send_header('Content-Disposition', f'attachment; filename="{dl_name}"')

                    if 'content-length' in r.headers:

                        self.send_header('Content-Length', r.headers['content-length'])

                    self.send_header('Access-Control-Allow-Origin', '*')

                    self.end_headers()

                    for chunk in r.iter_content(chunk_size=1024 * 1024):

                        if chunk:

                            self.wfile.write(chunk)

                    return

            except Exception as e:

                print(f"[LoRA Download] Stream error: {e}")



        self.send_error_response(404, "ملف أوزان LoRA غير متوفر للتنزيل.")



    def handle_lora_train(self, payload):

        model_name = (payload.get('model_name') or 'Custom LoRA').strip()

        trigger_word = (payload.get('trigger_word') or 'cindy_lora').strip()

        trigger_word = re.sub(r'[^A-Za-z0-9_]', '_', trigger_word).lower()

        is_style = bool(payload.get('is_style', False))

        steps = int(payload.get('steps', 1000) or 1000)

        steps = max(500, min(steps, 2500))

        images = payload.get('images', [])

        zip_b64 = payload.get('zip_b64', '')

        auto_caption = bool(payload.get('auto_caption', False))



        secrets = load_secrets()

        fal_key = secrets.get('fal_api_key', '')

        gemini_key = secrets.get('gemini_api_key', '')

        if not fal_key:

            self.send_error_response(400, "مفتاح Fal.ai مطلوب في الخزنة لتشغيل تدريب LoRA.")

            return



        if not images and not zip_b64:

            self.send_error_response(400, "يرجى تقديم صور التدريب (على الأقل 4 صور).")

            return



        # Build in-memory dataset ZIP

        zip_buf = io.BytesIO()

        if zip_b64:

            try:

                zip_bytes = base64.b64decode(zip_b64.split(';base64,')[-1])

                zip_buf.write(zip_bytes)

            except Exception:

                self.send_error_response(400, "ملف zip غير صالح.")

                return

        else:

            # Parse images

            parsed_items = []

            for idx, im_item in enumerate(images):

                data_str = im_item.get('data') if isinstance(im_item, dict) else im_item

                if not data_str or ';base64,' not in data_str:

                    continue

                header, b64 = data_str.split(';base64,', 1)

                try:

                    raw = base64.b64decode(b64)

                    ext = 'png' if 'png' in header else 'jpg'

                    mime = 'image/png' if ext == 'png' else 'image/jpeg'

                    im_name = f"image_{idx+1:02d}.{ext}"

                    caption = (im_item.get('caption') if isinstance(im_item, dict) else '') or ''

                    parsed_items.append({

                        "idx": idx,

                        "im_name": im_name,

                        "raw": raw,

                        "b64": b64,

                        "mime": mime,

                        "caption": caption

                    })

                except Exception:

                    continue



            # Parallel Gemini Vision auto-captioning

            if auto_caption and gemini_key and parsed_items:

                def _cap_worker(item):

                    if item["caption"]:

                        return item["idx"], item["caption"]

                    try:

                        g_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={gemini_key}"

                        c_prompt = f"Provide a single concise English descriptive caption for this training image. Begin with or include trigger word '{trigger_word}'."

                        g_body = {"contents": [{"parts": [{"text": c_prompt}, {"inlineData": {"mimeType": item["mime"], "data": item["b64"]}}]}]}

                        g_res = requests.post(g_url, json=g_body, timeout=8)

                        if g_res.status_code == 200:

                            cand = g_res.json().get('candidates', [])

                            if cand:

                                txt = cand[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()

                                if txt:

                                    return item["idx"], txt

                    except Exception:

                        pass

                    fallback = f"{trigger_word}, high resolution photorealistic portrait, cinematic 8k" if not is_style else f"in the style of {trigger_word}, cinematic visual style"

                    return item["idx"], fallback



                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:

                    cap_results = dict(executor.map(_cap_worker, parsed_items))

                for item in parsed_items:

                    item["caption"] = cap_results.get(item["idx"])



            # Write dataset zip

            with zipfile.ZipFile(zip_buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:

                for item in parsed_items:

                    zf.writestr(item["im_name"], item["raw"])

                    cap_text = item["caption"] or (f"{trigger_word}, high resolution photorealistic portrait, cinematic 8k" if not is_style else f"in the style of {trigger_word}, cinematic visual style")

                    zf.writestr(f"image_{item['idx']+1:02d}.txt", cap_text)



        zip_bytes = zip_buf.getvalue()

        if len(zip_bytes) < 500:

            self.send_error_response(400, "حجم حزمة صور التدريب صغير جداً أو تالف.")

            return



        # Upload dataset zip to Fal CDN storage

        try:

            init_headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json", "Accept": "application/json"}

            init_res = requests.post(

                "https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",

                headers=init_headers,

                json={"file_name": f"{trigger_word}_dataset.zip", "content_type": "application/zip"},

                timeout=20

            )

            if init_res.status_code != 200:

                self.send_error_response(init_res.status_code, f"فشل رفع بيانات التدريب: {init_res.text[:200]}")

                return

            init_data = init_res.json()

            up_url = init_data.get('upload_url')

            uploaded_zip_url = init_data.get('file_url')

            put_res = requests.put(up_url, data=zip_bytes, headers={"Content-Type": "application/zip"}, timeout=90)

            if put_res.status_code not in (200, 201):

                self.send_error_response(put_res.status_code, "فشل إرسال ملف البيانات إلى خادم التدريب السحابي.")

                return

        except Exception as e:

            self.send_error_response(500, f"Upload error: {e}")

            return



                # Check if RunPod backend is available or requested

        rp_key = secrets.get('runpod_api_key', '').strip()

        hf_token = secrets.get('huggingface_api_key', '').strip()

        use_runpod = bool(rp_key) or payload.get('backend') == 'runpod'



        if use_runpod:

            if not rp_key:

                self.send_error_response(400, "مفتاح RunPod API مطلوب لبدء التدريب السحابي.")

                return

            if not hf_token:

                self.send_error_response(400, "مفتاح Hugging Face مطلوب في الخزنة لتحميل أوزان نموذج FLUX.1-dev.")

                return



            gpu_type = payload.get('gpu_type') or None  # None activates the Cheapest-First Cascade

            job_id = f"rp_{int(time.time())}_{trigger_word[:8]}"

            job_record = {

                "id": job_id,

                "model_name": model_name,

                "trigger_word": trigger_word,

                "is_style": is_style,

                "steps": steps,

                "status": "IN_QUEUE",

                "progress": 5,

                "start_time": time.time(),

                "logs": ["تم تجهيز حزمة التدريب بنجاح.", f"جاري تشغيل كمبيوتر RunPod السحابي ({gpu_type})..."],

                "weights_url": None,

                "local_file": None,

                "engine": "runpod",

                "gpu_display": gpu_type

            }

            LORA_TRAINING_JOBS[job_id] = job_record



            def _runpod_worker():

                runpod_trainer.run_training_job(

                    job=job_record,

                    api_key=rp_key,

                    hf_token=hf_token,

                    data_url=uploaded_zip_url,

                    gpu_id=gpu_type,

                    upload_fn=_upload_lora_to_fal,

                    register_fn=_register_trained_lora,

                    loras_dir=LORAS_DIR,

                    max_minutes=90

                )



            threading.Thread(target=_runpod_worker, daemon=True).start()



            self.send_json_response(200, {

                "success": True,

                "job_id": job_id,

                "model_name": model_name,

                "trigger_word": trigger_word,

                "engine": "runpod",

                "status": "IN_QUEUE",

                "message": f"تم إطلاق كمبيوتر RunPod السحابي ({gpu_type}) للتدريب! سيتم إيقاف وحذف الجهاز تلقائياً فور الانتهاء لتوفير رصيدك."

            })

            return



        # Fallback to Fal.ai training queue

# Submit training job to fal-ai/flux-lora-fast-training

        train_body = {

            "images_data_url": uploaded_zip_url,

            "trigger_word": trigger_word,

            "is_style": is_style,

            "steps": steps

        }



        try:

            sub_res = requests.post(

                "https://queue.fal.run/fal-ai/flux-lora-fast-training",

                headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"},

                json=train_body,

                timeout=30

            )

            if sub_res.status_code not in (200, 201, 202):

                self.send_error_response(sub_res.status_code, f"فشل بدء التدريب في Fal: {sub_res.text[:300]}")

                return

            job_data = sub_res.json()

            request_id = job_data.get('request_id')

            status_url = job_data.get('status_url')

            response_url = job_data.get('response_url')

        except Exception as e:

            self.send_error_response(500, f"Training queue error: {e}")

            return



        # Record in in-memory tracker

        job_record = {

            "id": request_id,

            "model_name": model_name,

            "trigger_word": trigger_word,

            "is_style": is_style,

            "steps": steps,

            "status": "IN_QUEUE",

            "status_url": status_url,

            "response_url": response_url,

            "start_time": time.time(),

            "logs": ["تم إرسال حزمة التدريب بنجاح إلى سيرفرات التدريب السحابية."],

            "weights_url": None,

            "local_file": None

        }

        LORA_TRAINING_JOBS[request_id] = job_record



        # Launch background poller thread

        import threading

        t = threading.Thread(

            target=self._poll_lora_training_worker,

            args=(request_id, status_url, response_url, job_record, fal_key),

            daemon=True

        )

        t.start()



        self.send_json_response(200, {

            "success": True,

            "job_id": request_id,

            "model_name": model_name,

            "trigger_word": trigger_word,

            "status": "IN_QUEUE",

            "message": "بدأ تدريب الـ LoRA بنجاح! سيستغرق التدريب من 2 إلى 4 دقائق على كروت GPU السحابية."

        })



    def _poll_lora_training_worker(self, request_id, status_url, response_url, job_record, fal_key):

        headers = {"Authorization": f"Key {fal_key}"}

        for _ in range(180): # up to 15 mins

            time.sleep(5)

            try:

                st_res = requests.get(status_url, headers=headers, timeout=15)

                if st_res.status_code == 200:

                    st_data = st_res.json()

                    status = st_data.get('status', 'IN_PROGRESS')

                    job_record['status'] = status

                    if st_data.get('logs'):

                        job_record['logs'] = [l.get('message', str(l)) for l in st_data['logs']][-8:]

                    

                    if status == 'COMPLETED':

                        # Fetch final response

                        res_resp = requests.get(response_url, headers=headers, timeout=30)

                        if res_resp.status_code == 200:

                            res_json = res_resp.json()

                            diff_file = res_json.get('diffusers_lora_file') or {}

                            w_url = diff_file.get('url')

                            if w_url:

                                job_record['weights_url'] = w_url

                                job_record['file_size'] = diff_file.get('file_size', 0)



                                # Download local copy to outputs/loras/

                                safe_tw = re.sub(r'[^A-Za-z0-9_]', '_', job_record['trigger_word'])

                                fname = f"{safe_tw}_{request_id[:6]}.safetensors"

                                local_fpath = os.path.join(LORAS_DIR, fname)

                                try:

                                    dl_r = requests.get(w_url, headers=headers, timeout=120)

                                    if dl_r.status_code == 200:

                                        with open(local_fpath, 'wb') as lfh:

                                            lfh.write(dl_r.content)

                                        job_record['local_file'] = fname

                                except Exception:

                                    pass



                                # Register in cindy_loras.json

                                loras = load_loras()

                                new_entry = {

                                    "id": request_id,

                                    "model_name": job_record['model_name'],

                                    "trigger_word": job_record['trigger_word'],

                                    "is_style": job_record['is_style'],

                                    "steps": job_record['steps'],

                                    "weights_url": w_url,

                                    "local_file": job_record.get('local_file'),

                                    "file_size": diff_file.get('file_size', 0),

                                    "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),

                                    "status": "ready"

                                }

                                loras.insert(0, new_entry)

                                save_loras(loras)

                        return

                    elif status in ('FAILED', 'CANCELLED'):

                        job_record['status'] = status

                        job_record['error'] = st_data.get('error', 'Training failed on cloud server.')

                        return

            except Exception as e:

                job_record['logs'].append(f"Connection retry: {e}")



    def handle_lora_execute(self, payload):

        lora_id = payload.get('lora_id', '')

        safetensors_url = payload.get('safetensors_url', '')

        prompt = (payload.get('prompt') or '').strip()

        scale = float(payload.get('scale', 1.0) or 1.0)

        aspect_ratio = payload.get('aspect_ratio', 'landscape_16_9')

        num_images = min(max(int(payload.get('num_images', 1) or 1), 1), 4)

        media_type = payload.get('media_type', 'image')

        video_engine = payload.get('video_engine', 'kling-1.6-pro')

        duration = int(payload.get('duration', 5) or 5)

        motion_prompt = (payload.get('motion_prompt') or '').strip()



        if not safetensors_url and lora_id:

            loras = load_loras()

            match = next((l for l in loras if l.get('id') == lora_id), None)

            if match:

                safetensors_url = match.get('weights_url')

                tw = match.get('trigger_word', '')

                if tw and tw.lower() not in prompt.lower():

                    prompt = f"{tw}, {prompt}"



        if not safetensors_url:

            self.send_error_response(400, "يرجى اختيار نموذج LoRA صالح أو رابط أوزان (.safetensors).")

            return



        secrets = load_secrets()

        fal_key = secrets.get('fal_api_key', '')

        if not fal_key:

            self.send_error_response(400, "مفتاح Fal.ai مطلوب في الخزنة لتوليد لقطات LoRA.")

            return



        # Translate prompt via Cross-Lingual Transmutation (Arabic, French, Spanish)

        translated_prompt = self._translate_text_to_english(prompt, mode='image')



        # 1. Generate Keyframe using FLUX.1 LoRA

        req_body = {

            "prompt": translated_prompt,

            "loras": [

                {

                    "path": safetensors_url,

                    "scale": scale

                }

            ],

            "image_size": aspect_ratio,

            "num_images": 1 if media_type == 'video' else num_images,

            "enable_safety_checker": False

        }



        try:

            sub_res = requests.post(

                "https://queue.fal.run/fal-ai/flux-lora",

                headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"},

                json=req_body,

                timeout=30

            )

            if sub_res.status_code not in (200, 201, 202):

                self.send_error_response(sub_res.status_code, f"خطأ في إرسال طلب التوليد: {sub_res.text[:300]}")

                return

            q_data = sub_res.json()

            status_url = q_data.get('status_url')

            response_url = q_data.get('response_url')



            images_list = []

            for _ in range(45):

                time.sleep(2)

                st = requests.get(status_url, headers={"Authorization": f"Key {fal_key}"}, timeout=15).json()

                if st.get('status') == 'COMPLETED':

                    res = requests.get(response_url, headers={"Authorization": f"Key {fal_key}"}, timeout=20).json()

                    imgs = res.get('images', [])

                    images_list = [{"url": im.get('url', '')} for im in imgs if im.get('url')]

                    break

                elif st.get('status') in ('FAILED', 'CANCELLED'):

                    self.send_error_response(500, "فشل التوليد في الخادم السحابي.")

                    return



            if not images_list:

                self.send_error_response(504, "تجاوزت عملية التوليد الوقت المحدد.")

                return



            if media_type != 'video':

                self.send_json_response(200, {

                    "success": True,

                    "media_type": "image",

                    "url": images_list[0]['url'],

                    "images": images_list,

                    "prompt": prompt,

                    "lora_scale": scale,

                    "message": f"تم التوليد بنجاح بنموذج LoRA ({len(images_list)} صور)!"

                })

                return



            # 2. Animate Keyframe using SOTA Image-to-Video Engine

            keyframe_url = images_list[0]['url']

            vid_prompt = translated_prompt

            if motion_prompt:

                motion_prompt = self._translate_text_to_english(motion_prompt, mode='video')

                vid_prompt = f"{translated_prompt}, {motion_prompt}"



            ar_map = {

                'landscape_16_9': '16:9',

                'portrait_9_16': '9:16',

                'square_hd': '1:1',

                'landscape_21_9': '21:9'

            }

            target_ar = ar_map.get(aspect_ratio, '16:9')



            if 'minimax' in video_engine:

                video_ep = "fal-ai/minimax/video-01/image-to-video"

                v_body = {

                    "prompt": vid_prompt,

                    "first_frame_image": keyframe_url

                }

            elif 'luma' in video_engine:

                video_ep = "fal-ai/luma-dream-machine/ray-2/image-to-video"

                app_dur = 9 if duration >= 8 else 5

                v_body = {

                    "prompt": vid_prompt,

                    "image_url": keyframe_url,

                    "duration": f"{app_dur}s",

                    "aspect_ratio": target_ar

                }

            else: # Kling default

                video_ep = "fal-ai/kling-video/v1.6/pro/image-to-video"

                app_dur = 10 if duration >= 8 else 5

                v_body = {

                    "prompt": vid_prompt,

                    "image_url": keyframe_url,

                    "duration": str(app_dur),

                    "aspect_ratio": target_ar if target_ar in ('16:9', '9:16', '1:1') else '16:9'

                }



            v_sub = requests.post(

                f"https://queue.fal.run/{video_ep}",

                headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"},

                json=v_body,

                timeout=30

            )

            if v_sub.status_code not in (200, 201, 202):

                self.send_error_response(v_sub.status_code, f"فشل إرسال طلب تحريك الفيديو: {v_sub.text[:300]}")

                return



            v_data = v_sub.json()

            v_status_url = v_data.get('status_url')

            v_response_url = v_data.get('response_url')



            for _ in range(60):

                time.sleep(3)

                v_st = requests.get(v_status_url, headers={"Authorization": f"Key {fal_key}"}, timeout=15).json()

                if v_st.get('status') == 'COMPLETED':

                    v_res = requests.get(v_response_url, headers={"Authorization": f"Key {fal_key}"}, timeout=20).json()

                    v_url = (v_res.get('video') or {}).get('url') or v_res.get('url') or ''

                    if v_url:

                        self.send_json_response(200, {

                            "success": True,

                            "media_type": "video",

                            "url": v_url,

                            "keyframe_url": keyframe_url,

                            "video_engine": video_engine,

                            "duration": duration,

                            "prompt": prompt,

                            "message": "تم إنتاج مشهد الفيديو بنجاح بنموذج LoRA!"

                        })

                        return

                    break

                elif v_st.get('status') in ('FAILED', 'CANCELLED'):

                    self.send_error_response(500, "فشل تحريك الفيديو في الخادم السحابي.")

                    return



            self.send_error_response(504, "تجاوزت عملية تحريك الفيديو الوقت المسموح.")

        except Exception as e:

            self.send_error_response(500, f"Inference error: {e}")



    def handle_lora_upload(self, payload):
        """
        Uploads a local .safetensors LoRA file to Fal CDN storage once.
        Registers the resulting URL in Cindy's LoRA library so it can be reused infinitely
        without ever re-uploading from the user's computer.
        """
        name = (payload.get('model_name') or 'Actor LoRA').strip()
        tw = (payload.get('trigger_word') or 'cindy_actor').strip()
        filename = payload.get('filename', 'actor_lora.safetensors')
        b64data = payload.get('data', '')

        if not b64data:
            self.send_error_response(400, "لم يتم استلام بيانات ملف الـ LoRA.")
            return

        try:
            if ';base64,' in b64data:
                b64data = b64data.split(';base64,', 1)[1]
            raw_bytes = base64.b64decode(b64data)
        except Exception as e:
            self.send_error_response(400, f"فشل فك ترميز الملف: {e}")
            return

        # Save locally in lora storage first
        lora_dir = os.path.join(OUTPUTS_DIR, "loras")
        os.makedirs(lora_dir, exist_ok=True)
        safe_fname = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        if not safe_fname.endswith('.safetensors'):
            safe_fname += '.safetensors'
        local_path = os.path.join(lora_dir, safe_fname)
        with open(local_path, "wb") as f_out:
            f_out.write(raw_bytes)

        secrets = load_secrets()
        fal_key = secrets.get('fal_api_key', '')
        cloud_url = None

        if fal_key:
            cloud_url = _upload_lora_to_fal_cdn(local_path, fal_key)

        final_url = cloud_url or f"/outputs/loras/{safe_fname}"
        file_sz = len(raw_bytes)

        loras = load_loras()
        item_id = f"uploaded_{int(time.time())}"
        new_entry = {
            "id": item_id,
            "model_name": name,
            "trigger_word": tw,
            "is_style": False,
            "steps": 1000,
            "weights_url": final_url,
            "local_file": safe_fname,
            "file_size": file_sz,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": "ready",
            "is_imported": True
        }
        loras.insert(0, new_entry)
        save_loras(loras)

        self.send_json_response(200, {
            "success": True,
            "lora": new_entry,
            "cloud_url": final_url,
            "message": f"تم رفع وتخزين ملف الـ LoRA سحابياً بنجاح بحجم {file_sz // (1024*1024)} ميجابايت! أصبح جاهزاً للاستخدام الدائم بضغطة زر."
        })

    def handle_lora_import(self, payload):

        name = (payload.get('model_name') or 'External LoRA').strip()

        tw = (payload.get('trigger_word') or 'lora_char').strip()

        url = (payload.get('url') or '').strip()

        is_style = bool(payload.get('is_style', False))



        if not url or not url.startswith('https://'):

            self.send_error_response(400, "يرجى تقديم رابط مباشر صالح لملف .safetensors (HTTPS).")

            return



        loras = load_loras()

        item_id = f"ext_{int(time.time())}"

        new_entry = {

            "id": item_id,

            "model_name": name,

            "trigger_word": tw,

            "is_style": is_style,

            "steps": 1000,

            "weights_url": url,

            "local_file": None,

            "file_size": 0,

            "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),

            "status": "ready",

            "is_imported": True

        }

        loras.insert(0, new_entry)

        save_loras(loras)

        self.send_json_response(200, {"success": True, "lora": new_entry, "message": "تم استيراد الـ LoRA بنجاح وإضافته إلى مكتبتك!"})



    def handle_lora_delete(self, payload):

        lora_id = payload.get('id', '')

        loras = load_loras()

        match = next((l for l in loras if l.get('id') == lora_id), None)

        if not match:

            self.send_error_response(404, "النموذج غير موجود.")

            return

        # Delete local safetensors if exists

        if match.get('local_file'):

            lp = _safe_lora_path(match['local_file'])

            if lp and os.path.isfile(lp):

                try: os.remove(lp)

                except Exception: pass

        loras = [l for l in loras if l.get('id') != lora_id]

        save_loras(loras)

        self.send_json_response(200, {"success": True, "message": "تم حذف النموذج بنجاح."})





    def handle_edit_media_poll(self):

        parsed = urllib.parse.urlparse(self.path)

        qs = urllib.parse.parse_qs(parsed.query)

        status_url = (qs.get('status_url', [''])[0] or '').strip()

        response_url = (qs.get('response_url', [''])[0] or '').strip()



        if not status_url:

            self.send_error_response(400, "status_url required")

            return



        secrets = load_secrets()

        fal_key = secrets.get('fal_api_key', '')

        headers = {"Authorization": f"Key {fal_key}"}



        try:

            poll_res = requests.get(status_url, headers=headers, timeout=15)

            if poll_res.status_code == 200:

                p_data = poll_res.json()

                st = p_data.get('status')

                if st == 'COMPLETED':

                    video_url = _extract_media_url(p_data)

                    if not video_url and response_url:

                        final_res = requests.get(response_url, headers=headers, timeout=20)

                        if final_res.status_code == 200:

                            video_url = _extract_media_url(final_res.json())

                    if video_url:

                        self.send_json_response(200, {

                            "success": True,

                            "completed": True,

                            "media_type": "video",

                            "url": video_url,

                            "message": "اكتمل ريندر الفيديو بنجاح!"

                        })

                        return

                    else:

                        self.send_error_response(500, "اكتمل الريندر لكن تعذر استخراج رابط الفيديو.")

                        return

                elif st in ('FAILED', 'CANCELLED'):

                    self.send_error_response(500, f"فشل الريندر السحابي: {p_data.get('error')}")

                    return

                else:

                    self.send_json_response(200, {

                        "success": True,

                        "completed": False,

                        "status": st,

                        "message": "جاري الريندر..."

                    })

                    return

            self.send_error_response(poll_res.status_code, "فشل فحص حالة الريندر السحابي.")

        except Exception as e:

            self.send_error_response(500, f"خطأ فحص الطابور: {e}")





    def handle_comfyui_status(self):

        secrets = load_secrets()

        url = secrets.get('local_comfyui_url', '').strip()

        if not url:

            self.send_json_response(200, {

                "configured": False,

                "online": False,

                "url": "",

                "message": "لم يتم ربط ComfyUI بعد (يمكنك إدخال رابط محلي أو تشغيل استوديو سحابي بنقرة واحدة)."

            })

            return

        

        status = comfyui_client.check_comfyui_connection(url)

        resources = comfyui_client.get_available_resources(url) if status.get("online") else {}

        self.send_json_response(200, {

            "configured": True,

            "online": status.get("online", False),

            "url": url,

            "stats": status,

            "resources": resources,

            "message": status.get("message") or status.get("error")

        })



    def handle_comfyui_connect(self, payload):

        url = (payload.get('url') or '').strip().rstrip('/')

        if not url:

            self.send_error_response(400, "يرجى إدخال رابط ComfyUI صالح (مثلاً: http://127.0.0.1:8188).")

            return

        

        status = comfyui_client.check_comfyui_connection(url)

        if not status.get("online"):

            self.send_error_response(400, f"فشل الاتصال بهذا الرابط: {status.get('error')}")

            return

        

        secrets = load_secrets()

        secrets['local_comfyui_url'] = url

        save_secrets(secrets)

        

        resources = comfyui_client.get_available_resources(url)

        self.send_json_response(200, {

            "success": True,

            "online": True,

            "url": url,

            "stats": status,

            "resources": resources,

            "message": f"تم الاتصال بـ ComfyUI بنجاح! ({status.get('gpu', 'GPU')})"

        })



    def handle_comfyui_launch(self, payload):

        secrets = load_secrets()

        api_key = secrets.get('runpod_api_key', '').strip()

        if not api_key:

            self.send_error_response(400, "مفتاح RunPod API مطلوب في الخزنة لتشغيل استوديو ComfyUI السحابي.")

            return

        

        gpu_type = payload.get('gpu_type') or None  # None activates the Cheapest-First Cascade

        try:

            pod_info = comfyui_client.launch_runpod_comfyui_pod(api_key, gpu_type)

            secrets['local_comfyui_url'] = pod_info['comfyui_url']

            save_secrets(secrets)

            self.send_json_response(200, pod_info)

        except Exception as e:

            self.send_error_response(500, f"فشل تشغيل ComfyUI على RunPod: {str(e)}")



    def handle_comfyui_stop(self, payload):
        secrets = load_secrets()
        api_key = secrets.get('runpod_api_key', '').strip()
        pod_id = payload.get('pod_id')
        action = payload.get('action', 'stop')
        if not api_key:
            self.send_error_response(400, "مفتاح RunPod مطلوب.")
            return

        if action in ('terminate', 'terminate_all'):
            # Query all pods and terminate all active
            q = "query { myself { pods { id name desiredStatus } } }"
            res = _runpod_graphql(q, api_key)
            pods = res.get("data", {}).get("myself", {}).get("pods", [])
            terminated = []
            for p in pods:
                pid = p.get('id')
                term_mut = f'mutation {{ podTerminate(input: {{podId: "{pid}"}}) }}'
                _runpod_graphql(term_mut, api_key)
                terminated.append(pid)
            ok = True
            msg = f"تم إيقاف وحذف {len(terminated)} سيرفر سحابي فوراً لحماية رصيدك بالكامل!"
        else:
            ok = comfyui_client.stop_runpod_pod(api_key, pod_id)
            msg = "تم إيقاف كرت الشاشة السحابي مؤقتاً (Stop/Pause) ووقف استهلاك الرصيد فوراً إلى $0.00!"

        self.send_json_response(200, {
            "success": ok,
            "message": msg
        })

    def handle_pricing_daily(self, force_refresh=False):
        try:
            from cindy_pricing import build_daily_pricing_report
            report = build_daily_pricing_report(force_refresh=force_refresh)
            self.send_json_response(200, {
                "success": True,
                "pricing": report
            })
        except Exception as e:
            self.send_json_response(500, {
                "success": False,
                "error": str(e)
            })

    def handle_wallet_status(self):

        secrets = load_secrets()

        runpod_key = secrets.get('runpod_api_key', '').strip()

        fal_key = secrets.get('fal_api_key', '').strip()



        wallet = {

            "runpod": {"connected": False, "balance": 0.0, "spend_per_hr": 0.0, "currency": "USD", "status": "غير مربوط"},

            "fal": {"connected": False, "balance": None, "currency": "USD", "status": "غير مربوط"}

        }



        # 1. RunPod Live Balance & Burn Rate

        if runpod_key:

            query = """
            query {
                myself {
                    clientBalance
                    currentSpendPerHr
                    pods {
                        id
                        name
                        desiredStatus
                    }
                }
            }
            """

            try:

                r = requests.post(

                    'https://api.runpod.io/graphql',

                    headers={'Authorization': f'Bearer {runpod_key}', 'Content-Type': 'application/json'},

                    json={'query': query},

                    timeout=8

                )

                if r.status_code == 200:

                    data = r.json().get('data', {}).get('myself', {})

                    bal = data.get('clientBalance', 0.0)
                    spend = data.get('currentSpendPerHr', 0.0)
                    pods_raw = data.get('pods', [])
                    active_pods = [p for p in pods_raw if p.get('desiredStatus') != 'TERMINATED']
                    wallet["runpod"] = {
                        "connected": True,
                        "balance": round(float(bal), 2),
                        "spend_per_hr": round(float(spend), 3),
                        "currency": "USD",
                        "active_pods": len(active_pods),
                        "status": f"${round(float(bal), 2)} (استهلاك: ${round(float(spend), 3)}/س)"
                    }

                else:

                    wallet["runpod"]["status"] = f"استجاب السيرفر بكود {r.status_code}"

            except Exception as e:

                wallet["runpod"]["status"] = f"خطأ: {str(e)[:60]}"



        # 2. Fal.ai Live Status & Key Scope

        if fal_key:

            try:

                headers = {'Authorization': f'Key {fal_key}'}

                r = requests.get('https://rest.alpha.fal.ai/users/current', headers=headers, timeout=6)

                if r.status_code == 200:

                    f_data = r.json()

                    wallet["fal"] = {

                        "connected": True,

                        "balance": f_data.get('balance'),

                        "currency": "USD",

                        "status": f"متصل ونشط (${f_data.get('balance', 0.0)})"

                    }

                elif r.status_code == 403:

                    wallet["fal"] = {

                        "connected": True,

                        "balance": None,

                        "currency": "USD",

                        "status": "مفتاح توليد جاهز (نشط)",

                        "note": "لإظهار الرصيد بالدولار، امنح المفتاح صلاحية 'account:settings:read' من fal.ai/dashboard/keys"

                    }

                else:

                    wallet["fal"] = {

                        "connected": True,

                        "balance": None,

                        "currency": "USD",

                        "status": f"متصل (كود {r.status_code})"

                    }

            except Exception as e:

                wallet["fal"]["status"] = f"خطأ: {str(e)[:60]}"



        self.send_json_response(200, {"success": True, "wallet": wallet})



    

    def handle_comfyui_motion_control(self, payload):

        update_comfy_activity()

        source_img = (payload.get('source_image') or '').strip()

        driving_vid = (payload.get('driving_video') or '').strip()

        

        if not source_img:

            self.send_error_response(400, "يرجى اختيار أو رفع صورة الشخصية أولاً.")

            return

        if not driving_vid:

            self.send_error_response(400, "يرجى اختيار أو رفع فيديو تعابير الوجه التوجيهي (Driving Video).")

            return

            

        secrets = load_secrets()

        fal_key = secrets.get('fal_api_key', '').strip()

        if not fal_key:

            self.send_error_response(400, "مفتاح Fal AI مطلوب لتشغيل Kling Motion Control.")

            return

            

        # 1. Resolve URLs

        img_url = source_img

        if not source_img.startswith('http'):

            img_url = upload_file_to_fal(source_img, fal_key) or source_img

            

        vid_url = driving_vid

        if not driving_vid.startswith('http'):

            vid_url = upload_file_to_fal(driving_vid, fal_key) or driving_vid

            

        headers = {'Authorization': f'Key {fal_key}', 'Content-Type': 'application/json'}

        engine = "kling"
        engine_label = "Kling Motion Control (1080p)"



        # Engine B: Kling Motion Control v3 (Cinema Grade 1080p without any jitter)

        if engine == 'kling':

            kling_url = 'https://queue.fal.run/fal-ai/kling-video/v3/standard/motion-control'

            req_body = {

                'image_url': img_url,

                'video_url': vid_url,

                'character_orientation': 'video'

            }

            try:

                r = requests.post(kling_url, headers=headers, json=req_body, timeout=20)

                if r.status_code != 200:

                    self.send_error_response(500, f"فشل بدء ريندر Kling: {r.text[:200]}")

                    return

                queue_info = r.json()

                status_url = queue_info.get('status_url')

                resp_url = queue_info.get('response_url')

                start_t = time.time()

                video_url = None

                while time.time() - start_t < 360:

                    time.sleep(4)

                    st_res = requests.get(status_url, headers=headers, timeout=10)

                    if st_res.status_code == 200:

                        st_data = st_res.json()

                        st = st_data.get('status')

                        if st == 'COMPLETED':

                            final_res = requests.get(resp_url, headers=headers, timeout=15)

                            video_url = final_res.json().get('video', {}).get('url')

                            break

                        elif st == 'FAILED':

                            self.send_error_response(500, "فشلت معالجة مشهد Kling على السيرفر.")

                            return

                if not video_url:

                    self.send_error_response(504, "انتهت مهلة ريندر Kling.")

                    return

                v_bytes = requests.get(video_url, timeout=30).content

                fname = f"Kling_Motion_{int(time.time()*1000)}.mp4"

                fpath = os.path.join(OUTPUTS_DIR, fname)

                with open(fpath, 'wb') as f:

                    f.write(v_bytes)

                self.send_json_response(200, {

                    "success": True,

                    "url": f"/outputs/{fname}",

                    "filename": fname,

                    "media_type": "video",

                    "engine": "kling",

                    "message": "تم ريندر مشهد Kling السينمائي 1080p بنجاح فائق بدون أي هزة!"

                })

                return

            except Exception as e:

                self.send_error_response(500, f"خطأ أثناء ريندر Kling: {str(e)}")

                return



    def handle_comfyui_latentsync(self, payload):

        update_comfy_activity()

        video_src = (payload.get('video_source') or '').strip()

        audio_src = (payload.get('audio_source') or '').strip()

        

        if not video_src:

            self.send_error_response(400, "يرجى اختيار أو رفع كادر أو فيديو الشخصية أولاً.")

            return

        if not audio_src:

            self.send_error_response(400, "يرجى اختيار أو رفع ملف الصوت/الحوار (Audio Track).")

            return

            

        secrets = load_secrets()

        fal_key = secrets.get('fal_api_key', '').strip()

        if not fal_key:

            self.send_error_response(400, "مفتاح Fal AI مطلوب لتشغيل محرك LatentSync.")

            return

            

        # Resolve URLs

        vid_url = video_src

        if not video_src.startswith('http'):

            vid_url = upload_file_to_fal(video_src, fal_key) or video_src

            

        aud_url = audio_src

        if not audio_src.startswith('http'):

            aud_url = upload_file_to_fal(audio_src, fal_key) or audio_src

            

        headers = {'Authorization': f'Key {fal_key}', 'Content-Type': 'application/json'}

        req_body = {

            'video_url': vid_url,

            'audio_url': aud_url

        }

        

        try:

            r = requests.post('https://queue.fal.run/fal-ai/latentsync', headers=headers, json=req_body, timeout=20)

            if r.status_code != 200:

                self.send_error_response(500, f"فشل بدء ريندر LatentSync: {r.text[:200]}")

                return

                

            queue_info = r.json()

            status_url = queue_info.get('status_url')

            resp_url = queue_info.get('response_url')

            

            start_t = time.time()

            video_url = None

            while time.time() - start_t < 180:

                time.sleep(2.5)

                st_res = requests.get(status_url, headers=headers, timeout=10)

                if st_res.status_code == 200:

                    status = st_res.json().get('status')

                    if status == 'COMPLETED':

                        final_res = requests.get(resp_url, headers=headers, timeout=15)

                        video_url = final_res.json().get('video', {}).get('url')

                        break

                    elif status == 'FAILED':

                        self.send_error_response(500, "فشلت معالجة مزامنة الشفاه.")

                        return

                        

            if not video_url:

                self.send_error_response(504, "انتهت مهلة ريندر مزامنة الشفاه.")

                return

                

            v_bytes = requests.get(video_url, timeout=30).content

            fname = f"LatentSync_{int(time.time()*1000)}.mp4"

            fpath = os.path.join(OUTPUTS_DIR, fname)

            with open(fpath, 'wb') as f:

                f.write(v_bytes)

                

            self.send_json_response(200, {

                "success": True,

                "url": f"/outputs/{fname}",

                "filename": fname,

                "media_type": "video",

                "message": "تمت مزامنة ونطق الشفاه بنجاح!"

            })

        except Exception as e:

            self.send_error_response(500, f"خطأ أثناء تنفيذ LatentSync: {str(e)}")



    def handle_comfyui_generate_video(self, payload):
        secrets = load_secrets()
        fal_key = secrets.get('fal_api_key', '').strip()
        raw_url = secrets.get('local_comfyui_url', '').strip()

        image_url = (payload.get('image_url') or '').strip()
        if not image_url:
            self.send_error_response(400, "يرجى تحديد كادر الصورة المراد تحريكها.")
            return

        # Extract video parameters
        ckpt = payload.get('checkpoint', 'Wan2.1/wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors')
        ckpt_lower = str(ckpt).lower()
        width = int(payload.get('width', 1024))
        height = int(payload.get('height', 576))
        video_frames = int(payload.get('video_frames', 81))
        motion_bucket_id = int(payload.get('motion_bucket_id', 127))
        fps = int(payload.get('fps', 12))
        steps = int(payload.get('steps', 20))
        auto_stop = bool(payload.get('auto_stop', True))
        prompt_text = (payload.get('prompt', 'A cinematic sequence with dynamic camera movement') or "cinematic camera movement, high resolution").strip()

        job_id = f"vid_{int(time.time() * 1000)}"
        VIDEO_JOBS[job_id] = {
            "status": "processing",
            "progress": 15,
            "message": "جاري تجهيز الكادر المرجعي والاتصال بمحرك الفيديو...",
            "created_at": time.time()
        }

        def _bg_render():
            try:
                # 1. Robust path resolution with Smart Token Fuzzy Matcher
                clean_img = image_url.split('?')[0].strip().rstrip('/\\').strip()
                base_name = os.path.basename(clean_img)
                if not base_name and '/' in clean_img:
                    base_name = [p for p in clean_img.split('/') if p][-1]
                elif not base_name and '\\' in clean_img:
                    base_name = [p for p in clean_img.split('\\') if p][-1]

                local_img_path = None
                if image_url.startswith('data:'):
                    try:
                        header, b64data = image_url.split(';base64,', 1)
                        raw = base64.b64decode(b64data)
                        mtype, ext = _detect_magic_media(raw, 'reference.png')
                        fname = f"ref_{int(time.time() * 1000)}.{ext or 'png'}"
                        local_img_path = os.path.join(OUTPUTS_DIR, fname)
                        with open(local_img_path, 'wb') as fh:
                            fh.write(raw)
                    except Exception as e:
                        VIDEO_JOBS[job_id] = {"status": "failed", "error": str(e), "message": f"فشل قراءة كادر الصورة: {e}"}
                        return
                elif os.path.isabs(clean_img) and os.path.isfile(clean_img):
                    local_img_path = clean_img
                else:
                    cand = os.path.join(OUTPUTS_DIR, base_name)
                    if os.path.isfile(cand):
                        local_img_path = cand
                    else:
                        # Smart Token Fuzzy Matching
                        best_file = None
                        best_score = 0
                        clean_stem = os.path.splitext(base_name)[0].lower()
                        tokens = [t for t in re.split(r'[^a-zA-Z0-9]+', clean_stem) if len(t) >= 3]
                        for f in os.listdir(OUTPUTS_DIR):
                            f_lower = f.lower()
                            if not f_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                                continue
                            score = sum(1 for t in tokens if t in f_lower)
                            if score > best_score:
                                best_score = score
                                best_file = os.path.join(OUTPUTS_DIR, f)
                        if best_file and best_score >= 1 and os.path.isfile(best_file):
                            local_img_path = best_file

                if not local_img_path or not os.path.isfile(local_img_path):
                    VIDEO_JOBS[job_id] = {"status": "failed", "error": "file_not_found", "message": f"ملف كادر الصورة غير موجود كملف صالح: {image_url}"}
                    return

                VIDEO_JOBS[job_id]["progress"] = 35
                VIDEO_JOBS[job_id]["message"] = "تم تثبيت الكادر المرجعي.. جاري المعالجة السحابية الفائقة..."

                # 2. Check local/cloud ComfyUI
                comfy_is_alive = False
                if raw_url:
                    try:
                        r_ping = requests.get(f"{raw_url.rstrip('/')}/system_stats", headers={'User-Agent': 'Mozilla/5.0'}, timeout=1.5)
                        if r_ping.status_code == 200:
                            comfy_is_alive = True
                    except Exception:
                        comfy_is_alive = False

                # Helper for Cloud Render
                def do_cloud():
                    if not fal_key:
                        raise RuntimeError("مفتاح Fal.ai السحابي غير متوفر لإتمام الريندر.")
                    cloud_img = upload_file_to_fal(local_img_path, fal_key) or local_img_path
                    if 'wan' in ckpt_lower:
                        endpoint = "fal-ai/wan-i2v"
                        label = "Alibaba Wan 2.2" if ('2.2' in ckpt_lower or 'wan2.2' in ckpt_lower) else "Alibaba Wan 2.1"
                        fal_payload = {"prompt": prompt_text, "image_url": cloud_img}
                    elif 'hunyuan' in ckpt_lower:
                        endpoint = "fal-ai/hunyuan-video-image-to-video"
                        label = "Tencent HunyuanVideo (13B)"
                        fal_payload = {"prompt": prompt_text, "image_url": cloud_img}
                    elif 'cogvideo' in ckpt_lower:
                        endpoint = "fal-ai/cogvideox-5b/image-to-video"
                        label = "THUDM CogVideoX-5B"
                        fal_payload = {"prompt": prompt_text, "image_url": cloud_img}
                    else:
                        endpoint = "fal-ai/wan-i2v"
                        label = "Alibaba Wan 2.1"
                        fal_payload = {"prompt": prompt_text, "image_url": cloud_img}

                    sub_r = requests.post(f"https://queue.fal.run/{endpoint}", headers={'Authorization': f'Key {fal_key}', 'Content-Type': 'application/json'}, json=fal_payload, timeout=25)
                    if sub_r.status_code not in [200, 201, 202]:
                        raise RuntimeError(f"خطأ إرسال لمحرك {label}: {sub_r.text[:200]}")
                    q_info = sub_r.json()
                    st_url = q_info.get('status_url')
                    res_url = q_info.get('response_url')
                    t0 = time.time()
                    in_progress_t0 = None
                    vid_url = None
                    print(f"[COMFY_VIDEO] Launched job {job_id} -> Fal request: {q_info.get('request_id')} ({endpoint})", flush=True)
                    VIDEO_JOBS[job_id]["fal_request_id"] = q_info.get('request_id')
                    while time.time() - t0 < 1200:
                        time.sleep(3.5)
                        c_st = requests.get(st_url, headers={'Authorization': f'Key {fal_key}'}, timeout=15).json()
                        st = c_st.get('status')
                        elapsed = int(time.time() - t0)
                        q_pos = c_st.get('queue_position', 0)
                        if st == 'IN_QUEUE':
                            VIDEO_JOBS[job_id]["progress"] = min(35, 10 + elapsed // 4)
                            VIDEO_JOBS[job_id]["message"] = f"الطلب في طابور السيرفر السحابي لموديل {label} (موقع الطابور: {q_pos}) - جاري تخصيص كارت H100..."
                        elif st == 'IN_PROGRESS':
                            if in_progress_t0 is None:
                                in_progress_t0 = time.time()
                            ip_elapsed = int(time.time() - in_progress_t0)
                            VIDEO_JOBS[job_id]["progress"] = min(96, 40 + ip_elapsed // 2)
                            VIDEO_JOBS[job_id]["message"] = f"كارت H100 يريندر إطارات الفيديو الآن بدقة سينمائية لموديل {label} (زمن الريندر الفعلي: {ip_elapsed} ثانية)..."
                        else:
                            VIDEO_JOBS[job_id]["progress"] = min(90, 30 + elapsed // 3)
                            VIDEO_JOBS[job_id]["message"] = f"جاري معالجة مشهد {label} ({elapsed} ثانية)..."

                        if st == 'COMPLETED':
                            f_res = requests.get(res_url, headers={'Authorization': f'Key {fal_key}'}, timeout=20).json()
                            if 'detail' in f_res:
                                raise RuntimeError(f"خطأ من خادم {label}: {f_res.get('detail')}")
                            v_obj = f_res.get('video')
                            vid_url = v_obj.get('url') if isinstance(v_obj, dict) else (f_res.get('video_url') or f_res.get('url') or f_res.get('output'))
                            if not vid_url:
                                raise RuntimeError(f"لم يتم العثور على رابط الفيديو في استجابة خادم {label}: {f_res}")
                            break
                        elif st in ['FAILED', 'ERROR']:
                            raise RuntimeError(f"فشلت معالجة المشهد على خوادم {label}: {c_st}")
                    
                    if not vid_url:
                        raise TimeoutError("استغرق ريندر المشهد أكثر من الحد المسموح.")

                    v_name = f"Render_{label.replace(' ', '_').replace('(', '').replace(')', '')}_{int(time.time())}.mp4"
                    v_path = os.path.join(OUTPUTS_DIR, v_name)
                    v_bytes = requests.get(vid_url, timeout=60).content
                    with open(v_path, 'wb') as vf:
                        vf.write(v_bytes)

                    # Extract frame 0
                    try:
                        import cv2
                        cap = cv2.VideoCapture(v_path)
                        ret, frame = cap.read()
                        if ret:
                            f0_path = os.path.join(OUTPUTS_DIR, f"Frame0_{label.replace(' ', '_').replace('(', '').replace(')', '')}_{int(time.time())}.jpg")
                            cv2.imwrite(f0_path, frame)
                        cap.release()
                    except Exception:
                        pass

                    VIDEO_JOBS[job_id] = {
                        "success": True,
                        "status": "completed",
                        "progress": 100,
                        "url": f"/outputs/{v_name}",
                        "filename": v_name,
                        "media_type": "video",
                        "seed": int(time.time()),
                        "message": f"تم ريندر مشهد الفيديو بنجاح بدقة عالية عبر محرك {label}!"
                    }

                # If ComfyUI is not available, do cloud directly
                if not comfy_is_alive:
                    do_cloud()
                    return

                # Otherwise try ComfyUI workflow
                try:
                    uploaded_name = comfyui_client.upload_image_to_comfyui(raw_url, local_img_path)
                    if 'wan' in ckpt_lower and ('2.2' in ckpt_lower or 'wan2.2' in ckpt_lower):
                        workflow, seed = comfyui_client.build_wan22_workflow(uploaded_name, prompt_text, ckpt, width, height, video_frames, steps, fps)
                        engine_label = "Alibaba Wan 2.2"
                    elif 'wan' in ckpt_lower:
                        workflow, seed = comfyui_client.build_wan_workflow(uploaded_name, prompt_text, ckpt, width, height, video_frames, steps, fps)
                        engine_label = "Alibaba Wan 2.1"
                    elif 'hunyuan' in ckpt_lower:
                        workflow, seed = comfyui_client.build_hunyuan_workflow(uploaded_name, prompt_text, ckpt, width, height, 73, steps, fps)
                        engine_label = "Tencent HunyuanVideo"
                    elif 'cogvideo' in ckpt_lower:
                        workflow, seed = comfyui_client.build_cogvideox_workflow(uploaded_name, prompt_text, ckpt, width, height, 49, steps, fps)
                        engine_label = "THUDM CogVideoX-5B"
                    else:
                        workflow, seed = comfyui_client.build_svd_video_workflow(uploaded_name, ckpt, width, height, video_frames, motion_bucket_id, fps, steps)
                        engine_label = "Stability AI SVD-XT"

                    res = comfyui_client.execute_comfyui_workflow(raw_url, workflow, OUTPUTS_DIR, timeout_seconds=400)
                    fname = res["filename"]
                    VIDEO_JOBS[job_id] = {
                        "success": True,
                        "status": "completed",
                        "progress": 100,
                        "url": f"/outputs/{fname}",
                        "filename": fname,
                        "media_type": "video",
                        "seed": seed,
                        "message": f"تم ريندر مشهد الفيديو بنجاح عبر {engine_label}!"
                    }
                except Exception as e_wf:
                    # ComfyUI failed, fallback to cloud
                    do_cloud()

            except Exception as e_all:
                VIDEO_JOBS[job_id] = {
                    "status": "failed",
                    "error": str(e_all),
                    "message": f"فشل ريندر الفيديو: {str(e_all)}"
                }
            finally:
                if auto_stop and raw_url and 'runpod.net' in raw_url:
                    try:
                        runpod_key = secrets.get('runpod_api_key', '')
                        if runpod_key:
                            comfyui_client.stop_runpod_pod(runpod_key)
                    except Exception:
                        pass

        # Start thread and respond immediately!
        threading.Thread(target=_bg_render, daemon=True).start()
        self.send_json_response(200, {
            "success": True,
            "job_id": job_id,
            "status": "processing",
            "message": "تم إطلاق عملية الريندر السحابية بنجاح! جاري متابعة التقدم..."
        })

    def handle_comfyui_generate(self, payload):

        secrets = load_secrets()

        url = secrets.get('local_comfyui_url', '').strip()

        if not url:

            self.send_error_response(400, "يرجى ربط سيرفر ComfyUI أولاً.")

            return

        

        prompt = (payload.get('prompt') or '').strip()

        if not prompt:

            self.send_error_response(400, "يرجى كتابة وصف المشهد السينمائي.")

            return

        

        negative = payload.get('negative_prompt', 'blurry, bad anatomy, bad hands, low quality, artifacts')

        ckpt = payload.get('checkpoint', 'flux1-dev.sft')

        lora_name = payload.get('lora_name')

        lora_strength = float(payload.get('lora_strength', 0.9))

        width = int(payload.get('width', 1024))

        height = int(payload.get('height', 1024))

        steps = int(payload.get('steps', 25))

        cfg = float(payload.get('cfg', 4.0))

        sampler = payload.get('sampler', 'euler')

        scheduler = payload.get('scheduler', 'normal')

        auto_stop = bool(payload.get('auto_stop', True))

        

        img_source = payload.get('image_url') or payload.get('image') or None
        workflow, seed = comfyui_client.build_cinematic_image_workflow(

            prompt=prompt,

            negative_prompt=negative,

            checkpoint=ckpt,

            lora_name=lora_name,

            lora_strength=lora_strength,

            width=width,

            height=height,

            steps=steps,

            cfg=cfg,

            sampler=sampler,

            scheduler=scheduler

        )

        

        try:

            res = comfyui_client.execute_comfyui_workflow(

                base_url=url,

                workflow=workflow,

                outputs_dir=OUTPUTS_DIR,

                timeout_seconds=300

            )

            fname = res["filename"]

            local_url = f"/outputs/{fname}"

            self.send_json_response(200, {

                "success": True,

                "url": local_url,

                "filename": fname,

                "seed": seed,

                "media_type": "image",

                "message": "تم ريندر الكادر السينمائي بنجاح عبر ComfyUI!"

            })

        except Exception as e:

            self.send_error_response(500, f"فشل ريندر ComfyUI: {str(e)}")

        finally:

            if auto_stop:

                try:

                    runpod_key = secrets.get('runpod_api_key', '')

                    if runpod_key:

                        comfyui_client.stop_runpod_pod(runpod_key)

                except Exception:

                    pass



    def handle_runpod_status(self):

        secrets = load_secrets()

        api_key = secrets.get('runpod_api_key', '')

        if not api_key:

            self.send_json_response(200, {"configured": False, "pods": [], "message": "RunPod API Key غير مسجل."})

            return



        query = """

        query MyPods {

            myself {

                pods {

                    id

                    name

                    desiredStatus

                    runtime {

                        uptimeInSeconds

                    }

                    machine {

                        gpuDisplayName

                    }

                }

            }

        }

        """

        res = _runpod_graphql(query, api_key)

        if "errors" in res:

            self.send_json_response(200, {"configured": True, "error": res["errors"][0]["message"], "pods": []})

            return



        pods = res.get("data", {}).get("myself", {}).get("pods", [])

        self.send_json_response(200, {

            "configured": True,

            "pods": pods,

            "count": len(pods),

            "message": f"متصل بحساب RunPod ({len(pods)} أجهزة سحابية نشطة)."

        })



    def handle_runpod_terminate_all(self):

        secrets = load_secrets()

        api_key = secrets.get('runpod_api_key', '')

        if not api_key:

            self.send_error_response(400, "RunPod API Key required.")

            return



        # Query all pods first

        query = "query { myself { pods { id name } } }"

        res = _runpod_graphql(query, api_key)

        pods = res.get("data", {}).get("myself", {}).get("pods", [])

        terminated = []

        for p in pods:

            p_id = p.get('id')

            term_mut = f'mutation {{ podTerminate(input: {{podId: "{p_id}"}}) }}'

            _runpod_graphql(term_mut, api_key)

            terminated.append(p_id)



        self.send_json_response(200, {

            "success": True,

            "terminated_count": len(terminated),

            "message": f"تم إيقاف وحذف {len(terminated)} كمبيوتر سحابي فوراً لحماية رصيدك بنجاح!"

        })



    def handle_runpod_train(self, payload):

        self.handle_lora_train(dict(payload, backend='runpod'))









class ThreadedCindyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True

    daemon_threads = True





def _runpod_graphql(query, api_key, variables=None):

    headers = {"Content-Type": "application/json"}

    url = f"https://api.runpod.io/graphql?api_key={api_key.strip()}"

    payload = {"query": query}

    if variables:

        payload["variables"] = variables

    try:

        r = requests.post(url, headers=headers, json=payload, timeout=20)

        if r.status_code == 200:

            return r.json()

        return {"errors": [{"message": f"HTTP {r.status_code}: {r.text[:200]}"}]}

    except Exception as e:

        return {"errors": [{"message": str(e)}]}



def _extract_media_url(data):

    if not isinstance(data, dict):

        return ''

    # Check video object

    v = data.get('video')

    if isinstance(v, dict) and v.get('url'):

        return v['url']

    if isinstance(v, str) and v.startswith('http'):

        return v

    # Check output

    out = data.get('output')

    if isinstance(out, dict):

        sub_v = _extract_media_url(out)

        if sub_v:

            return sub_v

    # Check direct video_url

    if data.get('video_url') and isinstance(data['video_url'], str) and data['video_url'].startswith('http'):

        return data['video_url']

    # Check images list

    imgs = data.get('images', [])

    if isinstance(imgs, list) and imgs:

        first = imgs[0]

        if isinstance(first, dict) and first.get('url'):

            return first['url']

        if isinstance(first, str) and first.startswith('http'):

            return first

    # Check direct url

    if data.get('url') and isinstance(data['url'], str) and data['url'].startswith('http'):

        return data['url']

    return ''









# --- Automatic Inactivity Auto-Pause Watchdog (Zero-Loss Guarantee) ---

LAST_COMFY_ACTIVITY = time.time()

WATCHDOG_TIMEOUT_SECONDS = 300  # 15 minutes of inactivity



def update_comfy_activity():

    global LAST_COMFY_ACTIVITY

    LAST_COMFY_ACTIVITY = time.time()



def run_inactivity_watchdog():

    """Background watchdog that monitors RunPod pod. If running and inactive for > 15 mins, auto-pauses."""

    while True:

        time.sleep(60)

        try:

            now = time.time()

            if now - LAST_COMFY_ACTIVITY >= WATCHDOG_TIMEOUT_SECONDS:

                secrets = load_secrets()

                key = secrets.get('runpod_api_key', '').strip()

                if key:

                    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

                    q = "query { myself { pods { id desiredStatus runtime { uptimeInSeconds } } } }"

                    r = requests.post("https://api.runpod.io/graphql", headers=headers, json={"query": q}, timeout=10)

                    pods = r.json().get("data", {}).get("myself", {}).get("pods", [])

                    running_pods = [p for p in pods if p.get("desiredStatus") == "RUNNING"]

                    for p in running_pods:

                        uptime = (p.get("runtime") or {}).get("uptimeInSeconds") or 0

                        if uptime >= WATCHDOG_TIMEOUT_SECONDS:

                            comfyui_client.stop_runpod_pod(key, p.get("id"))

                            print(f"[Watchdog] Auto-paused pod {p.get('id')} after {uptime}s uptime to protect balance!")

        except Exception:

            pass



threading.Thread(target=run_inactivity_watchdog, daemon=True).start()





def upload_file_to_fal(local_rel_path, fal_key):

    """Upload a local output file to Fal.ai storage and return its public URL."""

    clean_name = os.path.basename(local_rel_path.split('?')[0].rstrip('/\\'))
    if os.path.exists(local_rel_path):
        local_full_path = local_rel_path
    elif os.path.exists(os.path.join(OUTPUTS_DIR, clean_name)):
        local_full_path = os.path.join(OUTPUTS_DIR, clean_name)
    elif os.path.exists(os.path.join(OUTPUTS_DIR, "blender_guides", clean_name)):
        local_full_path = os.path.join(OUTPUTS_DIR, "blender_guides", clean_name)
    else:
        return None
    ext = os.path.splitext(clean_name)[1].lower().lstrip('.')

    content_type = 'image/png'

    if ext in ('jpg', 'jpeg'): content_type = 'image/jpeg'

    elif ext == 'webp': content_type = 'image/webp'

    elif ext == 'mp4': content_type = 'video/mp4'

    elif ext in ('wav', 'wave'): content_type = 'audio/wav'

    elif ext == 'mp3': content_type = 'audio/mpeg'

    

    headers = {'Authorization': f'Key {fal_key}', 'Content-Type': 'application/json'}

    init_url = 'https://rest.alpha.fal.ai/storage/upload/initiate'

    r_init = requests.post(init_url, headers=headers, json={'file_name': clean_name, 'content_type': content_type}, timeout=15)

    if r_init.status_code != 200:

        return None

        

    data = r_init.json()

    upload_url = data.get('upload_url')

    file_url = data.get('file_url')

    

    with open(local_full_path, 'rb') as f:

        r_up = requests.put(upload_url, data=f, headers={'Content-Type': content_type}, timeout=60)

        if r_up.status_code in (200, 201):

            return file_url

    return None



if __name__ == '__main__':

    print(f"Starting Cindy AI Execution Server on http://{HOST}:{PORT} ...")

    def _pricing_worker():
        import time
        from cindy_pricing import build_daily_pricing_report
        try:
            build_daily_pricing_report(force_refresh=False)
        except Exception:
            pass
        while True:
            time.sleep(21600)
            try:
                build_daily_pricing_report(force_refresh=True)
            except Exception:
                pass
    threading.Thread(target=_pricing_worker, daemon=True).start()

    server = ThreadedCindyServer((HOST, PORT), CindySecureHandler)

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("Server stopped.")

