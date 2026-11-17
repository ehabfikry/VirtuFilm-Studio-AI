# المرجع التقني الشامل لأدوات الإنتاج السينمائي بالذكاء الاصطناعي (Master Tool Dossier)
## المخرج: إيهاب فكري | استوديو: Cindy-AI-Director

> هذا المرجع تم إعداده بعد دراسة فاحصة للأكواد المصدرية، الأوراق البحثية، الأوزان، المتطلبات البرمجية واستهلاك الذاكرة (VRAM) لكل أداة على حدة، لتكون كل أداة جاهزة للتنفيذ المباشر دون أي تجريب أو إهدار.

---

### 1. `Vchitect/SEINE` (ICLR 2024) — محرك النقلة العمرية والـ Match-Cut التوليدي
- **المستودع الرسمي**: `https://github.com/Vchitect/SEINE`
- **البنية الهندسية**: 3D UNet مبني فوق Stable Diffusion v1-4 (VAE + CLIP Text Encoder) مع طبقات انتباه زماني (Temporal Attention).
- **الأوزان**: `seine.pt` (3.6 GB) من HuggingFace (`Vchitect/SEINE`).
- **المكتبات الحاكمة**: `tensorboard==2.15.1`, `diffusers==0.15.0`, `transformers==4.29.2`, `decord==0.6.0`, `rotary-embedding-torch==0.3.5`, `timm==0.9.10`, `omegaconf`.
- **مواصفات التشغيل**:
  - الذاكرة المطلوبة: 12GB - 16GB VRAM (FP16).
  - الكارت الأمثل: RTX 3090 / A5000 / A6000.
  - زمن الريندر: ~45 ثانية لـ 250 خطوة DDPM (16 فريم بدقة 512x512).
- **التوظيف في الفيلم**: الانتقال التوليدي المتصل بين كادر "عبد العزيز الشاب" (جينز + آفرو + ضحكة) إلى "عبد العزيز العجوز" (ترتر + فرو + كافيه).
- **ملف التنفيذ الجاهز**: `C:\Users\DELL\Desktop\Cindy-AI-Director\run_seine_pod.py`

---

### 2. `bytedance/DreamID-V` (Faster Engine) — محرك تثبيت الهوية وتبديل الوجوه السينمائي
- **المستودع الرسمي**: `https://github.com/bytedance/DreamID-V`
- **البنية الهندسية**: Diffusion Transformer (DiT) متكامل مع العمود الفقري لنموذج `Wan2.1-T2V-1.3B` + أوزان `dreamidv_faster.pth`.
- **الأوزان**:
  - `Wan-AI/Wan2.1-T2V-1.3B` (حوالي 3.8 GB)
  - `bytedance/DreamID-V/dreamidv_faster.pth` (حوالي 1.2 GB)
- **المكتبات الحاكمة**: `diffusers`, `transformers`, `decord`, `insightface`, `onnxruntime`, `einops`.
- **مواصفات التشغيل**:
  - الدقة: 832x480 (81 فريم @ 24fps).
  - الذاكرة المطلوبة: 16GB - 20GB VRAM.
  - الكارت الأمثل: RTX 3090 / A5000 / RTX 4090.
  - زمن الريندر: ~90 ثانية لـ 16 خطوة أخذ عينات.
- **التوظيف في الفيلم**: حقن ملامح عبد العزيز المعتمدة على الممثل الحقيقي في لقطة دفع الثور الواقعية 4K (`Slow_push_on_struggling_bull_4K_20261025200900.mp4`).
- **الأصل المجهز**: تم تقطيع 81 فريم بدقة 832x480 ورفعها على CDN: `https://v3b.fal.media/files/b/0ab28930/qVuvetaIUn_MhuQ6MGI1Y_driving_bull_832x480.mp4`
- **ملف التنفيذ الجاهز**: `C:\Users\DELL\Desktop\Cindy-AI-Director\run_dreamidv_bull_pod.py`

---

### 3. `Doubiiu/MotionCanvas` (SIGGRAPH 2025) — مصمم اللقطات وحركات الكاميرا 3D
- **المستودع الرسمي**: `https://github.com/Doubiiu/MotionCanvas`
- **الجهة البحثية**: CUHK & Adobe Research.
- **البنية الهندسية**: نموذج ممتد من `Wan2.1-Fun-1.3B-InP` مدمج مع `DiffSynth-Studio`، يتحكم في حركة الكاميرا وحركة العناصر في الفراغ ثلاثي الأبعاد دون الحاجة لبيانات 3D ضخمة.
- **المخرجات**: حتى 49 فريم بدقة 832x480 بحركة كاميرا حرة (Orbit, Pan, Zoom, Drone descent).
- **الذاكرة المطلوبة**: 16GB - 24GB VRAM.
- **التوظيف في الفيلم**: توليد حركة كاميرا الدرون التي تهبط وتدور 360 درجة حول عبد العزيز وعبشكور وهما يتعانقان، انطلاقاً من صورة ثابتة 2K بدون تشوه بيئي.

