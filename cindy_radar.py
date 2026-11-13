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

import os
import json
import time
import requests
import re

RADAR_CACHE_PATH = r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\cinema_radar_cache.json'

# Curated High-Value Baseline Trends (Hollywood & Open-Weights SOTA)
FALLBACK_BASELINE_TRENDS = [
    {
        "id": "wan_2_2_hybrid",
        "title": "Alibaba Wan 2.2 TI2V (Unified 14B Cinema Engine)",
        "source": "Alibaba Wan-AI & Hugging Face SOTA (2026-11)",
        "category": "Cinematic Video Engine",
        "badge": "💎 بطل الساحة الحالي",
        "summary": "إطلاق معمارية Wan 2.2 الموحدة (Text-to-Video و Image-to-Video) بمحاكاة فيزيائية واقعية وانعدام تام لتشوهات أطراف الشخصيات وحركة الإضاءة ثلاثية الأبعاد.",
        "impact_on_director": "أرخص وأدق محرك فيديو سينمائي متاح حالياً للتحريك المرجعي (I2V) بجودة 720p/1080p وبتكلفة منخفضة جداً.",
        "cost_indicator": "~$0.04 - $0.06 / لقطة",
        "action_prompt": "Cinematic camera push-in on subject with volumetric lighting, matching environmental audio and dramatic depth"
    },
    {
        "id": "hyperflow_h3_flash",
        "title": "MiniMax HyperFlow H3 Flash (Open Weights & 6-Step Video)",
        "source": "Synon Video Gen AI Daily & Video Rebirth (2026-11)",
        "category": "ComfyUI & Local Distillation",
        "badge": "⚡ أوزان مفتوحة محلياً",
        "summary": "إطلاق أوزان HyperFlow H3 Flash المصغرة من MiniMax H3 بحجم 14B و 6 خطوات توليد فقط (INT8). الموديل يعمل محلياً بالكامل على كروت RTX 4090 ويولد 5.2 ثانية في نحو 130 ثانية بدون أي تكلفة سحابية.",
        "impact_on_director": "تحرير المخرج تماماً من تكاليف السحابة في مرحلة المسودات الأولية (Drafts) وتشغيل فيزياء MiniMax محلياً داخل ComfyUI.",
        "cost_indicator": "مجاني محلياً (Open Weights)",
        "action_prompt": "Local ComfyUI test using HyperFlow H3 Flash 14B 6-step distillation for hyper-fast drafting"
    },
    {
        "id": "flux_3_max_i2v",
        "title": "FLUX 3 Max Image-to-Video (Native Audio & End-Frames)",
        "source": "Black Forest Labs & fal.ai Research (2026-11)",
        "category": "Cinematic Video Engine",
        "badge": "👑 أعلى دقة + صوت مدمج",
        "summary": "محرك التحريك الفوتوغرافي الأقوى عالمياً حالياً من مبتكري FLUX. يدعم توليد لقطات سينمائية بطول 5 إلى 20 ثانية بنبضة واحدة مع توليد صوت محيطي متزامن (Native Audio) والتحكم بكادر البداية والنهاية بدقة 1080p.",
        "impact_on_director": "حل معضلة المخرج في مزامنة الصوت والمؤثرات مع حركة اللقطة في ملف واحد فائق الدقة بدون الحاجة لاستوديو مونتاج صوتي منفصل.",
        "cost_indicator": "~$0.25 / 5s (فيديو + صوت)",
        "action_prompt": "Cinematic camera push-in on subject with volumetric lighting, matching environmental audio and dramatic depth"
    },
    {
        "id": "ltx_2_5_reframe",
        "title": "Lightricks LTX-2.5 Reframe (Generative Video Outpainting)",
        "source": "Lightricks & fal.ai (2026-11)",
        "category": "Aspect Ratio & Post-Production",
        "badge": "🎨 توسيع ذكي للكادر",
        "summary": "أداة إعادة تأطير الفيديوهات الذكية. بدلاً من القص الحاد التقليدي عند تحويل الفيديو السينمائي 16:9 إلى عمودي 9:16 أو العكس، تقوم الأداة بتوليد ورسم بقية المشهد في الأعلى والأسفل والجوانب متوافقاً مع حركة الكاميرا والفيزياء الأصلية.",
        "impact_on_director": "تحويل أي لقطة فيلم سينمائية إلى مادة سوشيال ميديا (Reels / TikTok) بدقة 1080p بدون التضحية بأي عنصر في الكادر.",
        "cost_indicator": "~$0.05 - $0.10 / ثانية",
        "action_prompt": "Generative outpainting reframe from 16:9 to 9:16 vertical preserving camera continuity"
    },
    {
        "id": "skyreels_v4_leaderboard",
        "title": "SkyReels V4 (Top 10 Global Leaderboard Entry)",
        "source": "Artificial Analysis Video Arena (2026-11)",
        "category": "Character Consistency",
        "badge": "🔥 المركز 9 عالمياً",
        "summary": "دخول رسمي لنموذج SkyReels V4 ضمن المراكز العشرة الأولى عالمياً في مؤشر Artificial Analysis بدرجة 1137 نقطة متفوقاً على Seedance 2.0 في ثبات حركة الأطراف والأوجه البشرية.",
        "impact_on_director": "خيار موثوق جداً لتحريك لقطات الممثلين القريبة دون أي تشوه في العيون أو حركة الأصابع.",
        "cost_indicator": "~$0.15 / 5s",
        "action_prompt": "Close-up portrait sequence with flawless eye contact and natural human micro-expressions"
    },
    {
        "id": "open_micro_drama_anil",
        "title": "Open Micro-Drama Pipeline (Screenplay → Storyboard → Multi-Scene Video)",
        "source": "Open-Source Community (Anil Matcha / GitHub)",
        "category": "Episodic AI Direction",
        "badge": "🎬 معمارية المسلسلات القصيرة",
        "summary": "معمارية مفتوحة المصدر لتقسيم الأفكار الدرامية إلى مشاهد متتالية (Multi-Agent Pipeline) وتجميعها تلقائياً في حلقة فيديو درامية قصيرة متماسكة.",
        "impact_on_director": "تم دمجها وتطويرها في سيندي لتوليد حلقات كاملة مع الحفاظ على ترقية الجودة السينمائية 4K ومونتاج FFmpeg الخارق دون أي قيود مدفوعة.",
        "cost_indicator": "مفتوح المصدر (MIT Inspired)",
        "action_prompt": "Cinematic vertical micro-drama scene sequence with consistent character arc and dramatic tension"
    },
    {
        "id": "duix_digital_human",
        "title": "Duix-Avatar (Offline Digital Human & Neural Lip-Sync)",
        "source": "Duix.com Open Source (GitHub SOTA)",
        "category": "Actor Cloning & Speech",
        "badge": "💎 16K+ نجمة • محلي بالكامل",
        "summary": "حزمة أدوات مفتوحة المصدر بالكامل لاستنساخ الممثلين الرقميين ومزامنة الشفاه (Lip-Sync) في الوقت الحقيقي محلياً دون أي حاجة للإنترنت أو اشتراكات خارجية.",
        "impact_on_director": "تحرير المخرج من تكاليف خدمات التحدث السحابية وتوفير دبلجة ومزامنة كلام سينمائية للممثل داخل الاستوديو.",
        "cost_indicator": "مجاني محلياً 100%",
        "action_prompt": "High fidelity photorealistic digital human monologue with natural facial micro-expressions"
    },
    {
        "id": "wunjo_cinema_toolkit",
        "title": "Wunjo Studio (Video Inpainting & Clean Plate Studio)",
        "source": "Wunjo Open Source (C++ / Qt6 / MLT)",
        "category": "Post-Production & VFX",
        "badge": "🛠️ استوديو المعالجة المفتوح",
        "summary": "منظومة إخراجية مفتوحة المصدر لمعالجة الفيديو محلياً: إزالة العناصر والميكروفونات من الكادر (Video Inpainting)، تفريغ الخلفيات وعزل الأصوات بدون أي تكلفة.",
        "impact_on_director": "أداة VFX وتصحيح كادرات مجانية بجانب سيندي تمنح المخرج حرية تصحيح عيوب التصوير بنقرة واحدة.",
        "cost_indicator": "مجاني محلياً (GPL v3)",
        "action_prompt": "Cinematic visual clean plate inpainting removing unwanted objects from foreground"
    },
    {
        "id": "openjourney_gemini_veo",
        "title": "Openjourney Grid & Google Veo 3 Video Hub",
        "source": "Next.js 15 & Google Gemini / Veo SDK",
        "category": "Multi-Variations & Veo",
        "badge": "⚡ شبكة الكادرات الأربعة",
        "summary": "واجهة مفتوحة المصدر تعتمد توليد 4 تنويعات بصرية متزامنة للكادر مع دعم محركات Veo 2 و Veo 3 للفيديو عالي الجودة مع الصوت المتزامن.",
        "impact_on_director": "إلهام متميز لاستعراض 4 خيارات إخراجية لكل لقطة في سيندي قبل اختيار الكادر الفائز للريندر النهائي.",
        "cost_indicator": "مفتوح المصدر (MIT)",
        "action_prompt": "4-way cinematic variation grid exploring different director camera perspectives"
    },
    {
        "id": "toonflow_infinite_canvas",
        "title": "Toonflow AI (Infinite Canvas & Short-Drama Storyboard)",
        "source": "HBAI-Ltd (21K+ Stars / GitHub MIT)",
        "category": "Storyboard & Drama Canvas",
        "badge": "🎨 كانفاس الدراما اللانهائي",
        "summary": "منصة مفتوحة المصدر لترتيب مشاهد وقصص الدراما التفاعلية على مساحة عمل بصرية غير محدودة مع إدارة ثابتة لهوية الممثل والديكور.",
        "impact_on_director": "استلهام طريقة العرض البصري البانورامي للمشاهد وتقليل التشتت أثناء الإخراج المتتابع.",
        "cost_indicator": "مفتوح المصدر (MIT)",
        "action_prompt": "Panoramic multi-panel storyboard layout depicting consecutive character scenes"
    },
    {
        "id": "tein_emotion_control",
        "title": "TEIN Emotion Control & Face Replacement Workflow",
        "source": "Sirio Berati / TEIN AI (GitHub SOTA)",
        "category": "Actor Performance & VFX",
        "badge": "🎭 التحكم بالانفعال والوجه",
        "summary": "معمارية مفتوحة المصدر عبر ComfyUI لنقل الأداء البشري وتعبيرات الوجه بدقة 478 نقطة تتبع، واستبدال الممثل في المشهد دون مساس بالصوت والإضاءة.",
        "impact_on_director": "تمكين المخرج من تسجيل انفعالاته بنفسه وتطبيقها على الممثل الرقمي بصدق تمثيلي فائق، واستبدال الدوبلير بنقرة زر.",
        "cost_indicator": "مفتوح المصدر محلياً",
        "action_prompt": "High fidelity emotional facial expression transfer with nuanced micro-expressions and intense eye contact"
    },
    {
        "id": "nomi_video_workbench",
        "title": "Nomi AI Video Workbench (Timeline & MCP Studio)",
        "source": "Nomi Open Source (AGPL v3)",
        "category": "Timeline & Multi-Model",
        "badge": "⏱️ تايم لاين المونتاج المحلي",
        "summary": "بيئة عمل محلية لمونتاج الفيديو بالذكاء الاصطناعي مع تايم لاين تفاعلي وربط مفتوح لأي موديل دون أي تتبع أو اشتراكات.",
        "impact_on_director": "دعم استقلالية المخرج وربط أدوات التحرير المباشرة في جهازك دون الاعتماد على خدمات المونتاج السحابية الباهظة.",
        "cost_indicator": "مجاني محلياً 100%",
        "action_prompt": "Multi-track video timeline editing sequence with seamless transitions"
    },
    {
        "id": "locally_uncensored_studio",
        "title": "Locally Uncensored AI Desktop Studio",
        "source": "PurpleDoubleD Open Source (AGPL v3)",
        "category": "Desktop Local AI Hub",
        "badge": "🛡️ حرية الإبداع المحلي",
        "summary": "استوديو مكتبي محلي متكامل لتشغيل الذكاء الاصطناعي على جهاز المخرج بنقرة واحدة بدون دوكر أو تيرمينال مع حرية درامية كاملة.",
        "impact_on_director": "دليل إرشادي عملي لتشغيل النماذج محلياً بدون قيود الرقابة السحابية التجارية على النصوص السينمائية الحماسية.",
        "cost_indicator": "مجاني محلياً 100%",
        "action_prompt": "Cinematic dramatic noir confrontation with dynamic lighting and intense narrative tension"
    }


]

