# Upgrade video duration options and add Fal.ai Models Studio Explorer to tab-screening
with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Expand Video Duration dropdown with cinematic options
old_duration_select = '''            <select id="video-duration-select" class="bg-transparent text-amber-300 font-bold focus:outline-none text-xs">
              <option value="5" selected>5 ثوانٍ</option>
              <option value="10">10 ثوانٍ</option>
              <option value="15">15 ثانية (Commercial)</option>
            </select>'''

new_duration_select = '''            <select id="video-duration-select" class="bg-transparent text-amber-300 font-bold focus:outline-none text-xs">
              <option value="2">2 ثانية (Micro-Cut / Reaction)</option>
              <option value="3">3 ثوانٍ (Cutaway)</option>
              <option value="4">4 ثوانٍ (Standard Beat)</option>
              <option value="5" selected>5 ثوانٍ (Cinematic Standard)</option>
              <option value="6">6 ثوانٍ (MiniMax Fixed)</option>
              <option value="8">8 ثوانٍ (Veo Extended)</option>
              <option value="10">10 ثوانٍ (Long Shot)</option>
              <option value="15">15 ثانية (Commercial Beat)</option>
              <option value="20">20 ثانية (Seedance Master)</option>
              <option value="30">30 ثانية (Seedance Sequence)</option>
            </select>'''

assert old_duration_select in html, "old_duration_select not found"
html = html.replace(old_duration_select, new_duration_select, 1)
print("index.html: video-duration-select updated with full options (2s to 30s).")

# 2. Add Fal.ai Models Explorer Hub inside tab-screening right after the title
old_screening_header = '''          <h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-cloud text-amber-400"></i>
            <span>استوديو أدوات Fal.ai السحابية (25 محرك فيديو و 9 محركات صور مرتبة من الأرخص للأغلى)</span>
          </h2>'''

