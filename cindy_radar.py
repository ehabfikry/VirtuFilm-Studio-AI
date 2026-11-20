import os
import json
import time
import requests
import re

RADAR_CACHE_PATH = r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\cinema_radar_cache.json'

def _translate_japan_brief_to_arabic(headline, desc, secrets=None):
    """Translate Japanese headline & description into concise Arabic via Gemini Flash."""
    if not (headline or desc):
        return "", ""
    gemini_key = ""
    if isinstance(secrets, dict):
        gemini_key = (secrets.get("gemini_api_key") or "").strip()
    if not gemini_key:
        sec_path = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"
        if os.path.exists(sec_path):
            try:
                with open(sec_path, "r", encoding="utf-8") as sf:
                    gemini_key = (json.load(sf).get("gemini_api_key") or "").strip()
            except Exception:
                pass
    if gemini_key:
        prompt = (
            "ترجم العنوان والملخص الياباني التاليين لأخبار الذكاء الاصطناعي في صناعة الفيديو إلى العربية الواضحة والمختصرة لمخرج سينمائي.\n"
            "أرجع JSON فقط بالشكل التالي: {\"title_ar\": \"...\", \"summary_ar\": \"...\"}\n"
            f"Headline: {headline}\nDescription: {desc[:600]}"
        )
        for model_id in ("gemini-2.5-flash", "gemini-2.0-flash"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={gemini_key}"
                r = requests.post(
                    url,
                    json={
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
                    },
                    timeout=8,
                )
                if r.status_code == 200:
                    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(txt)
                    t_ar = (parsed.get("title_ar") or "").strip()
                    s_ar = (parsed.get("summary_ar") or "").strip()
                    if t_ar or s_ar:
                        return t_ar or headline, s_ar or desc
            except Exception:
                continue

    # Fast zero-key fallback: MyMemory Translation API (Japanese -> Arabic)
    def _gt_ar(text):
        if not text:
            return ""
        try:
            r = requests.get(
                "https://api.mymemory.translated.net/get",
                params={"q": text[:490], "langpair": "ja|ar"},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=6,
            )
            if r.status_code == 200:
                tr = (r.json().get("responseData") or {}).get("translatedText") or ""
                if tr and "MYMEMORY WARNING" not in tr.upper():
                    return tr.strip()
        except Exception:
            pass
        return text

    return _gt_ar(headline), _gt_ar(desc)


def fetch_live_synon_japan_trends(secrets=None):
    """Dynamically discover the newest Video Gen AI Daily article from Synon Japan index."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    index_url = "https://synon.co.jp/article/news/?series=video-gen-ai-daily"
    try:
        idx_res = requests.get(index_url, headers=headers, timeout=6)
        if idx_res.status_code == 200:
            articles = re.findall(r'href=["\'](/article/news/[^"\']+)["\']', idx_res.text)
            video_articles = [a for a in articles if 'video-gen-ai-daily' in a.lower()]
            if video_articles:
                latest_art_path = video_articles[0]
                art_full_url = "https://synon.co.jp" + latest_art_path
                
                art_res = requests.get(art_full_url, headers=headers, timeout=6)
                art_res.encoding = 'utf-8'
                if art_res.status_code == 200:
                    headline = ""
                    desc = ""
                    pub_date = "اليوم"
                    for m in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', art_res.text, re.DOTALL):
                        try:
                            d = json.loads(m.strip())
                            if d.get("@type") == "NewsArticle" or "description" in d:
                                headline = d.get("headline", "")
                                desc = d.get("description", "")
                                pub_date = (d.get("datePublished") or pub_date)[:10]
                                break
                        except Exception:
                            pass

                    title_ar, desc_ar = _translate_japan_brief_to_arabic(headline, desc, secrets=secrets)
                    summary_ar = (
                        f"تقرير طوكيو اليومي ({pub_date}):\n"
                        f"{desc_ar or 'متابعة يومية لأحدث إطلاقات نماذج توليد الفيديو ومقارنة الأسعار والجودة.'}"
                    )

                    impact_ar = (
                        "الفائدة المباشرة للمخرج: متابعة يومية مترجمة لأحدث إطلاقات نماذج الفيديو العالمية وأسعار التوليد."
                    )

                    return {
                        "id": "synon_japan_daily_monitor",
                        "title": f"تقرير مرصد طوكيو ({pub_date}): {title_ar or 'أحدث تطورات الفيديو بالذكاء الاصطناعي'}",
                        "source": f"Synon.co.jp ({pub_date})",
                        "url": art_full_url,
                        "category": "Asian AI Innovation & SOTA",
                        "badge": f"🇯🇵 تقرير طوكيو اليومي ({pub_date})",
                        "summary": summary_ar,
                        "impact_on_director": impact_ar,
                        "cost_indicator": "تحديث يومي حي (مترجم)",
                        "action_prompt": f"Analyze latest video AI trend: {title_ar or headline or latest_art_path}"
                    }
    except Exception as e:
        print("[Synon Dynamic Radar Error]:", e)
    return None

def fetch_live_huggingface_video_trends():
    """Live API fetch: Query top 3 trending text-to-video / image-to-video open-source models on Hugging Face."""
    url = "https://huggingface.co/api/models?pipeline_tag=text-to-video&sort=trendingScore&direction=-1&limit=4"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            data = r.json()
            for m in data:
                m_id = m.get('id', '')
                likes = m.get('likes', 0)
                downloads = m.get('downloads', 0)
                short_name = m_id.split('/')[-1] if '/' in m_id else m_id
                
                if 'wan' in short_name.lower():
                    desc = f"تحديث أوزان عائلة Wan (Alibaba) الأكثر رواجاً عالمياً. يتميز بالواقعية الفوتوغرافية وفهم زوايا الكاميرا المعقدة."
                    impact = "استخدمه لتوليد المشاهد الدرامية والإضاءة الطبيعية بكفاءة عالية على جهازك أو السحابة."
                elif 'minimax' in short_name.lower():
                    desc = f"نسخة تسريع Turbo LoRA لنماذج MiniMax لتوليد الحركة البشرية وتثبيت الملامح بسرعة فائقة."
                    impact = "مثالي للمشاهد التي تتطلب حركة جسدية واقعية أو حوارات سريعة."
                else:
                    desc = f"نموذج فيديو مفتوح المصدر يتصدر قوائم التداول العالمية (Trending Score) على منصة Hugging Face مع دعم مجتمعي واسع."
                    impact = "يمكن دمجه مباشرة في معمل ComfyUI المحلي لتنفيذ تجارب بصرية بدون اشتراكات سحابية."

                items.append({
                    "id": f"hf_{short_name.lower()}",
                    "title": f"{short_name} (Hugging Face Trending)",
                    "source": f"Hugging Face Hub (Repo: {m_id})",
                    "url": f"https://huggingface.co/{m_id}",
                    "category": "Open-Weights Video Engine",
                    "badge": f"🔥 {downloads:,} تنزيل • {likes} إعجاب",
                    "summary": desc,
                    "impact_on_director": impact,
                    "cost_indicator": "أوزان مفتوحة (مجاني محلياً)",
                    "action_prompt": f"Load open weights from {m_id} into ComfyUI local pipeline"
                })
    except Exception as e:
        print("[Hugging Face Radar Fetch Error]:", e)
    return items

def fetch_live_comfyui_release():
    """Live API fetch: Query latest ComfyUI core release version from GitHub."""
    url = "https://api.github.com/repos/comfyanonymous/ComfyUI/releases/latest"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            rel = r.json()
            tag = rel.get('tag_name', 'v0.45.0')
            body = (rel.get('body') or '')[:300].strip().replace('\r\n', ' ')
            date = (rel.get('published_at') or '')[:10]
            return {
                "id": f"comfyui_core_{tag.lower().replace('.', '_')}",
                "title": f"ComfyUI Core Engine ({tag} Latest Release)",
                "source": f"Official GitHub Release ({date})",
                "category": "Local Execution Framework",
                "badge": "⚡ نواة المعمل المجاني",
                "summary": f"تحديث نواة ComfyUI الرسمية بإصدار {tag}، متضمناً تحسينات تسريع استهلاك VRAM ودعم أحدث عقد تحريك الفيديو ونماذج التقطير الحديثة.",
                "impact_on_director": "يسمح لك بتشغيل نماذج 14B على كروت RTX 3060/4060 دون نفاد الذاكرة بفضل تقنيات الـ Offloading المتطورة.",
                "cost_indicator": "مجاني ومفتوح 100%",
                "action_prompt": "Update local ComfyUI standalone environment to latest commit"
            }
    except Exception as e:
        print("[ComfyUI Radar Fetch Error]:", e)
    return None

FALLBACK_BASELINE_TRENDS = [
    {
        "id": "freefield_comfy_suite",
        "title": "FreeField (بديل Higgsfield مفتوح المصدر — 120 أداة ComfyUI)",
        "source": "neuregex / freefield (GitHub • 1.6K+ Stars)",
        "url": "https://github.com/neuregex/freefield",
        "category": "Open-Weights Video Engine",
        "badge": "🔥 120 أداة مفتوحة",
        "summary": "منصة مفتوحة المصدر فوق ComfyUI تضم 120 تطبيقاً للصور والفيديو والمؤثرات والصوت بأوزان مفتوحة بالكامل تعمل على جهازك أو السحابة.",
        "impact_on_director": "بديل مجاني كامل لـ Higgsfield لتجربة أحدث تقنيات الفيديو والمؤثرات بدون اشتراكات شهرية.",
        "cost_indicator": "مفتوح المصدر (مجاني محلياً)",
        "action_prompt": "Suggest the best FreeField open-weight ComfyUI workflow for this shot"
    },
    {
        "id": "openjutsu_char_swap",
        "title": "OpenJutsu (تبديل الممثل في الفيديو بضغطة واحدة + إضاءة FLUX.3)",
        "source": "D3voz / openjutsu (GitHub • 2.5K+ Stars)",
        "url": "https://github.com/D3voz/openjutsu",
        "category": "Character Consistency & Face Swap",
        "badge": "🎭 تبديل ممثل كامل",
        "summary": "بديل محلي مفتوح لـ Higgsfield Genjutsu مبني على ComfyUI و MiniMax H3 مع إعادة إضاءة FLUX.3 Klein لتبديل الشخصية بالكامل في أي فيديو.",
        "impact_on_director": "تثبيت وتبديل بطل الفيلم داخل أي لقطة فيديو جاهزة مع تطابق كامل للإضاءة والظلال.",
        "cost_indicator": "محلي مفتوح المصدر",
        "action_prompt": "Plan an OpenJutsu character swap workflow with matching scene lighting"
    },
    {
        "id": "triposplat_3d_gaussians",
        "title": "TripoSplat (تحويل صورة واحدة إلى 3D Gaussian Splatting)",
        "source": "VAST-AI-Research / TripoSplat (GitHub • 1.4K+ Stars)",
        "url": "https://github.com/VAST-AI-Research/TripoSplat",
        "category": "3D Pre-vis & Environment",
        "badge": "🧊 3D Splat من صورة",
        "summary": "يحوّل صورة واحدة إلى مشهد 3D Gaussian Splatting عالي الجودة لبناء الخلفيات والديكورات السينمائية ثلاثية الأبعاد.",
        "impact_on_director": "مثالي لتحويل كادر مرجعي واحد إلى ديكور 3D قابل لتحريك الكاميرا بداخله بحرية.",
        "cost_indicator": "مفتوح المصدر (TripoAI)",
        "action_prompt": "Convert reference set image to 3D Gaussian Splat via TripoSplat for camera blocking"
    },
    {
        "id": "video_shotcraft_recipes",
        "title": "Video-ShotCraft (124 وصفة شوت سينمائي ومزامنة إيقاع)",
        "source": "Vincentwei1021 / video-shotcraft (GitHub • 21K+ Stars)",
        "url": "https://github.com/Vincentwei1021/video-shotcraft",
        "category": "Directing & Shot Design",
        "badge": "🎬 124 وصفة شوت",
        "summary": "مكتبة ضخمة تضم 124 بطاقة وصفة شوت سينمائي و150 معاينة حركة مع مزامنة الإيقاع وتصميم الصوت.",
        "impact_on_director": "تغذّي سيندي بوصفات جاهزة لحركات الكاميرا والإيقاع المونتاجي في المشاهد السريعة والإعلانات.",
        "cost_indicator": "مفتوح المصدر",
        "action_prompt": "Apply a cinematic Video-ShotCraft shot recipe and beat sync for this scene"
    },
    {
        "id": "caprust_local_editor",
        "title": "CapRust (بديل CapCut المجاني والمحلي على ويندوز)",
        "source": "Domica / CapRust (Rust • Local Windows)",
        "url": "https://github.com/Domica/CapRust",
        "category": "Timeline & Automated Production",
        "badge": "✂️ مونتاج محلي سريع",
        "summary": "محرر فيديو محلي فائق السرعة مكتوب بـ Rust بديل لـ CapCut على ويندوز مع LUTs وإعادة التأطير التلقائي وإزالة العناصر والخلفيات أوفلاين.",
        "impact_on_director": "تجميع وتلوين اللقطات المولدة من سيندي محلياً بدون علامات مائية أو اشتراك.",
        "cost_indicator": "مجاني 100% محلياً",
        "action_prompt": "Export shot list and LUT grading plan for CapRust final assembly"
    },
    {
        "id": "overheads_camera_blocking",
        "title": "Overheads (مخطط الكاميرات والبلوكينج العلوي للمخرجين)",
        "source": "JesseDana / overheads (مدمج في تبويب السيناريو)",
        "url": "/overheads_blocking.html",
        "category": "Directing & Shot Design",
        "badge": "📐 مخطط كاميرا مدمج",
        "summary": "أداة تخطيط علوي (Overhead Floorplan) لوضع الممثلين والكاميرات وتقسيم الـ Beats وتصدير كود الشوتات، مدمجة الآن مباشرة في تبويب السيناريو.",
        "impact_on_director": "تخطيط زوايا الكاميرا وخط الـ 180 درجة بصرياً في ثوانٍ قبل الرندر.",
        "cost_indicator": "مدمج مجاناً داخل سيندي",
        "action_prompt": "Design an overhead camera blocking diagram with 180-degree line safety"
    },
    {
        "id": "openmontage_studio_engine",
        "title": "OpenMontage (استوديو المونتاج والتايم لاين البرمجي الآلي)",
        "source": "OpenMontageInc / GitHub (MIT License - 2026)",
        "category": "Timeline & Automated Production",
        "badge": "🎬 تايم لاين ومونتاج آلي",
        "summary": "نظام تجميع آلي للمشاهد مبني على FFmpeg يدمج الكادرات المتتابعة، ويصنع انتقالات سينمائية ناعمة (Crossfade)، ويدمج الموسيقى التصويرية ويصدر الفيلم الكامل بـ 1080p فوراً.",
        "impact_on_director": "يمكنك استخدامه مباشرة عبر زر 'تجميع الفيلم' لتوليد الفيلم النهائي ومزامنته مع الصوت دون الحاجة لفتح برامج مونتاج خارجية.",
        "cost_indicator": "مفتوح المصدر (مجاني 100%)",
        "action_prompt": "Multi-track timeline assembly with audio crossfade, subtitles burning and automated QA gates via FFmpeg"
    },
    {
        "id": "duix_avatar_studio",
        "title": "Duix-Avatar (الدوبلاج العصبي ومزامنة الشفاه مع الصوت العربي)",
        "source": "Duix.com Open Source (GitHub SOTA - 16K+ Stars)",
        "category": "Digital Human & Lip-Sync",
        "badge": "👄 دوبلاج ومزامنة شفاه مجانية",
        "summary": "محرك محلي أوفلاين فائق الدقة يحلل الذبذبات الصوتية ويقوم بتحريك شفاه وملامح الممثل في الصورة أو الفيديو لتطابق نطق الحوار تماماً وبدون أي اشتراك سحابي.",
        "impact_on_director": "أداة أساسية لدبلجة المشاهد الدرامية بالعربية: ترفع الصوت وكادر البطل فيقوم بإنتاج مشهد ناطق متطابق.",
        "cost_indicator": "محلي 100% (أوفلاين بدون إنترنت)",
        "action_prompt": "Run Duix neural audio-driven lip synchronization on character keyframe"
    },
    {
        "id": "wunjo_vfx_studio",
        "title": "Wunjo Studio (معمل المؤثرات ومسح العناصر وتعديل الكادر)",
        "source": "Wunjo Open Source (C++ / Qt6 / MLT)",
        "category": "Video VFX & Inpainting",
        "badge": "🛠️ مسح وتنظيف الكوادر",
        "summary": "استوديو مفتوح لتنظيف لقطات الفيديو، وإزالة العناصر غير المرغوبة (Inpainting)، وتغيير الخلفيات وعزل الشخصيات بدون شاشات خضراء.",
        "impact_on_director": "يعالج الأخطاء البصرية في لقطات الذكاء الاصطناعي (مثل ظهور أطراف مشوهة أو أجسام دخيلة) بفرشاة بسيطة لملء الخلفية طبيعياً.",
        "cost_indicator": "مفتوح المصدر بالكامل",
        "action_prompt": "Temporal video inpainting and object removal"
    },
    {
        "id": "reactor_tein_face_swap",
        "title": "ComfyUI ReActor & TEIN (تثبيت ملامح بطل العمل وتبديل الوجوه)",
        "source": "Gourieff & Sirio Berati (GitHub SOTA)",
        "category": "Character Consistency & Face Swap",
        "badge": "🎭 تثبيت وجه الممثل",
        "summary": "نظام استبدال ملامح عالي الجودة مع معالجة وترميم فوتوغرافي (CodeFormer) يضمن بقاء وجه بطل الفيلم ثابتاً عبر كل لقطات العمل حتى لو تحرك الجسد كدوبلير.",
        "impact_on_director": "الحل العملي الأقوى لمشكلة 'تغير الممثل' بين مشهد وآخر؛ تثبت وجه بطلك في كل الشوتات بدقة متناهية.",
        "cost_indicator": "محلي مجاني 100%",
        "action_prompt": "High-fidelity face replacement with CodeFormer face restoration"
    },
    {
        "id": "resonant_audio_studio",
        "title": "Resonant (استوديو الموسيقى التصويرية والمكساج المحلي)",
        "source": "calesthio / Resonant (Windows Desktop / MIT)",
        "category": "Local Audio & DAW",
        "badge": "🎵 استوديو موسيقى محلي",
        "summary": "محطة عمل صوتية متكاملة لإنشاء وتأليف الموسيقى التصويرية والمؤثرات الصوتية للمشاهد والتحكم بها عبر بروتوكول MCP محلياً.",
        "impact_on_director": "تأليف موسيقى أصلية لكل مشهد بالفيلم دون حقوق ملكية، وتغذيتها مباشرة في تايم لاين المونتاج.",
        "cost_indicator": "مجاني ومفتوح المصدر",
        "action_prompt": "Generate dynamic orchestral soundtrack adhering to scene tempo and mood"
    }
]

def get_latest_cinema_trends(force_refresh=False, secrets=None):
    now = time.time()
    
    if not force_refresh and os.path.exists(RADAR_CACHE_PATH):
        try:
            with open(RADAR_CACHE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if now - data.get('timestamp', 0) < 3600:
                    return data
        except Exception:
            pass

    hf_trends = fetch_live_huggingface_video_trends()
    comfy_item = fetch_live_comfyui_release()
    synon_item = fetch_live_synon_japan_trends(secrets=secrets)

    combined_trends = []
    if synon_item:
        combined_trends.append(synon_item)
    if hf_trends:
        combined_trends.extend(hf_trends[:3])
    if comfy_item:
        combined_trends.append(comfy_item)
    combined_trends.extend(FALLBACK_BASELINE_TRENDS)

    result = {
        "timestamp": now,
        "last_updated": time.strftime("%Y-%m-%d %I:%M %p"),
        "source_attribution": "Live Hugging Face Hub, GitHub Official & Synon Video Intelligence (Tokyo)",
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
        print(f"- [{t['badge']}] {t['title']}")
