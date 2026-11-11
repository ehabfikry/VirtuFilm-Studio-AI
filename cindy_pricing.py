import os
import json
import time
import datetime
import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

SECRETS_PATH = r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json'
CACHE_PATH = r'C:\Users\DELL\Desktop\Cindy-AI-Director\daily_pricing_cache.json'

FAL_PRICING_ENDPOINTS = [
    # Video Models
    'fal-ai/kling-video/v3/standard/motion-control',
    'fal-ai/kling-video/v1.6/pro/image-to-video',
    'fal-ai/kling-video/v1.6/pro/text-to-video',
    'fal-ai/kling-video/v1.6/standard/image-to-video',
    'fal-ai/kling-video/v1.6/standard/text-to-video',
    'fal-ai/kling-video/o1/video-to-video/edit',
    'fal-ai/luma-dream-machine/ray-2/image-to-video',
    'fal-ai/luma-dream-machine/ray-2/text-to-video',
    'fal-ai/luma-dream-machine/ray-2/modify',
    'fal-ai/wan/v2.1/text-to-video',
    'fal-ai/wan/v2.1/image-to-video',
    'fal-ai/ltx-2.3-22b/image-to-video/lora',
    'fal-ai/ltx-2.3-22b/distilled/image-to-video/lora',
    'minimax/h3/image-to-video/lora',
    'fal-ai/minimax/video-01',
    'fal-ai/minimax/video-01/camera-controls',
    'fal-ai/bytedance/seedance/v1/pro/text-to-video',
    'fal-ai/pixverse/v6',
    'fal-ai/topaz/upscale-video',
    'fal-ai/sync-lipsync/v2',
    'fal-ai/musetalk',
    # Image & Edit Models
    'fal-ai/flux-pro/v1.1-ultra',
    'fal-ai/flux/dev',
    'fal-ai/flux/schnell',
    'blackforestlabs/flux-3/klein/edit-image/lora',
    'fal-ai/qwen-image-2512/lora',
    'fal-ai/qwen-image-edit-2511',
    'fal-ai/nano-banana',
    'fal-ai/nano-banana-pro',
    'fal-ai/ideogram/v2',
    'fal-ai/recraft-v3'
]