new_screening_header = '''          <h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-cloud text-amber-400"></i>
            <span>استوديو أدوات Fal.ai السحابية ومحرّك التوليد المباشر</span>
          </h2>

          <!-- QUICK MODEL SELECTOR FOR SCREENING STUDIO -->
          <div class="mt-2 flex flex-wrap items-center gap-2 bg-cinema-900/90 border border-amber-500/30 rounded-xl p-2.5">
            <span class="text-xs font-bold text-amber-300 flex items-center gap-1.5 shrink-0">
              <i class="fa-solid fa-sliders"></i> المحرّك النشط في استوديو Fal.ai:
            </span>
            <select id="screening-fal-model-select" onchange="syncScreeningStudioModel(this.value)" class="flex-1 min-w-[260px] bg-cinema-950 border border-cinema-700 rounded-lg px-2.5 py-1.5 text-xs font-bold text-slate-100 focus:outline-none focus:border-cinema-gold">
              <optgroup label="🎬 موديلات الفيديو وقفل الملامح بالـ LoRA (Fal.ai)">
                <option value="Wan 2.1 (Alibaba 14B)" selected>💎 Alibaba Wan 2.1 — [~$0.03 / 5s] (الأرخص إطلاقاً: $0.006/ث)</option>
                <option value="MiniMax H3 Lite">⚡ MiniMax Hailuo H3 Lite — [~$0.04 / 6s] (اقتصادي سريع)</option>
                <option value="Wan 2.2 Image-to-Video">💎 Alibaba Wan 2.2 I2V — [~$0.04 / 5s] (حركية عالية)</option>
                <option value="LTX-2.3 Distilled Fast LoRA">⚡ LTX-2.3 Distilled LoRA — [~$0.08 / 5s] (درافت سريع بقفل لورا)</option>
                <option value="Tencent HunyuanVideo">🎬 Tencent HunyuanVideo — [~$0.10 / 5s] (ثبات 13B)</option>
                <option value="PixVerse V6 Cinematic">🎥 PixVerse V6 Cinematic — [~$0.18 / 5s] (20 عدسة وتحكم كاميرا)</option>
                <option value="LTX-2.3 22B Cinema LoRA">👑 LTX-2.3 22B Cinema LoRA — [~$0.20 / 5s] (أعلى جودة + LoRA)</option>
                <option value="MiniMax H3 I2V LoRA">🎯 MiniMax H3 I2V LoRA — [~$0.25 / 5s] (قفل ملامح الممثل بالـ LoRA)</option>
                <option value="MiniMax Camera Controls">📐 MiniMax Camera Controls — [~$0.25 / 5s] (تحكم مداري ثلاثي الأبعاد)</option>
                <option value="ByteDance Seedance 2.5">💃 ByteDance Seedance 2.5 — [~$0.18/s - $1.20] (حتى 30 ثانية ومراجع)</option>
                <option value="Kling 1.6 Pro Image-to-Video">👑 Kling 1.6 Pro I2V — [~$0.49 / 5s] (كادر بداية ونهاية)</option>
                <option value="Luma Ray 2 Image-to-Video">🌊 Luma Ray 2 I2V — [~$0.50 / 5s] (كادر بداية ونهاية)</option>
                <option value="Kling Motion Control (1080p)">👑 Kling Motion Control 1080p — [~$0.63 / 5s] (نقل حركة كامل)</option>
                <option value="Topaz Video Upscale">✨ Topaz Video Upscale — [~$0.12 / 5s] (ترقية الفيديو لـ 4K)</option>
                <option value="Sync Lipsync 2.0">👄 Sync Lipsync 2.0 — [~$0.05 / 5s] (مزامنة الشفاه مع الصوت العربي)</option>
                <option value="MuseTalk LipSync">👄 MuseTalk LipSync — [~$0.03 / 5s] (دوبلاج فوري سريع)</option>
              </optgroup>
              <optgroup label="📸 موديلات الصور وتعديل الكوادر (Fal.ai)">
                <option value="fal-ai/flux/schnell">⚡ FLUX.1 Schnell — [$0.003 / كادر] (أسرع درافت)</option>
                <option value="fal-ai/nano-banana">🍌 Google Nano Banana — [$0.005 / كادر]</option>
                <option value="fal-ai/nano-banana-pro">🍌 Google Nano Banana Pro — [$0.015 / كادر] (2K Pro)</option>
                <option value="fal-ai/qwen-image-edit-2511">🪄 Qwen-Image-Edit-2511 — [$0.020 / تعديل]</option>
                <option value="fal-ai/flux/dev">💎 FLUX.1 Dev — [$0.025 / كادر] (دقة سينمائية)</option>
                <option value="blackforestlabs/flux-3/klein/edit-image/lora">⚡ FLUX 3 Klein Edit LoRA — [$0.012 / MP] (تعديل بالـ LoRA)</option>
                <option value="fal-ai/qwen-image-2512/lora">🪄 Qwen Image 2512 LoRA — [$0.035 / MP]</option>
                <option value="fal-ai/flux-pro/v1.1-ultra">📸 FLUX 1.1 Pro Ultra — [$0.060 / كادر] (2K RAW)</option>
              </optgroup>
            </select>
            <span id="screening-model-cost-pill" class="text-[11px] font-mono font-bold text-amber-300 bg-black/40 px-2 py-1 rounded border border-cinema-700">~$0.03 / 5s</span>
          </div>'''

assert old_screening_header in html, "old_screening_header not found"
html = html.replace(old_screening_header, new_screening_header, 1)
print("index.html: Fal.ai Models Selector integrated directly into tab-screening.")

# 3. Add JS helper syncScreeningStudioModel
old_execute_screening = '''    function executeActiveScreeningPrompt() {
      const prompt = document.getElementById('screen-active-prompt')?.value || '';'''

new_execute_screening = '''    function syncScreeningStudioModel(val) {
      const activeVidSelect = document.getElementById('active-video-model');
      const activeImgSelect = document.getElementById('active-image-model');
      const costPill = document.getElementById('screening-model-cost-pill');
      if (costPill) {
        costPill.innerText = MODEL_COST_MAP[val] || 'حسب الاستهلاك السحابي';
      }
      if (val.startsWith('fal-ai/flux') || val.includes('nano-banana') || val.includes('qwen') || val.includes('recraft') || val.includes('ideogram')) {
        setGenerationMode('image');
        if (activeImgSelect) activeImgSelect.value = val;
      } else {
        setGenerationMode('video');
        if (activeVidSelect) activeVidSelect.value = val;
      }
      currentSelectedModel = val;
      showToast(`تم اختيار محرك [${val}] في استوديو Fal.ai! 🎬`, 'info');
    }

    function executeActiveScreeningPrompt() {
      const prompt = document.getElementById('screen-active-prompt')?.value || '';'''

assert old_execute_screening in html, "old_execute_screening not found"
html = html.replace(old_execute_screening, new_execute_screening, 1)
print("index.html: syncScreeningStudioModel added.")

with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html updated successfully!")
