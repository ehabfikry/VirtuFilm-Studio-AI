# -*- coding: utf-8 -*-
import json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

memory_data = {
    "version": "1.0.0",
    "bot_name": "Cindy (سيندي)",
    "title": "مستشارة ومخرجة الذكاء الاصطناعي السينمائي والتوليد التنفيذي",
    "persona": {
        "languages": ["Arabic", "English"],
        "voice_enabled": True,
        "tone": "سينمائية، احترافية، مبدعة، ملهمة، وسريعة التنفيذ",
        "system_instruction": "تتحدث سيندي باللغة التي يبدأ بها المستخدم (عربي أو إنجليزي). تقدم حلولاً إخراجية وبرومبتات دقيقة متوافقة مع كل أداة ذكاء اصطناعي، وتنفذ أوامر التجهيز والمعالجة السينمائية بناءً على الصلاحية الممنوحة."
    },
    "permissions": {
        "current_level": "supervised", # "advisor", "supervised", "autonomous"
        "available_levels": {
            "advisor": "استشارة وتخطيط فقط (توليد برومبتس وخطط لقطات دون تشغيل برامج)",
            "supervised": "تنفيذ بإذن مسبق (عرض الأوامر وسكريبتات FFmpeg والـ APIs وطلب الموافقة قبل التشغيل)",
            "autonomous": "تنفيذ فوري مباشر (تشغيل التحويلات والمعالجة تلقائياً)"
        }
    },
    "user_preferences": {
        "default_aspect_ratio": "16:9",
        "default_fps": "24fps (Cinematic)",
        "preferred_aesthetic": "35mm anamorphic cinematic film, natural volumetric lighting, high dynamic range",
        "global_negative_prompts": "cgi, 3d render, cartoon, plastic skin, distorted face, extra limbs, bad anatomy, overexposed, low quality, glitchy movement, flickering, jittery, amateur video, oversaturated, text watermarks",
        "favorite_models": ["Kling AI 1.5", "Runway Gen-3 Alpha", "Minimax Hailuo", "Wan 2.1"]
    },
    "learned_rules": [
        {
            "id": "LR-001",
            "category": "Kling AI",
            "rule": "في Kling AI، تجنب استخدام أكثر من حركتي كاميرا متعارضتين في نفس البرومبت، وركز على وصف حركة العنصر الرئيسي أولاً ثم اتجاه حركة الكاميرا بنعومة (Smooth slow pan / gentle dolly in).",
            "date_added": "2026-10-28",
            "source": "Cinematic Prompt Vault"
        },
        {
            "id": "LR-002",
            "category": "Runway Gen-3",
            "rule": "Runway Gen-3 يستجيب بدقة مذهلة للوسوم المنظمة في بداية البرومبت: [Camera]: ..., [Lighting]: ..., [Movement]: ... يليه الوصف الحركي.",
            "date_added": "2026-10-28",
            "source": "Runway Director Guide"
        },
        {
            "id": "LR-003",
            "category": "Minimax Hailuo",
            "rule": "Minimax يتفوق في التعبير البشري والفيزياء الواقعية؛ اكتب وصف المشاعر الدقيقة للوجه وتفاصيل الملابس العضوية دون الحاجة لحشو كلمات جودة مثل 8k و photorealistic.",
            "date_added": "2026-10-29",
            "source": "MiniMax Official Research"
        },
        {
            "id": "LR-004",
            "category": "Wan 2.1 / Wan 2.2",
            "rule": "لنماذج Wan، استخدم توصيفاً خطياً متتابعاً للحدث (First..., then..., while camera moves...) لضمان ثبات التماسك الفيزيائي بين البداية والنهاية.",
            "date_added": "2026-10-30",
            "source": "Wan Open Source Community"
        },
        {
            "id": "LR-005",
            "category": "Character Consistency",
            "rule": "للحفاظ على ثبات الشخصيات بين اللقطات المتعددة، ثبت 3 عناصر مميزة: الزي المميز ولونه، تسريحة ولون الشعر، وإكسسوار أو علامة فارقة محددة في كل برومبت.",
            "date_added": "2026-10-30",
            "source": "Cinema Pipeline Workflows"
        }
    ],
    "models_knowledge": {
        "Kling AI": {
            "strengths": "الفيزياء الواقعية، الحركات البشرية الكبيرة، محاكاة السوائل والنار، الـ Motion Brush وتحديد إطارات البداية والنهاية.",
            "best_format": "وصف المشهد الرئيسي + تفاصيل الإضاءة والعدسة + حركة الشخصية + حركة الكاميرا المفردة + أسلوب التلوين.",
            "tips": "استخدم Negative Prompts دائماً لمنع التشوه الحركي، وتجنب الحركات المفاجئة السريعة للكاميرا.",
            "ideal_aspect_ratios": ["16:9", "9:16", "1:1"]
        },
        "Runway Gen-3 Alpha / Turbo": {
            "strengths": "التكوين السينمائي الفائق، إضاءة هوليوود، التحكم المتقدم في الكاميرا (Dolly, Pan, Zoom, Tilt, Roll)، ودقة التفاصيل البصرية.",
            "best_format": "وسوم هيكلية: [Camera movement] [Lighting setup] [Subject & Action] [Atmosphere & Color palette] [Shot speed].",
            "tips": "تجنب الأوصاف الغامضة، واستخدم أسماء العدسات الحقيقية مثل 35mm أو 85mm anamorphic.",
            "ideal_aspect_ratios": ["16:9", "9:16"]
        },
        "Luma Dream Machine": {
            "strengths": "الانتقالات الحركية السلسة، حركة الكاميرا الديناميكية في المشاهد المفتوحة، وميزة تمديد اللقطات (Extend) وتكرارها (Loop).",
            "best_format": "وصف سينمائي تدفقي طبيعي يركز على اتجاه الحركة والسرعة في أول 3 ثوانٍ.",
            "tips": "ممتاز في تحويل الصور الثابتة إلى فيديو، خاصة عند تحديد نقطة البداية ونقطة النهاية.",
            "ideal_aspect_ratios": ["16:9", "9:16", "4:3", "21:9"]
        },
        "Minimax Hailuo AI": {
            "strengths": "أعلى واقعية في حركة الوجوه، لغة الجسد الطبيعية، تعابير العيون، والمشاهد الدرامية ذات الحوارات.",
            "best_format": "قصة مشهد سردية تركز على ما يفعله ويشعر به البطل، مع زاوية الكاميرا المحيطة به.",
            "tips": "لا تضع أوامر مكررة للجودة العالية؛ ركز على سرد تفاصيل التفاعل الحسي في المشهد.",
            "ideal_aspect_ratios": ["16:9", "9:16"]
        },
        "OpenAI Sora / Veo 3": {
            "strengths": "فهم عميق للفيزياء الحقيقية للضوء والظل، ديمومة المشهد لفترات أطول، وعلاقة العناصر المتعددة في المشهد.",
            "best_format": "نص سردي متكامل وغني بالمعاني السينمائية والتفاصيل الجغرافية والحركية الدقيقة.",
            "tips": "حدد بدقة موقع الشخصية بالنسبة لمحيطها، وكيف تتفاعل مع البيئة (رياح، مطر، حركة أقدام).",
            "ideal_aspect_ratios": ["16:9", "9:16"]
        },
        "Wan 2.1 / Wan 2.2": {
            "strengths": "نموذج مفتوح المصدر عالي القدرة، استجابة عالية للبرومبتات التوجيهية، وتوليد حركات معقدة.",
            "best_format": "برومبت منظم يصف موضوع اللقطة أولاً، البيئة، حركة الكاميرا، ودرجة الإضاءة بدقة.",
            "tips": "تأكد من ضبط الـ CFG scale بين 5 إلى 7 لتفادي تشوه الحركة.",
            "ideal_aspect_ratios": ["16:9", "9:16", "1:1"]
        },
        "Midjourney / FLUX (Keyframing)": {
            "strengths": "توليد الإطار الافتتاحي (First Frame) بأعلى دقة فنية ليكون مرجعاً (Image-to-Video).",
            "best_format": "Shot type + Subject + Lighting + Camera lens + Film grain / color grading + --ar 16:9 --v 6.1 / flux.",
            "tips": "ابدأ دائماً بصورة مفتاحية عالية الجودة لتضمن تحكماً فائقاً في فيديو الـ AI اللاحق.",
            "ideal_aspect_ratios": ["16:9", "21:9", "9:16"]
        }
    },
    "camera_lexicon": {
        "Dolly In / Push In": "تقريب الكاميرا جسدياً نحو العنصر لزيادة التوتر والتركيز الدرامي الحميم.",
        "Dolly Out / Pull Back": "ابتعاد الكاميرا جسدياً لكشف البيئة المحيطة أو إظهار العزلة والحجم.",
        "Truck Left / Right": "حركة الكاميرا جانبياً بالتوازي مع العنصر لتتبع مساره بحيوية.",
        "Pan (Left / Right)": "تدوير رأس الكاميرا أفقياً دون تحريك قاعدتها لمسح الأفق أو متابعة شخص.",
        "Tilt (Up / Down)": "تدوير رأس الكاميرا عمودياً للأعلى (لإظهار الهيبة) أو للأسفل (لإظهار الضعف).",
        "Crane / Jib Shot": "حركة عمودية شاهقة تمنح رؤية بانورامية ملحمية للموقع.",
        "Orbit / Arc 360": "دوران الكاميرا الدائري حول العنصر لإبراز لحظة ملحمية أو صدمة درامية.",
        "FPV Drone Fly-Through": "طيران حر فائق السرعة عبر الممرات والزوايا الضيقة يثير الأدرينالين.",
        "Whip Pan": "حركة التفاف سريعة ومموهة تضفي طاقة حركية عالية أو انتقالاً سينمائياً بين لقطتين."
    },
    "lighting_lexicon": {
        "Chiaroscuro": "تضاد درامي عنيف بين النور الساطع والظلال العميقة (أسلوب أفلام النوار والغموض).",
        "Volumetric God Rays": "أشعة ضوء ملموسة تخترق الغبار أو الضباب تضفي روحانية وعمقاً ملحمياً.",
        "Golden Hour": "ضوء شمس الغروب الدافئ الناعم المائل إلى الذهبي والبرتقالي السينمائي.",
        "Cyberpunk Neon Rim": "إضاءة حواف ساطعة بألوان النيون (سيان وماجنتا) مع انعكاسات مائية رطبة.",
        "Rembrandt Lighting": "إضاءة كلاسيكية ترسم مثلث ضوء على خد الشخصية في الجانب المظلل.",
        "Moody Low-Key": "سيادة الظلال الداكنة والغموض مع نقاط ضوء خافتة مدروسة."
    }
}

target_file = r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_memory.json'
with open(target_file, 'w', encoding='utf-8') as f:
    json.dump(memory_data, f, ensure_ascii=False, indent=2)

print(f"Generated cindy_memory.json successfully at {target_file}")
