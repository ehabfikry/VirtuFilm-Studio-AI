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

import json, os, time, requests, re

SCRIPTS_STORAGE_PATH = r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\scripts_storyboard.json'

def load_storyboards():
    if os.path.exists(SCRIPTS_STORAGE_PATH):
        try:
            with open(SCRIPTS_STORAGE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"projects": []}

def save_storyboards(data):
    os.makedirs(os.path.dirname(SCRIPTS_STORAGE_PATH), exist_ok=True)
    with open(SCRIPTS_STORAGE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def breakdown_script_with_ai(script_text, director_notes="", secrets=None):
    if not secrets:
        secrets = {}
    
    gemini_key = secrets.get('gemini_api_key', '').strip()
    fal_key = secrets.get('fal_api_key', '').strip()
    
    prompt = f"""
You are a veteran Hollywood 1st Assistant Director (1st AD) and expert Cinema Decoupage Master.
The Film Director has provided the following script/scene:

=== SCRIPT / SCENE TEXT ===
{script_text}

=== DIRECTOR NOTES ===
{director_notes or 'Standard professional cinematic breakdown with natural storytelling pacing.'}

Your task is to break down this scene into consecutive cinematic shots for a visual storyboard (3 to 8 shots depending on scene length).
For each shot, provide:
1. shot_number (1, 2, 3...)
2. shot_type (e.g. Master Wide, Medium Close-Up, Extreme Close-Up, Over-the-Shoulder, Low-Angle Tracking)
3. lens_mm (e.g. 24mm, 35mm, 50mm, 85mm, 100mm Macro)
4. camera_movement (e.g. Slow Push-in, Static Locked-off, Handheld intimate, Orbital Pan)
5. lighting (e.g. Chiaroscuro high-contrast, Soft golden hour rim light, Neon noir shadows)
6. action_description (in Arabic for the Director: ما يحدث أمام الكاميرا وانفعال الممثل بدقة)
7. visual_prompt (in English: highly detailed cinematic prompt formatted specifically for FLUX.1 / cinematic AI image generator: 35mm film still, lighting, camera angle, actor emotion, photorealistic, 8k, cinematic color grade, depth of field)
8. suggested_model (e.g. "Wan 2.1 (Alibaba 14B)", "LTX-2.3 22B Cinema LoRA", "MiniMax H3 I2V LoRA", "Kling Motion Control (1080p)")
9. estimated_duration (e.g. 3, 4, 5, 6 seconds)

RESPOND ONLY WITH STRICT VALID JSON matching this exact structure:
{{
  "scene_title": "عنوان المشهد",
  "logline": "ملخص الفكرة الإخراجية للمشهد بجملة واحدة",
  "shots": [
    {{
      "shot_number": 1,
      "shot_type": "Master Wide Shot",
      "lens_mm": "24mm",
      "camera_movement": "Slow subtle dolly in",
      "lighting": "Atmospheric cinematic sidelight",
      "action_description": "...",
      "visual_prompt": "Cinematic 35mm film still of...",
      "suggested_model": "Wan 2.1 (Alibaba 14B)",
      "estimated_duration": 5
    }}
  ]
}}
"""
    
    # 1. Try Gemini
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            req_data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 4096}
            }
            res = requests.post(url, json=req_data, timeout=20)
            if res.status_code == 200:
                out = res.json()
                raw_text = out['candidates'][0]['content']['parts'][0]['text']
                raw_text = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
                raw_text = re.sub(r'```$', '', raw_text.strip(), flags=re.MULTILINE)
                return json.loads(raw_text.strip())
        except Exception as e:
            print(f"[Storyboard AI] Gemini error: {e}")

    # 2. Try Fal Any-LLM
    if fal_key:
        try:
            headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
            fal_url = "https://fal.run/fal-ai/any-llm"
            req_data = {
                "model": "google/gemini-2.5-flash-lite",
                "prompt": prompt,
                "system_prompt": "You are a professional film 1st AD. Respond strictly with JSON."
            }
            res = requests.post(fal_url, headers=headers, json=req_data, timeout=20)
            if res.status_code == 200:
                raw_text = res.json().get('output', '')
                raw_text = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
                raw_text = re.sub(r'```$', '', raw_text.strip(), flags=re.MULTILINE)
                return json.loads(raw_text.strip())
        except Exception as e:
            print(f"[Storyboard AI] Fal Any-LLM error: {e}")

    # Fallback template
    return {
        "scene_title": "مشهد درامي",
        "logline": "تقطيع المشهد لقطات سينمائية متتالية",
        "shots": [
            {
                "shot_number": 1,
                "shot_type": "Establishing Wide Shot",
                "lens_mm": "28mm",
                "camera_movement": "Slow forward tracking",
                "lighting": "Low-key dramatic cinematic rim lighting",
                "action_description": "لقطة عامة لتأسيس المكان وحركة الشخصية داخل الفراغ.",
                "visual_prompt": f"Cinematic 35mm movie still, wide angle 28mm anamorphic, atmospheric dramatic lighting, {script_text[:120]}, masterpiece 8k, cinematic framing",
                "suggested_model": "Wan 2.1 (Alibaba 14B)",
                "estimated_duration": 5
            },
            {
                "shot_number": 2,
                "shot_type": "Medium Close-Up",
                "lens_mm": "50mm",
                "camera_movement": "Static focused beat",
                "lighting": "Soft cinematic key light on eyes",
                "action_description": "لقطة متوسطة قريبة تركز على انفعال الممثل ونظرته الحادة.",
                "visual_prompt": f"Cinematic medium close-up shot, 50mm lens, shallow depth of field, intense emotional expression, {script_text[:120]}, cinematic color grade",
                "suggested_model": "LTX-2.3 22B Cinema LoRA",
                "estimated_duration": 4
            },
            {
                "shot_number": 3,
                "shot_type": "Tight Close-Up Reaction",
                "lens_mm": "85mm",
                "camera_movement": "Handheld subtle breathing",
                "lighting": "Dramatic contrast, deep shadows",
                "action_description": "رد فعل درامي مباشر وتفاصيل دقيقة في العينين وملامح الوجه.",
                "visual_prompt": f"Cinematic intense close up reaction shot, 85mm prime lens, micro-details in eyes, atmospheric moody shadows, high budget movie still",
                "suggested_model": "MiniMax H3 I2V LoRA",
                "estimated_duration": 3
            }
        ]
    }