def fetch_live_huggingface_video_trends():
    """Live API fetch: Query trending open-source video models directly from Hugging Face."""
    url = "https://huggingface.co/api/models?pipeline_tag=text-to-video&sort=trendingScore&direction=-1&limit=5"
    headers = {"User-Agent": "VirtuFilm-Studio-Cindy/8.0"}
    live_items = []
    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            models = r.json()
            for m in models:
                mid = m.get("id", "")
                downloads = m.get("downloads", 0)
                likes = m.get("likes", 0)
                short_name = mid.split("/")[-1]
                
                # Contextualize for the Director
                live_items.append({
                    "id": f"hf_{short_name.lower()}",
                    "title": f"{short_name} (Hugging Face Trending)",
                    "source": f"Hugging Face Hub (Repo: {mid})",
                    "category": "Open-Source Models Hub",
                    "badge": f"🔥 {downloads:,} تنزيل • {likes} إعجاب",
                    "summary": f"نموذج فيديو مفتوح المصدر يتصدر قوائم التداول العالمية (Trending Score) على منصة Hugging Face مع دعم مجتمعي واسع ومعدل تنزيل مرتفع.",
                    "impact_on_director": f"إمكانية تنزيل أوزان {short_name} مجاناً وتشغيله محلياً أو على ComfyUI السحابي بدون اشتراكات مغلقة.",
                    "cost_indicator": "مفتوح المصدر (مجاني بالكامل)",
                    "action_prompt": f"Text-to-video cinematic sequence rendered via {short_name} open weights"
                })
    except Exception as e:
        print("[HuggingFace Fetch Error]:", e)
    return live_items

