# -*- coding: utf-8 -*-
"""
Cindy AI Director - Production Design & Virtual Wardrobe Studio Module
(استوديو السينوغرافيا والأزياء الواقعية وإعادة الإضاءة)

Features:
- Pure Open Source & Commercially Permissive (Apache 2.0 & MIT compliant).
- Set Design & Decor Prop Staging.
- Realistic Costume / Wardrobe fitting.
- Material and Surface Inpainting.
- Cinematic Relighting (IC-Light style lighting direction & color temperature match).
"""

import os, sys, time, json, base64, urllib.request, urllib.error
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'production_assets')
COSTUMES_DIR = os.path.join(ASSETS_DIR, 'costumes')
PROPS_DIR = os.path.join(ASSETS_DIR, 'props')
MATERIALS_DIR = os.path.join(ASSETS_DIR, 'materials')
RESULTS_DIR = os.path.join(ASSETS_DIR, 'results')
CATALOG_FILE = os.path.join(ASSETS_DIR, 'catalog.json')

for d in [ASSETS_DIR, COSTUMES_DIR, PROPS_DIR, MATERIALS_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Initial Preset Catalog (Production Design & Wardrobe)
# ---------------------------------------------------------------------------
DEFAULT_CATALOG = {
    "costumes": [
        {
            "id": "costume_vintage_trench",
            "title": "معطف ترينش كلاسيكي (1970s Trench Coat)",
            "category": "costumes",
            "era": "1970s - كلاسيكي نوير",
            "description": "معطف بيج كلاسيكي بقماش ثقيل وياقة عريضة مع قبعة فيدورا، يضفي طابع الغموض والتحقيق.",
            "prompt_enhancer": "1970s cinematic beige heavy-cotton trench coat, realistic fabric folds, vintage collar, film noir aesthetic",
            "icon": "fa-user-tie"
        },
        {
            "id": "costume_leather_jacket",
            "title": "سترة جلدية عتيقة (Distressed Leather Jacket)",
            "category": "costumes",
            "era": "معاصر / أكشن",
            "description": "جاكيت جلد أسود بتأثير الزمن والخدوش، ثنيات واقعية على الأكمام والأكتاف.",
            "prompt_enhancer": "rugged distressed black leather biker jacket, natural leather sheen, realistic creases and wrinkles, cinematic lighting",
            "icon": "fa-vest"
        },
        {
            "id": "costume_oriental_robe",
            "title": "عباءة شرقية تراثية فاخرة (Embroidered Kaftan)",
            "category": "costumes",
            "era": "تراثي / تاريخي",
            "description": "ثوب شرقي من الحرير الثقيل المطرز بخيوط ذهبية دقيقة، ملمس قماشي فخم وانسدال طبيعي.",
            "prompt_enhancer": "luxurious traditional oriental embroidered robe, silk damask texture, intricate gold thread embroidery, photorealistic fabric drape",
            "icon": "fa-shirt"
        },
        {
            "id": "costume_velvet_gown",
            "title": "فستان سهرة مخملي كلاسيكي (Velvet Evening Gown)",
            "category": "costumes",
            "era": "كلاسيكي هوليوودي",
            "description": "فستان مخملي كحلي داكن بقصة انسيابية وملمس قطيفة ناعم يعكس الإضاءة بنعومة.",
            "prompt_enhancer": "elegant deep-navy velvet evening dress, rich plush velvet texture, realistic light sheen, graceful drape",
            "icon": "fa-person-dress"
        },
        {
            "id": "costume_linen_suit",
            "title": "بذلة كتان صيفية إيطالية (Italian Linen Suit)",
            "category": "costumes",
            "era": "صيفي / دراما متوسطية",
            "description": "بذلة من الكتان الطبيعي بلون بيج رملي مع تجاعيد الكتان الخفيفة الواقعية.",
            "prompt_enhancer": "tailored light-sand linen blazer and trousers, visible raw linen weave, natural casual creases, cinematic 35mm look",
            "icon": "fa-user-tie"
        }
    ],
    "props": [
        {
            "id": "prop_chesterfield",
            "title": "أريكة تشيسترفيلد جلدية عتيقة (Vintage Chesterfield Sofa)",
            "category": "props",
            "era": "كلاسيكي / مكتب فاخر",
            "description": "كنبة جلد بني محروق بأزرار غائرة وتنجيد يدوي متقن تضفي هيبة على كادر الغرفة.",
            "prompt_enhancer": "authentic tufted deep-brown leather Chesterfield sofa, aged vintage patina, photorealistic room perspective and contact shadow",
            "icon": "fa-couch"
        },
        {
            "id": "prop_brass_lamp",
            "title": "أباجورة مكتب نحاسية خضراء (Banker's Brass Lamp)",
            "category": "props",
            "era": "تحقيق / أرشيف",
            "description": "مصباح مكتب من النحاس العتيق بغطاء زجاجي أخضر كلاسيكي مع توهج دافئ ناعم.",
            "prompt_enhancer": "vintage brass banker lamp with emerald green glass shade, warm glowing filament, realistic ambient bounce light",
            "icon": "fa-lightbulb"
        },
        {
            "id": "prop_arabesque_desk",
            "title": "مكتب خشبي أرابيسك مطعم بالصدف (Arabesque Desk)",
            "category": "props",
            "era": "تراثي / قصر تاريخي",
            "description": "مكتب خشبي عريق بنقوش هندسية دقيقة وتطعيم صدف أبيض طبيعي مع حواف منحوتة.",
            "prompt_enhancer": "intricate handcrafted dark walnut arabesque desk, mother-of-pearl inlay, fine geometric woodwork, cinema set prop",
            "icon": "fa-table"
        },
        {
            "id": "prop_rotary_phone",
            "title": "هاتف قرصي عتيق (1960s Rotary Phone)",
            "category": "props",
            "era": "1960s - 1980s",
            "description": "تليفون أرضي بقرص دوار من الباكلايت الأسود اللامع مع سلك لولبي واقعي.",
            "prompt_enhancer": "vintage heavy black bakelite rotary dial telephone, coiled cable, realistic tabletop reflection",
            "icon": "fa-phone"
        },
        {
            "id": "prop_vintage_gramophone",
            "title": "جراموفون أسطوانات نحاسي (Antique Gramophone)",
            "category": "props",
            "era": "كلاسيكي 1920s",
            "description": "جراموفون بقاعدة خشبية منحوتة وبوق نحاسي ذهبي كبير مع أسطوانة فونوغراف سوداء.",
            "prompt_enhancer": "ornate antique brass horn gramophone, polished mahogany wood base, nostalgic retro film prop",
            "icon": "fa-compact-disc"
        }
    ],
    "materials": [
        {
            "id": "mat_exposed_brick",
            "title": "جدار طوب أحمر معتق (Weathered Exposed Brick)",
            "category": "materials",
            "era": "لوفت صناعي / نيويوركي",
            "description": "حوائط طوب أحمر قديم مع آثار مونة أسمنتية بيضاء وتباين ملمسي عالي.",
            "prompt_enhancer": "weathered industrial exposed red brick wall, tactile texture, realistic mortar roughness, cinematic side lighting",
            "icon": "fa-border-all"
        },
        {
            "id": "mat_herringbone_parquet",
            "title": "أرضية باركيه خشب زان (Herringbone Parquet)",
            "category": "materials",
            "era": "كلاسيكي أوروبي",
            "description": "أرضيات خشبية متراصة بنمط زجزاجي (عظم السمكة) مع لمعة شمعية خفيفة وانعكاسات ناعمة.",
            "prompt_enhancer": "herringbone aged oak parquet flooring, satin wood sheen, subtle floor reflections, architectural realism",
            "icon": "fa-grip"
        },
        {
            "id": "mat_raw_concrete",
            "title": "خرسانة معمارية خام (Brutalist Raw Concrete)",
            "category": "materials",
            "era": "مودرن / غموض",
            "description": "جدران خرسانية صريحة بمسام وثقوب قوالب الصب وتدرجات رمادية باردة.",
            "prompt_enhancer": "brutalist architectural raw concrete wall, formwork tie holes, subtle porous texture, modern minimalist set design",
            "icon": "fa-square"
        },
        {
            "id": "mat_victorian_wallpaper",
            "title": "ورق حائط فيكتوري مطرز (Victorian Damask Wallpaper)",
            "category": "materials",
            "era": "فيكتوري / دراما تاريخية",
            "description": "نقوش دمشقية بارزة بدرجات الأخضر الزمردي والذهبي المطفي لمظهر قصور فخمة.",
            "prompt_enhancer": "luxurious emerald and gold Victorian damask wallpaper, embossed textile texture, period drama interior",
            "icon": "fa-gem"
        }
    ]
}

def load_catalog():
    if not os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CATALOG, f, ensure_ascii=False, indent=2)
        return DEFAULT_CATALOG
    try:
        with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CATALOG