MODEL_METADATA = {
    # 1. Video Models
    'fal-ai/wan/v2.1/text-to-video': {
        'name': 'Alibaba Wan 2.1 (Text-to-Video)',
        'category': 'video_t2v',
        'badge': 'الأرخص إطلاقاً (سنتات)',
        'type': 'Text-to-Video',
        'calc_shot': lambda p: 0.03,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'الأرخص عالمياً (~$0.03 للشوت) وجودة سينمائية مذهلة بفيزياء طبيعية'
    },
    'fal-ai/wan/v2.1/image-to-video': {
        'name': 'Alibaba Wan 2.1 (Image-to-Video)',
        'category': 'video_i2v',
        'badge': 'الأرخص إطلاقاً (سنتات)',
        'type': 'Image-to-Video',
        'calc_shot': lambda p: 0.03,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'تحريك كوادر الممثلين بأقل تكلفة ممكنة مع نتائج طبيعية وحركة كاميرا سلسة'
    },
    'fal-ai/minimax/video-01': {
        'name': 'MiniMax Hailuo H3 Lite',
        'category': 'video_t2v',
        'badge': 'اقتصادي سريع',
        'type': 'Text-to-Video',
        'calc_shot': lambda p: 0.04,
        'shot_label': 'شوت 6 ثوانٍ كامل',
        'recommendation': 'حركة ممثلين سريعة وواقعية بـ 4 سنتات فقط للشوت الثابت 6 ثوانٍ'
    },
    'fal-ai/ltx-2.3-22b/distilled/image-to-video/lora': {
        'name': 'LTX-2.3 Distilled Fast LoRA',
        'category': 'video_i2v',
        'badge': 'سريع + قفل LoRA',
        'type': 'Image-to-Video',
        'calc_shot': lambda p: 0.08,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'مسودة فيديو سريعة مع قفل ملامح الممثل بواسطة نموذج LoRA المخصص'
    },
    'fal-ai/ltx-2.3-22b/image-to-video/lora': {
        'name': 'LTX-2.3 22B Cinema LoRA',
        'category': 'video_i2v',
        'badge': 'أعلى جودة + قفل LoRA',
        'type': 'Image-to-Video',
        'calc_shot': lambda p: 0.20,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'المعيار الذهبي الهوليوودي للإنتاج السينمائي مع قفل وجه وهوية الممثل بدقة 22B'
    },
    'minimax/h3/image-to-video/lora': {
        'name': 'MiniMax H3 I2V LoRA',
        'category': 'video_i2v',
        'badge': 'قفل ملامح بالـ LoRA',
        'type': 'Image-to-Video',
        'calc_shot': lambda p: 0.25,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'ثبات ملامح الوجه وتعبيرات الممثل الدرامية مع تحريك كادر البداية'
    },
    'fal-ai/minimax/video-01/camera-controls': {
        'name': 'MiniMax Camera Controls',
        'category': 'video_camera',
        'badge': 'تحكم مداري ثلاثي الأبعاد',
        'type': 'Camera Control',
        'calc_shot': lambda p: 0.25,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'تحكم دقيق بزاوية الكاميرا (Orbit / Pan / Tilt / Zoom) ثلاثي الأبعاد'
    },
    'fal-ai/pixverse/v6': {
        'name': 'PixVerse V6 Cinematic',
        'category': 'video_camera',
        'badge': '20 عدسة سينمائية',
        'type': 'Cinematic Video',
        'calc_shot': lambda p: 0.18,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'خيارات عدسات أنامورفيك وتأطير سينمائي احترافي وتحكم كامل بالحركة'
    },
    'fal-ai/bytedance/seedance/v1/pro/text-to-video': {
        'name': 'ByteDance Seedance 2.5',
        'category': 'video_multiref',
        'badge': 'حتى 30 ثانية ومراجع',
        'type': 'Multi-Ref Video',
        'calc_shot': lambda p: round(p * 5, 2) if p else 0.90,
        'shot_label': 'شوت 5 ثوانٍ (حتى 30ث)',
        'recommendation': 'يدعم مراجع متعددة (صور + فيديو + صوت) وتوليد مقاطع طويلة حتى 30 ثانية'
    },
    'fal-ai/kling-video/v1.6/pro/image-to-video': {
        'name': 'Kling 1.6 Pro (Image-to-Video)',
        'category': 'video_i2v',
        'badge': 'جودة سينمائية Pro',
        'type': 'Image-to-Video',
        'calc_shot': lambda p: round(p * 5, 2) if p else 0.49,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'المعيار الذهبي لتحريك اللقطات السينمائية من كادر البداية مع كادر نهاية اختياري'
    },
    'fal-ai/kling-video/v1.6/pro/text-to-video': {
        'name': 'Kling 1.6 Pro (Text-to-Video)',
        'category': 'video_t2v',
        'badge': 'فيديو من النص Pro',
        'type': 'Text-to-Video',
        'calc_shot': lambda p: round(p * 5, 2) if p else 0.49,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'توليد مشهد كامل من الوصف فقط بأعلى نقاء لوني وفيزيائي'
    },
    'fal-ai/kling-video/v1.6/standard/image-to-video': {
        'name': 'Kling 1.6 Standard (Image-to-Video)',
        'category': 'video_i2v',
        'badge': 'درافت واقتصادي',
        'type': 'Image-to-Video',
        'calc_shot': lambda p: round(p * 5, 2) if p else 0.28,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'خيار ممتاز لتجربة حركة الكاميرا والزوايا بنصف التكلفة'
    },
    'fal-ai/kling-video/v1.6/standard/text-to-video': {
        'name': 'Kling 1.6 Standard (Text-to-Video)',
        'category': 'video_t2v',
        'badge': 'درافت واقتصادي',
        'type': 'Text-to-Video',
        'calc_shot': lambda p: round(p * 5, 2) if p else 0.28,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'مسودات مشاهد سريعة'
    },
    'fal-ai/luma-dream-machine/ray-2/image-to-video': {
        'name': 'Luma Ray 2 (Image-to-Video)',
        'category': 'video_i2v',
        'badge': 'فيزياء وحركة كاميرا معقدة',
        'type': 'Image-to-Video',
        'calc_shot': lambda p: 0.50,
        'shot_label': 'شوت 5 ثوانٍ كامل',
        'recommendation': 'ممتاز للانتقالات السريعة، المركبات، والسيارات والحركات الديناميكية'
    },
    'fal-ai/luma-dream-machine/ray-2/text-to-video': {
        'name': 'Luma Ray 2 (Text-to-Video)',
        'category': 'video_t2v',
        'badge': 'حركة متدفقة',
        'type': 'Text-to-Video',
        'calc_shot': lambda p: 0.50,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'توليد حركات كاميرا واسعة من النص'
    },
    'fal-ai/kling-video/v3/standard/motion-control': {
        'name': 'Kling Motion Control (1080p)',
        'category': 'video_motion',
        'badge': 'نقل حركة كاملة 1080p',
        'type': 'Motion Transfer',
        'calc_shot': lambda p: round(p * 5, 2) if p else 0.63,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'الأفضل عالمياً في نقل الأداء التمثيلي الجسدي وثبات الوجه من فيديو مرجعي'
    },
    'fal-ai/kling-video/o1/video-to-video/edit': {
        'name': 'Kling O1 Video Edit',
        'category': 'video_edit',
        'badge': 'تعديل فيديو قائم',
        'type': 'Video Edit',
        'calc_shot': lambda p: round(p * 5, 2) if p else 0.50,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'تعديل وتغيير خامات وإضاءة فيديو موجود بالذكاء الاصطناعي'
    },
    'fal-ai/luma-dream-machine/ray-2/modify': {
        'name': 'Luma Ray 2 Modify',
        'category': 'video_edit',
        'badge': 'إعادة ستايل الفيديو',
        'type': 'Video Edit',
        'calc_shot': lambda p: round(p * 5, 2) if p else 1.75,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'تعديل البيئة والستايل الكلي للقطة'
    },
    'fal-ai/topaz/upscale-video': {
        'name': 'Topaz Video Upscale',
        'category': 'video_upscale',
        'badge': 'ترقية 4K سينمائية',
        'type': 'Video Upscale',
        'calc_shot': lambda p: 0.12,
        'shot_label': 'شوت 5 ثوانٍ',
        'recommendation': 'رفع نقاء ودقة الفيديو إلى 4K سينمائي نقي وإزالة الضوضاء الرقمية'
    },
    'fal-ai/sync-lipsync/v2': {
        'name': 'Sync Lipsync 2.0',
        'category': 'video_lipsync',
        'badge': 'مزامنة شفاه احترافية',
        'type': 'Audio-to-Video',
        'calc_shot': lambda p: 0.05,
        'shot_label': 'شوت 5 ثوانٍ ($0.70/د)',
        'recommendation': 'تطابق حركة الشفاه بدقة مع الحوار الصوتي العربي والأجنبي'
    },
    'fal-ai/musetalk': {
        'name': 'MuseTalk LipSync',
        'category': 'video_lipsync',
        'badge': 'دوبلاج فوري سريع',
        'type': 'Audio-to-Video',
        'calc_shot': lambda p: 0.03,
        'shot_label': 'شوت 5 ثوانٍ ($0.40/د)',
        'recommendation': 'دوبلاج صوتي اقتصادي وفوري لمقاطع الفيديو التمثيلية'
    },

    # 2. Image & Keyframe Models
    'fal-ai/flux/schnell': {
        'name': 'FLUX.1 [schnell]',
        'category': 'image',
        'badge': 'سريع وشبه مجاني',
        'type': 'Image Draft',
        'calc_shot': lambda p: 0.003,
        'shot_label': 'كادر ستوري بورد',
        'recommendation': 'توليد فوري للستوري بورد وتجربة الإضاءة (0.3 سنت فقط للكادر)'
    },
    'fal-ai/nano-banana': {
        'name': 'Google Nano Banana',
        'category': 'image',
        'badge': 'فوتوغرافي سريع',
        'type': 'Image Keyframe',
        'calc_shot': lambda p: 0.005,
        'shot_label': 'كادر سينمائي',
        'recommendation': 'فوتوغرافي سريع وعالي النقاء لكوادر الممثلين بنصف سنت'
    },
    'fal-ai/nano-banana-pro': {
        'name': 'Google Nano Banana Pro',
        'category': 'image',
        'badge': 'جودة 2K Pro',
        'type': 'Image Keyframe',
        'calc_shot': lambda p: 0.015,
        'shot_label': 'كادر سينمائي 2K',
        'recommendation': 'دقة 2K سينمائية متوازنة واحترافية للكوادر والمراجع'
    },
    'fal-ai/flux/dev': {
        'name': 'FLUX.1 [dev]',
        'category': 'image',
        'badge': 'متوازن ويدعم LoRA',
        'type': 'Image Keyframe',
        'calc_shot': lambda p: round(p, 3) if p else 0.025,
        'shot_label': 'كادر سينمائي',
        'recommendation': 'الموديل المعتمد لدمج لورات الممثلين وتوليد الشخصيات المتطابقة بدقة 1080p'
    },
    'blackforestlabs/flux-3/klein/edit-image/lora': {
        'name': 'FLUX 3 Klein Edit LoRA',
        'category': 'image',
        'badge': 'تعديل كادر سريع بالـ LoRA',
        'type': 'Image Edit',
        'calc_shot': lambda p: 0.012,
        'shot_label': 'تعديل كادر',
        'recommendation': 'تعديل الإضاءة والملابس والبيئة مع الحفاظ الكامل على ملامح الممثل بواسطة LoRA'
    },
    'fal-ai/qwen-image-2512/lora': {
        'name': 'Qwen Image 2512 LoRA',
        'category': 'image',
        'badge': 'قفل ملامح متعدد',
        'type': 'Image Keyframe',
        'calc_shot': lambda p: 0.035,
        'shot_label': 'كادر مع لورا',
        'recommendation': 'توليد كوادر سينمائية للشخصيات مع تثبيت الهوية بالـ LoRA بدقة متناهية'
    },
    'fal-ai/qwen-image-edit-2511': {
        'name': 'Qwen-Image-Edit-2511',
        'category': 'image',
        'badge': 'تعديل كادر ذكي',
        'type': 'Image Edit',
        'calc_shot': lambda p: 0.020,
        'shot_label': 'تعديل كادر',
        'recommendation': 'تعديل أجزاء محددة من الصورة بالأوامر النصية مع الحفاظ على باقي الكادر'
    },
    'fal-ai/recraft-v3': {
        'name': 'Recraft V3',
        'category': 'image',
        'badge': 'تصميم وفيكتور',
        'type': 'Vector & Graphic',
        'calc_shot': lambda p: round(p, 2) if p else 0.04,
        'shot_label': 'تصميم أو كادر',
        'recommendation': 'تصاميم فنية مميزة وضبط كامل للألوان والبوسترات'
    },
    'fal-ai/ideogram/v2': {
        'name': 'Ideogram v2',
        'category': 'image',
        'badge': 'تايبوجرافي وبوسترات',
        'type': 'Poster & Design',
        'calc_shot': lambda p: round(p, 2) if p else 0.05,
        'shot_label': 'بوستر أو لافتة',
        'recommendation': 'الأقوى في رسم الحروف والكلمات داخل المشهد وعمل أفيشات الأفلام'
    },
    'fal-ai/flux-pro/v1.1-ultra': {
        'name': 'FLUX.1 [pro] v1.1 Ultra',
        'category': 'image',
        'badge': 'القمة الفوتوغرافية 4K',
        'type': 'Image Keyframe',
        'calc_shot': lambda p: round(p, 3) if p else 0.06,
        'shot_label': 'كادر سينمائي RAW',
        'recommendation': 'أعلى تفاصيل واقعية للمسامات والجلد والإضاءة السينمائية (Raw Film Look)'
    }
}

