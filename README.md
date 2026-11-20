# 🎬 VirtuFilm AI Studio

**An End-to-End Local AI Filmmaking & Post-Production Desktop Suite (BYOK — Bring Your Own Key).**

Direct scenes with an AI Director (**Cindy**) featuring **Character Lock**, generate storyboards & cinema shots with top video models, train commercially licensed actor LoRAs, and finish in 4K with dedicated Post-Production — all running locally on your machine with **zero monthly SaaS lock-in**.

![Platform](https://img.shields.io/badge/Platform-Windows%20Desktop-0078D6?style=flat-square)
![Python](https://img.shields.io/badge/Backend-Python%203.10+-3776AB?style=flat-square)
![Mode](https://img.shields.io/badge/Pricing-BYOK%20(Bring%20Your%20Own%20Key)-10B981?style=flat-square)

---

## ✨ Two Focused Desktop Apps, One Shared Studio

VirtuFilm AI splits your workflow cleanly into two standalone desktop apps (Chrome/Edge App Mode) sharing the same local backend (`http://127.0.0.1:8765`) and `outputs/` media library:

| App | Purpose | Highlights |
| :--- | :--- | :--- |
| **🎥 VirtuFilm AI Production** (`/`) | Pre-production, Direction & Generation | • **1. Direction (`الإخراج`)**: Chat with Cindy AI Director + **Character Lock Protocol** to keep actor appearance consistent across shots.<br>• **2. Script & Storyboard (`السيناريو`)**: Shot cards, camera blocking, and overhead diagrams.<br>• **3. Commercial LoRA (`LoRA`)**: Train & test character/style LoRAs via **Fal.ai Fast API** (commercially licensed).<br>• **4. Generation (`التوليد`)**: Free vs. Paid wing switcher (`Kling 4.0 Pro Omni`, `Kling 3.0 Pro`, `Seedance 2.5`, `MiniMax H3`, `Luma Ray 2`, `Runway Gen-3`) with Image/Video/Audio reference attachments. |
| **✂️ VirtuFilm AI Post-Production** (`/post`) | Finishing, Audio & Final Assembly | • **4K Upscaling**: Local FFmpeg or AI upscaling (`SeedVR2`).<br>• **Smart Auto-Reframe**: Convert between `16:9`, `9:16`, `1:1`, `4:5`, `21:9`.<br>• **Audio Studio**: FFmpeg audio muxing/mixing + free TTS & Foley links.<br>• **Final Film Assembly**: Multi-clip timeline merge + one-click external NLE launch. |

---

## 🚀 Quickstart (2-Minute Core Setup)

The **Core Studio** only needs Python 3.10+, FFmpeg, and your own API keys (`Gemini` + `Fal.ai`):

```bash
# 1. Clone the repository
git clone https://github.com/ehabfikry/VirtuFilm-Studio-AI.git
cd VirtuFilm-Studio-AI

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Launch silently (Windows)
wscript.exe launch_cindy_silent.vbs
```

Or run the server directly:
```bash
python cindy_server.py
```
Then open:
- **Production App:** `http://127.0.0.1:8765`
- **Post-Production App:** `http://127.0.0.1:8765/post`

Open the **Vault (`الخزنة`)** inside the app to add your `Gemini` and `Fal.ai` API keys.

---

## 🧩 Optional Power Add-ons (Pro / Advanced Modules)

The Core Studio works completely standalone. When you're ready to expand into 3D blocking or open-weight GPU rendering, you can optionally enable these modular add-ons:

1. **🧊 Blender 3D Pre-vis Add-on (`cindy_blender_bridge.py`)**
   - Automatically builds 3D blocking scenes, camera motion paths, depth maps, and overhead diagrams in Blender to guide AI video generation.
2. **🟢 Modal Serverless L40S Pack (`cindy_modal_freefield.py`)**
   - Connects to your Modal account for on-demand L40S GPU workflows: `LTX-2.5`, `MiniMax H3`, `Wan 2.2 Camera`, `SeedVR2 4K Upscale`, `Recast`, `Relight`, and `Speak`.
3. **⚡ ComfyUI Local & RunPod Cloud Studio**
   - Connect a local ComfyUI instance or spin up/terminate on-demand RunPod GPU pods with built-in emergency stop & auto-stop balance protection.

---

## 🇪🇬 نظرة سريعة بالعربية

**VirtuFilm AI Studio** هو استوديو إنتاج سينمائي ومونتاج متكامل يعمل محلياً على جهازك بنظام **BYOK (استخدم مفاتيح API الخاصة بك بدون اشتراكات شهرية)**.

- **تطبيق الإنتاج (`VirtuFilm AI Production`):**
  - مخرجة ذكاء اصطناعي (**سيندي**) تدعم **تثبيت ملامح الشخصية (Character Lock)** عبر كل اللقطات.
  - كتابة السيناريو والستوري بورد وتدريب نماذج **LoRA تجارية** عبر `Fal.ai`.
  - توليد الفيديو بأقوى الموديلات العالمية مع دعم إرفاق صور وفيديوهات وصوتيات مرجعية.
- **تطبيق المونتاج (`VirtuFilm AI Post-Production`):**
  - رفع الجودة لـ **4K**، تعديل الأبعاد الذكي (**Auto-Reframe**)، استوديو الصوت، ودمج اللقطات في فيلم نهائي.
- **إضافات اختيارية للمحترفين (Add-ons):** ربط **Blender 3D Pre-vis**، وتشغيل موديلات **Modal L40S**، وربط **ComfyUI / RunPod**.

---

## 🤝 Contributing & Feedback

Issues, feature requests, and PRs are welcome! If you find VirtuFilm AI useful for your filmmaking workflow, consider giving the repo a ⭐ **Star**.
