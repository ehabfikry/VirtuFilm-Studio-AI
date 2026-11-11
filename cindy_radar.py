import os, json, time, requests, re

RADAR_CACHE_PATH = r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\cinema_radar_cache.json'

DEFAULT_TRENDS = [
    {
        "id": "wan_2_2",
        "title": "Alibaba Wan 2.2 Image-to-Video & Native LoRA",
        "category": "Video Engine",
        "badge": "تحديث هائل",
        "summary": "إطلاق معمارية Wan 2.2 بقدرة تحريك فيزيائية فائقة وتماسك كامل للأقمشة والإضاءة مع دعم مدمج للـ LoRA لتثبيت الممثلين بتكلفة تبدأ من $0.04 للشوت.",
        "impact_on_director": "أفضل بديل اقتصادي لتوليد الشوتات الحركية الصعبة دون الحاجة لتصوير حي.",
        "cost_indicator": "~$0.04 / 5s",
        "action_prompt": "Cinematic shot using Alibaba Wan 2.2 with seamless camera motion and authentic physics"
    },
    {
        "id": "kling_motion_control_1080p",
        "title": "Kling 1.6 Pro & Motion Control 1080p",
        "category": "Motion Tracking",
        "badge": "هوليوودي",
        "summary": "تحديث Kling المطور لنقل حركة الجسم والكاميرا من أي فيديو مرجعي بدقة 1080p نقية مع قفل تطابق الممثل بنسبة 100%.",
        "impact_on_director": "يسمح لك بتمثيل الحركة بنفسك في الغرفة بكاميرا الموبايل ونقلها لشخصية فيلمك مباشرة.",
        "cost_indicator": "~$0.63 / 5s",
        "action_prompt": "1080p motion tracking sequence transferring exact choreography"
    },
    {
        "id": "gemini_flash_audio_masri",
        "title": "Google Gemini 2.5 / 3.8 Flash Native Audio TTS",
        "category": "Voice & Dubbing",
        "badge": "لهجة مصرية نقية",
        "summary": "إطلاق محرك الصوت المباشر من Google DeepMind بنبرات درامية حقيقية وقدرة نادرة على نطق العامية المصرية (Masri) بنقاء 24kHz بدون نبرة الروبوت الجافة.",
        "impact_on_director": "دوبلاج فوري للمشاهد وتجربة حوارات الشخصيات باللهجة المصرية مجاناً 100%.",
        "cost_indicator": "مجاني (Free Tier)",
        "action_prompt": "Generate authentic Cairo colloquial dialogue"
    },
    {
        "id": "flux_1_schnell_storyboarding",
        "title": "FLUX.1 Schnell Ultra-Fast Pre-vis",
        "category": "Keyframing & Pre-vis",
        "badge": "شبه مجاني",
        "summary": "أصبح معيار الستوري بورد الأول في هوليوود لتوليد كادرات الكاميرا في أقل من ثانيتين بتكلفة $0.003 للكادر فقط.",
        "impact_on_director": "تصميم ديكوباج المشهد كاملاً بـ 10 كادرات بأقل من نصف جنيه مصري.",
        "cost_indicator": "$0.003 / كادر",
        "action_prompt": "Cinematic 35mm storyboard frame with dramatic chiaroscuro lighting"
    }
]

def get_latest_cinema_trends(force_refresh=False, secrets=None):
    now = time.time()
    if not force_refresh and os.path.exists(RADAR_CACHE_PATH):
        try:
            with open(RADAR_CACHE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if now - data.get('timestamp', 0) < 86400: # 24 hours
                    return data
        except Exception:
            pass
    
    # In live mode, we can fetch real-time updates via Fal / Gemini if keys are present
    trends = DEFAULT_TRENDS
    if secrets:
        gemini_key = secrets.get('gemini_api_key', '').strip()
        if gemini_key and force_refresh:
            try:
                # Query Gemini for the latest breakthroughs
                prompt = """
You are Cindy AI Director's Head of Cinema Technology Radar.
Summarize the top 4 cutting-edge breakthroughs in Generative AI for Film & Video Production right now (e.g. Wan 2.2, Kling 1.6 Motion Control, FLUX, Veo 3, Gemini Audio).
Provide the response strictly in valid JSON matching this structure:
{
  "trends": [
    {
      "id": "string",
      "title": "string",
      "category": "string (e.g. Video Engine, Motion Control, Audio Dubbing, Pre-vis)",
      "badge": "string (e.g. ثورة تقنية, اقتصادي, هوليوودي)",
      "summary": "Arabic summary (2-3 sentences max focused on real director benefits)",
      "impact_on_director": "Arabic explanation of how the Film Director saves money or elevates visuals",
      "cost_indicator": "e.g. ~$0.04/shot or Free",
      "action_prompt": "English cinematic prompt"
    }
  ]
}
"""
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
                if res.status_code == 200:
                    raw = res.json()['candidates'][0]['content']['parts'][0]['text']
                    raw = re.sub(r'^```json\s*', '', raw.strip(), flags=re.MULTILINE)
                    raw = re.sub(r'```$', '', raw.strip(), flags=re.MULTILINE)
                    parsed = json.loads(raw.strip())
                    if parsed.get('trends'):
                        trends = parsed['trends']
            except Exception as e:
                print(f"[Radar AI Refresh Error]: {e}")
    
    result = {
        "timestamp": now,
        "last_updated": time.strftime("%Y-%m-%d %I:%M %p"),
        "trends": trends
    }
    
    os.makedirs(os.path.dirname(RADAR_CACHE_PATH), exist_ok=True)
    with open(RADAR_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
    return result