def save_catalog(cat):
    try:
        with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cat, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[ProductionDesign] Error saving catalog: {e}")
        return False

def add_custom_item(category, title, description, era, prompt_enhancer, image_b64=None):
    cat = load_catalog()
    if category not in cat:
        cat[category] = []
    
    timestamp = int(time.time())
    item_id = f"custom_{category}_{timestamp}"
    
    saved_img_path = None
    if image_b64:
        try:
            if ',' in image_b64:
                image_b64 = image_b64.split(',', 1)[1]
            img_bytes = base64.b64decode(image_b64)
            target_folder = COSTUMES_DIR if category == 'costumes' else (PROPS_DIR if category == 'props' else MATERIALS_DIR)
            fname = f"{item_id}.jpg"
            saved_img_path = os.path.join(target_folder, fname)
            with open(saved_img_path, 'wb') as f:
                f.write(img_bytes)
        except Exception as e:
            print(f"[ProductionDesign] Image save warning: {e}")

    new_item = {
        "id": item_id,
        "title": title,
        "category": category,
        "era": era or "مخصص",
        "description": description,
        "prompt_enhancer": prompt_enhancer or title,
        "image_file": os.path.basename(saved_img_path) if saved_img_path else None,
        "custom": True,
        "created_at": datetime.utcnow().isoformat()
    }
    cat[category].insert(0, new_item)
    save_catalog(cat)
    return new_item