---

### 4. `time-to-move/TTM` (ICLR 2026) — جسر تحويل بلندر إلى فيديو واقعي (Blender-to-Real)
- **المستودع الرسمي**: `https://github.com/time-to-move/TTM`
- **البنية الهندسية**: تقنية *Dual-Clock Denoising* (بدون تدريب إضافي Training-Free).
  - تقوم بتطبيق تشويش منخفض داخل المناطق الموجهة بمسار مسبق (كتصدير بلندر) وتشويش عالي في باقي الكادر ليتحول الكروكي إلى تفاصيل واقعية سينمائية كاملة.
- **النماذج المدعومة كعمود فقري**: `Wan 2.2`، `CogVideoX`، `Stable Video Diffusion`.
- **الميزة الحاكمة**: خفيف جداً ولا يحتاج أوزان مخصصة؛ يعمل كـ Plug-and-Play Sampling Strategy.
- **التوظيف في الفيلم**: أخذ ريندر الـ Previs الكروكي من بلندر وتحويله إلى ممثلين حقيقيين وأقمشة وإضاءة واقعية.

---

### 5. `HiDream-ai/MotionPro` (CVPR 2025) — متحكم المسارات المستقل (الكاميرا vs الشخصيات)
- **المستودع الرسمي**: `https://github.com/HiDream-ai/MotionPro`
- **البنية الهندسية**: مبني فوق Stable Video Diffusion (SVD) مع تقنية Region-wise Trajectories.
- **الميزة الحاكمة**: يفصل تماماً بين مسار حركة الكاميرا ومسار حركة الأجسام (Brush & Drag). يمنع تداخل خلفية المشهد مع أجساد الممثلين أثناء الحركات السريعة.
- **الذاكرة المطلوبة**: 18GB - 24GB VRAM.

---

### 6. `DINGYANB/MTVCrafter` (ICLR 2026) — محرك الأقمشة المعقدة وحركة 4D
- **المستودع الرسمي**: `https://github.com/DINGYANB/MTVCrafter`
- **البنية الهندسية**: 4D Motion Tokenizer (4DMoT) مع Motion-aware Video DiT (MV-DiT).
- **الميزة الحاكمة**: يتخلى تماماً عن هياكل الـ 2D Skeleton القديمة التي تسبب تشوه الملابس، ويستخدم رموز حركة 4D فراغية مباشرة، مما يجعله المحرك الأقوى للأقمشة الفضفاضة (جاكت عبشكور، بنطلون الشارلستون، وياقة الفرو لعبد العزيز).
- **العمود الفقري**: متاح بنسختي `CogVideoX-5B` و `Wan-2.1-14B`.

---

### 7. `taco-group/PISCO` (NeurIPS 2025) — محرك زرع الممثلين داخل الفيديوهات الحقيقية
- **المستودع الرسمي**: `https://github.com/taco-group/PISCO`
- **الجهة البحثية**: Texas A&M + Stanford + KAIST.
- **البنية الهندسية**: انتشار موجه بمفاتيح كادرية متفرقة (Sparse Keyframe Control) مع أدوات تقسيم ذكية (SAM3) وعمق مكاني (Depth-Anything).
- **التوظيف في الفيلم**: إمكانية تصوير كافيه أو شارع حقيقي في القاهرة بكاميرا المخرج، ثم زرع شخصيتي عبد العزيز وعبشكور داخل الفيديو بظلال وتفاعل فيزيائي طبيعي مع الطاولات والمارة.

---

### 8. `Zhen-Dong/Magic-Me` (CVPR 2024) — قفل البصمة البيومترية للممثل (Identity Lock)
- **المستودع الرسمي**: `https://github.com/Zhen-Dong/Magic-Me`
- **البنية الهندسية**: تخصيص انتشار الفيديو عبر Subject ID Tokens مع 3D Gaussian Noise Prior.
- **التوظيف في الفيلم**: تثبيت البصمة الشكلية لشخصيات الفيلم عبر جميع المشاهد واللقطات المتتابعة، بحيث لا تختلف ملامح الوجه أو تضيع تفاصيل الممثلين بين لقطة وأخرى.

---

### 9. `AlayaLab/AlayaRenderer` — محرك الرندرة العصبية للبيئات العميقة
- **المستودع الرسمي**: `https://github.com/AlayaLab/AlayaRenderer`
- **البنية الهندسية**: Generative World Renderer يعتمد على ممرات G-Buffer (Depth, Normals, Albedo, Roughness) لتحويل بيئات الثري دي إلى ريندر سينمائي فوتوريلستيك فوري.

---

### 10. `IGLICT/SketchVideo` — محرك تحويل الاسكتش إلى فيديو سينمائي
- **المستودع الرسمي**: `https://github.com/IGLICT/SketchVideo`
- **البنية الهندسية**: DiT مدعوم بـ Sketch Control Blocks و Inter-Frame Attention لنقل خطوط الستوريبورد المرسومة باليد إلى لقطات متحركة حية.