def load_secrets():
    if os.path.exists(SECRETS_PATH):
        try:
            with open(SECRETS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def fetch_live_fal_prices():
    secrets = load_secrets()
    fal_key = secrets.get('fal_api_key', '').strip()
    if not fal_key:
        return {}
    
    headers = {'Authorization': f'Key {fal_key}'}
    pricing_map = {}
    
    # Query key endpoints individually with small delay to avoid 404 on batch and 429 rate limit
    for ep in FAL_PRICING_ENDPOINTS:
        try:
            r = requests.get(f'https://api.fal.ai/v1/models/pricing?endpoint_id={ep}', headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                for item in data.get('prices', []):
                    matched_ep = item.get('endpoint_id', ep)
                    pricing_map[matched_ep] = {
                        'unit_price': item.get('unit_price'),
                        'unit': item.get('unit'),
                        'currency': item.get('currency', 'USD'),
                        'is_live': True
                    }
            elif r.status_code == 429:
                time.sleep(0.4)
        except Exception:
            pass
        time.sleep(0.08)
        
    return pricing_map

def fetch_live_runpod_gpus():
    secrets = load_secrets()
    runpod_key = secrets.get('runpod_api_key', '').strip()
    if not runpod_key:
        return []
        
    query = """
    query GpuTypes {
        gpuTypes {
            id
            displayName
            memoryInGb
            communityPrice
            lowestPrice(input: {gpuCount: 1}) {
                minimumBidPrice
                uninterruptablePrice
            }
        }
    }
    """
    try:
        r = requests.post(
            'https://api.runpod.io/graphql',
            headers={'Authorization': f'Bearer {runpod_key}', 'Content-Type': 'application/json'},
            json={'query': query},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json().get('data', {}).get('gpuTypes', [])
            result = []
            for g in data:
                name = g.get('displayName') or g.get('id', '')
                mem = g.get('memoryInGb', 0)
                community = g.get('communityPrice')
                low = g.get('lowestPrice', {}) or {}
                uninterruptable = low.get('uninterruptablePrice')
                
                if mem >= 24 or any(t.lower() in name.lower() for t in ['4090', '3090', 'a100', 'l40s']):
                    result.append({
                        'id': g.get('id'),
                        'name': name,
                        'vram': f"{mem} GB VRAM",
                        'on_demand_per_hr': round(float(uninterruptable), 2) if uninterruptable else None,
                        'community_per_hr': round(float(community), 2) if community else None,
                        'approx_per_min': round((float(uninterruptable or community or 0.5) / 60), 3),
                        'recommended_use': 'ComfyUI Wan 2.1 & LoRA Training' if '4090' in name or '3090' in name else ('Heavy 80GB Video Render' if 'a100' in name.lower() else 'Fast Cloud Compute')
                    })
            result.sort(key=lambda x: (x.get('community_per_hr') or x.get('on_demand_per_hr') or 99))
            return result[:8]
    except Exception as e:
        print(f"[Pricing] Error fetching RunPod GPUs: {e}")
    return []

def get_llm_pricing():
    return [
        {
            'name': 'Google Gemini 2.0 / 3.5 Flash',
            'role': 'مساعد المخرج الفوري وتحليل الكوادر والـ Pre-vis',
            'input_rate': 'مجاني (Free Tier) / $0.10 لكل مليون Token',
            'output_rate': '$0.40 لكل مليون Token',
            'cost_per_scene': 'شبه مجاني ($0.00)',
            'status': 'نشط ومعتمد في سندي'
        },
        {
            'name': 'Google Gemini 1.5 Pro',
            'role': 'كتابة السيناريو العميق والرؤية البصرية الشاملة',
            'input_rate': '$1.25 لكل مليون Token',
            'output_rate': '$5.00 لكل مليون Token',
            'cost_per_scene': 'أقل من $0.01',
            'status': 'متاح في الخزنة'
        },
        {
            'name': 'OpenAI GPT-4o',
            'role': 'مراجعة الحوار والدراماتورجيا',
            'input_rate': '$2.50 لكل مليون Token',
            'output_rate': '$10.00 لكل مليون Token',
            'cost_per_scene': '~$0.02',
            'status': 'اختياري'
        },
        {
            'name': 'Anthropic Claude 3.5 Sonnet',
            'role': 'التطوير الإبداعي للشخصيات والأبعاد النفسية',
            'input_rate': '$3.00 لكل مليون Token',
            'output_rate': '$15.00 لكل مليون Token',
            'cost_per_scene': '~$0.03',
            'status': 'اختياري'
        }
    ]

def build_daily_pricing_report(force_refresh=False):
    now = time.time()
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    if not force_refresh and os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                cache_time = cached.get('timestamp', 0)
                if (now - cache_time) < 43200 and len(cached.get('fal_models', [])) >= 20:
                    return cached
        except Exception:
            pass

    fal_prices = fetch_live_fal_prices()
    runpod_gpus = fetch_live_runpod_gpus()
    llms = get_llm_pricing()
    
    models_list = []
    for ep, meta in MODEL_METADATA.items():
        fal_info = fal_prices.get(ep, {})
        unit_p = fal_info.get('unit_price')
        unit = fal_info.get('unit', '')
        
        if unit_p is None:
            if 'motion-control' in ep:
                unit_p = 0.126
                unit = 'seconds'
            elif 'pro/image-to-video' in ep or 'pro/text-to-video' in ep:
                unit_p = 0.098
                unit = 'seconds'
            elif 'standard' in ep:
                unit_p = 0.056
                unit = 'seconds'
            elif 'ray-2/image-to-video' in ep:
                unit_p = 0.50
                unit = '5 seconds'
            elif 'ray-2/modify' in ep:
                unit_p = 0.35
                unit = 'seconds'
            elif 'wan' in ep:
                unit_p = 0.006
                unit = 'seconds'
            elif 'ltx-2.3-22b/image-to-video' in ep:
                unit_p = 0.040
                unit = 'seconds'
            elif 'ltx' in ep:
                unit_p = 0.016
                unit = 'seconds'
            elif 'minimax/h3' in ep:
                unit_p = 0.050
                unit = 'seconds'
            elif 'pixverse' in ep:
                unit_p = 0.036
                unit = 'seconds'
            elif 'topaz' in ep:
                unit_p = 0.024
                unit = 'seconds'
            elif 'flux-pro' in ep:
                unit_p = 0.06
                unit = 'images'
            elif 'flux/dev' in ep:
                unit_p = 0.025
                unit = 'megapixels'
            elif 'flux/schnell' in ep:
                unit_p = 0.003
                unit = 'megapixels'
            elif 'ideogram' in ep:
                unit_p = 0.05
                unit = 'images'
            elif 'recraft' in ep:
                unit_p = 0.04
                unit = 'images'
            elif 'qwen' in ep:
                unit_p = 0.025
                unit = 'images'
            elif 'banana-pro' in ep:
                unit_p = 0.015
                unit = 'images'
            elif 'banana' in ep:
                unit_p = 0.005
                unit = 'images'
            else:
                unit_p = 0.05
                unit = 'unit'
        
        calc_fn = meta['calc_shot']
        estimated_shot = calc_fn(unit_p)
        
        models_list.append({
            'endpoint_id': ep,
            'name': meta['name'],
            'category': meta['category'],
            'badge': meta['badge'],
            'type': meta['type'],
            'unit_price': unit_p,
            'unit': unit,
            'currency': 'USD',
            'estimated_shot_cost': estimated_shot,
            'shot_label': meta['shot_label'],
            'recommendation': meta['recommendation']
        })

    report = {
        'date': today_str,
        'timestamp': now,
        'last_updated_formatted': datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p'),
        'currency': 'USD',
        'fal_models': models_list,
        'runpod_gpus': runpod_gpus,
        'llm_engines': llms,
        'summary': {
            'best_motion_engine': 'Kling Motion Control (1080p) [~$0.63 / 5s]',
            'best_budget_video': 'Wan 2.1 [~$0.03 / 5s]',
            'best_cinema_lora': 'LTX-2.3 22B Cinema LoRA [~$0.20 / 5s]',
            'best_keyframe_artist': 'FLUX.1 [pro] v1.1 Ultra [$0.06 / كادر]',
            'best_gpu_setup': 'RTX 4090 (24GB) [~$0.34/hr Community - صفر تكلفة API]'
        }
    }
    
    try:
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Pricing] Error saving cache: {e}")
        
    return report

if __name__ == '__main__':
    rep = build_daily_pricing_report(force_refresh=True)
    print(f"Daily Pricing Report generated successfully for: {rep['date']}")
    print(f"Total Fal Models tracked: {len(rep['fal_models'])}")
    print(f"Total RunPod GPUs tracked: {len(rep['runpod_gpus'])}")