def render_storyboard_frame(visual_prompt, aspect_ratio="16:9", fal_key=""):
    if not fal_key:
        raise ValueError("Fal.ai API key is required to render storyboard frames.")
    
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }
    
    ar_map = {
        "16:9": "landscape_16_9",
        "9:16": "portrait_9_16",
        "1:1": "square_hd",
        "21:9": "landscape_21_9"
    }
    img_size = ar_map.get(aspect_ratio, "landscape_16_9")
    
    req_body = {
        "prompt": f"cinematic film storyboard frame, 35mm movie still, {visual_prompt}, highly detailed, sharp focus, professional cinema production, 8k",
        "image_size": img_size,
        "num_inference_steps": 4,
        "num_images": 1,
        "enable_safety_checker": False
    }
    
    # Render with FLUX.1 Schnell (lightning fast ~1.5s and ultra cheap ~$0.003)
    res = requests.post("https://fal.run/fal-ai/flux/schnell", headers=headers, json=req_body, timeout=30)
    if res.status_code == 200:
        data = res.json()
        imgs = data.get('images', [])
        if imgs and imgs[0].get('url'):
            return imgs[0]['url']
        raise RuntimeError("No image returned from Fal.ai")
    else:
        raise RuntimeError(f"Fal.ai error {res.status_code}: {res.text[:180]}")