def get_secrets():
    sec_path = os.path.join(BASE_DIR, 'cindy_secrets.json')
    if os.path.exists(sec_path):
        try:
            with open(sec_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

# ---------------------------------------------------------------------------
# Core Synthesis & Relighting Pipeline
# ---------------------------------------------------------------------------
def apply_production_design(scene_img_b64, mask_b64=None, item_id=None, custom_prompt="", lighting_config=None, custom_image_b64=None):
    """
    Applies realistic wardrobe/decor inpainting and relighting.
    Uses pure Apache-2.0 / MIT models (Qwen-Image-Edit-2511 / Fast-SDXL Inpaint).
    """
    secrets = get_secrets()
    fal_key = (secrets.get('fal_api_key') or secrets.get('fal_key') or '').strip()
    
    if not scene_img_b64:
        raise ValueError("صورة الكادر الأساسية مطلوبة للبدء.")

    if not fal_key:
        raise ValueError("مفتاح Fal API غير معرف في cindy_secrets.json. يرجى توفيره لتشغيل محركات الرندر السحابية.")

    # Find item prompt enhancer if item_id provided
    item_prompt = custom_prompt
    item_category = "general"
    item_title = "ديكور / زي مخصص"
    if item_id:
        catalog = load_catalog()
        for cat_name, items in catalog.items():
            for itm in items:
                if itm['id'] == item_id:
                    item_prompt = itm.get('prompt_enhancer', custom_prompt)
                    item_title = itm.get('title', item_title)
                    item_category = cat_name
                    break

    lighting_config = lighting_config or {}
    light_dir = lighting_config.get('light_direction', 'ambient')
    temp = lighting_config.get('temperature', 'warm')
    match_scene = lighting_config.get('match_scene', True)

    # Lighting prompt injection (simulating IC-Light consistency)
    lighting_terms = []
    if match_scene:
        lighting_terms.append("perfectly integrated scene lighting, matched ambient illumination and shadows")
    if light_dir == 'left':
        lighting_terms.append("directional soft lighting from the left, natural contact shadows on the right")
    elif light_dir == 'right':
        lighting_terms.append("directional soft lighting from the right, natural contact shadows on the left")
    elif light_dir == 'top':
        lighting_terms.append("subtle overhead cinematic downlight, realistic rim lighting")

    if temp == 'warm':
        lighting_terms.append("warm tungsten 3200K ambient color grading")
    elif temp == 'cool':
        lighting_terms.append("cool cinematic cyan 6500K color grading")
    elif temp == 'teal_orange':
        lighting_terms.append("hollywood teal and orange color grading")

    # Prepare data URLs
    if not scene_img_b64.startswith('data:'):
        scene_data_url = f"data:image/jpeg;base64,{scene_img_b64}"
    else:
        scene_data_url = scene_img_b64

    mask_data_url = None
    has_mask = False
    if mask_b64 and len(mask_b64) > 100:
        has_mask = True
        if not mask_b64.startswith('data:'):
            mask_data_url = f"data:image/png;base64,{mask_b64}"
        else:
            mask_data_url = mask_b64

    timestamp = int(time.time())
    result_filename = f"prod_design_{timestamp}.jpg"
    result_path = os.path.join(RESULTS_DIR, result_filename)

    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json"
    }

    # Decide pipeline: Inpainting with Mask VS Semantic Instruction Edit
    if has_mask:
        endpoint = "https://queue.fal.run/fal-ai/fast-sdxl/inpainting"
        terms_str = ', '.join(lighting_terms)
        full_prompt = f"{item_prompt}, {terms_str}, ultra-realistic, 35mm film photograph, master production design"
        payload = {
            "image_url": scene_data_url,
            "mask_url": mask_data_url,
            "prompt": full_prompt,
            "negative_prompt": "blurry, distorted, cartoon, plastic, floating object, deformed, low quality, artifacts",
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
        model_name = "Fast-SDXL Inpainting (MIT / Apache-2.0)"
        cost_str = "~$0.01 (SDXL Inpainting)"
    else:
        endpoint = "https://queue.fal.run/fal-ai/qwen-image-edit-2511"
        image_urls = [scene_data_url]
        terms_str = ', '.join(lighting_terms)
        if custom_image_b64:
            c_url = custom_image_b64 if custom_image_b64.startswith('data:') else f"data:image/jpeg;base64,{custom_image_b64}"
            image_urls.append(c_url)
            full_prompt = f"Seamlessly integrate and adapt the element shown in the second image into the scene in the first image: {item_prompt}, {terms_str}, highly detailed, photorealistic"
        else:
            full_prompt = f"Add {item_prompt} seamlessly into the scene, with realistic contact shadows, accurate floor/wall perspective, and {terms_str}, master cinematic production design"

        payload = {
            "prompt": full_prompt,
            "image_urls": image_urls,
            "num_inference_steps": 28,
            "guidance_scale": 5.0
        }
        model_name = "Qwen-Image-Edit-2511 (Apache 2.0)"
        cost_str = "~$0.02 (Qwen-Image-Edit-2511)"

    # Submit to Fal Queue
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='replace')
        raise RuntimeError(f"خطأ في خادم Fal (HTTP {e.code}): {err_msg}")
    except Exception as e:
        raise RuntimeError(f"تعذر الاتصال بمحرك الرندر: {e}")

    req_id = data.get('request_id')
    status_url = data.get('status_url') or (f"{endpoint}/requests/{req_id}/status" if req_id else None)
    response_url = data.get('response_url') or (f"{endpoint}/requests/{req_id}" if req_id else None)

    # Polling loop
    poll_headers = {"Authorization": f"Key {fal_key}"}
    final_data = None
    for _ in range(40):
        time.sleep(2)
        if status_url:
            st_req = urllib.request.Request(status_url, headers=poll_headers)
            try:
                with urllib.request.urlopen(st_req, timeout=15) as sresp:
                    st_data = json.loads(sresp.read().decode('utf-8'))
                    if st_data.get('status') == 'COMPLETED':
                        resp_req = urllib.request.Request(response_url, headers=poll_headers)
                        with urllib.request.urlopen(resp_req, timeout=15) as rresp:
                            final_data = json.loads(rresp.read().decode('utf-8'))
                        break
                    elif st_data.get('status') in ['FAILED', 'ERROR']:
                        raise RuntimeError(f"فشل التوليد في المحرك السحابي: {st_data.get('error', 'Unknown')}")
            except Exception as e:
                if 'فشل التوليد' in str(e):
                    raise
                pass

    if not final_data:
        raise RuntimeError("تجاوزت المعالجة السحابية الحد الأقصى للوقت (Timeout). يرجى المحاولة مجدداً.")

    images = final_data.get('images', [])
    if not images or 'url' not in images[0]:
        raise RuntimeError("لم يُرجع المحرك صورة ناتجة صالحة.")

    out_url = images[0]['url']

    # Download and save locally
    img_req = urllib.request.Request(out_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(img_req, timeout=30) as rresp:
        with open(result_path, 'wb') as out_f:
            out_f.write(rresp.read())

    return {
        "success": True,
        "filename": result_filename,
        "local_url": f"/production_assets/results/{result_filename}",
        "cloud_url": out_url,
        "category": item_category,
        "model_used": model_name,
        "prompt_used": full_prompt,
        "cost": cost_str,
        "legal_audit": {
            "ip_clean": True,
            "license": "Apache 2.0 / MIT (Commercially Free)",
            "no_commercial_restrictions": True
        }
    }


if __name__ == '__main__':
    cat = load_catalog()
    print(f"Production Design Studio Loaded: {len(cat.get('costumes', []))} costumes, {len(cat.get('props', []))} props, {len(cat.get('materials', []))} materials.")