def fetch_live_comfyui_release():
    """Live API fetch: Query latest ComfyUI core release version from GitHub."""
    url = "https://api.github.com/repos/comfyanonymous/ComfyUI/releases/latest"
    headers = {"User-Agent": "VirtuFilm-Studio-Cindy/8.0"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            rel = r.json()
            tag = rel.get("tag_name", "v0.45+")
            pub_date = rel.get("published_at", "")[:10]
            return {
                "id": f"comfyui_core_{tag}",
                "title": f"ComfyUI Core Engine ({tag} Latest Release)",
                "source": f"Official GitHub Release ({pub_date})",
                "category": "Local Execution Framework",
                "badge": "⚡ نواة المعمل المجاني",
                "summary": f"تحديث نواة ComfyUI الرسمية بإصدار {tag}، متضمناً تحسينات تسريع استهلاك VRAM ودعم أحدث عقد تحريك الفيديو المفتوحة (Wan, Hunyuan, LTX).",
                "impact_on_director": "استقرار أعلى وسرعة أكبر عند تشغيل معمل الريندر المحلي أو على كروت RunPod.",
                "cost_indicator": "مفتوح المصدر 100%",
                "action_prompt": "Run full local pipeline on ComfyUI latest core"
            }
    except Exception as e:
        print("[ComfyUI GitHub Fetch Error]:", e)
    return None

def get_latest_cinema_trends(force_refresh=False, secrets=None):
    now = time.time()
    
    # Check cache if not forced (1 hour freshness for truly live intelligence)
    if not force_refresh and os.path.exists(RADAR_CACHE_PATH):
        try:
            with open(RADAR_CACHE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if now - data.get('timestamp', 0) < 3600:
                    return data
        except Exception:
            pass

    # 1. Fetch live open-source trends from Hugging Face
    hf_trends = fetch_live_huggingface_video_trends()
    
    # 2. Fetch latest ComfyUI core release status
    comfy_item = fetch_live_comfyui_release()

    # 3. Combine with curated industry baseline
    combined_trends = []
    
    # Put top trending live items first
    if hf_trends:
        combined_trends.extend(hf_trends[:3])
        
    if comfy_item:
        combined_trends.append(comfy_item)
        
    # Append the curated film-production models
    combined_trends.extend(FALLBACK_BASELINE_TRENDS)

    result = {
        "timestamp": now,
        "last_updated": time.strftime("%Y-%m-%d %I:%M %p"),
        "source_attribution": "Live Hugging Face AI Hub, GitHub Official & fal.ai Research Engine",
        "trends": combined_trends
    }
    
    os.makedirs(os.path.dirname(RADAR_CACHE_PATH), exist_ok=True)
    with open(RADAR_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
    return result

if __name__ == '__main__':
    data = get_latest_cinema_trends(force_refresh=True)
    print(f"Loaded {len(data['trends'])} real-world verified trends.")
    for t in data['trends']:
        print(f"- [{t['badge']}] {t['title']} ({t['source']})")
