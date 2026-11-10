# Script to cleanly apply both duration options and the Fal.ai Models Studio Hub
with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update video-duration-select
pos_dur = html.find('video-duration-select')
end_dur = html.find('</select>', pos_dur)

new_dur_opts = '''video-duration-select" class="bg-transparent text-amber-300 font-bold focus:outline-none text-xs">
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

html = html[:pos_dur] + new_dur_opts + html[end_dur+9:]
print("Duration select replaced cleanly.")

# 2. Add prominent Fal.ai Tools Explorer Hub right in tab-screening
pos_screen = html.find('tab-screening')
pos_h2 = html.find('<h2', pos_screen)
pos_h2_end = html.find('</h2>', pos_h2)

new_h2_block = '''<h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-cloud text-amber-400"></i>
            <span>استوديو أدوات Fal.ai السحابية ومحرّك التوليد المباشر</span>
          </h2>

          <!-- PROMINENT FAL.AI TOOLS SELECTOR HUB -->
          <div class="mt-3 bg-gradient-to-r from-cinema-900 via-cinema-950 to-cinema-900 border-2 border-amber-500/60 rounded-2xl p-4 shadow-2xl space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-2 border-b border-cinema-700/80 pb-2">
              <div class="flex items-center gap-2">
                <span class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-sm border border-amber-500/30">
                  <i class="fa-solid fa-wand-magic-sparkles"></i>
                </span>
                <div>
                  <h3 class="text-xs font-black text-white">اختر الأداة السحابية للريندر المباشر (Fal.ai):</h3>
                  <p class="text-[10px] text-amber-300">جميع الموديلات الـ 42 متاحة هنا مباشرةً مع حساب التكلفة</p>
                </div>
              </div>
              <span id="screening-model-cost-pill" class="text-xs font-mono font-bold text-amber-300 bg-amber-950/80 px-3 py-1 rounded-lg border border-amber-500/40 shadow">~$0.03 / 5s</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
              <div class="md:col-span-8">
                <select id="screening-fal-model-select" onchange="syncScreeningStudioModel(this.value)" class="w-full bg-cinema-950 border border-cinema-gold/70 rounded-xl px-3 py-2 text-xs font-bold text-amber-200 focus:outline-none focus:border-amber-400 shadow-inner">
                  <optgroup label="🎬 موديلات الفيديو وقفل الملامح بالـ LoRA (Fal.ai)">
                    <option value="Wan 2.1 (Alibaba 14B)" selected>💎 1. Alibaba Wan 2.1 — [~$0.03 / 5s] (الأرخص إطلاقاً: $0.006/ث)</option>
                    <option value="MiniMax H3 Lite">⚡ 2. MiniMax Hailuo H3 Lite — [~$0.04 / 6s] (اقتصادي سريع)</option>
                    <option value="Wan 2.2 Image-to-Video">💎 3. Alibaba Wan 2.2 I2V — [~$0.04 / 5s] (حركية وفيزياء عالية)</option>
                    <option value="LTX-2.3 Distilled Fast LoRA">⚡ 4. LTX-2.3 Distilled LoRA — [~$0.08 / 5s] (درافت سريع بقفل لورا)</option>
                    <option value="Tencent HunyuanVideo">🎬 5. Tencent HunyuanVideo — [~$0.10 / 5s] (ثبات 13B)</option>
                    <option value="PixVerse V6 Cinematic">🎥 6. PixVerse V6 Cinematic — [~$0.18 / 5s] (20 عدسة وتحكم كاميرا)</option>
                    <option value="LTX-2.3 22B Cinema LoRA">👑 7. LTX-2.3 22B Cinema LoRA — [~$0.20 / 5s] (أعلى جودة + LoRA)</option>
                    <option value="MiniMax H3 I2V LoRA">🎯 8. MiniMax H3 I2V LoRA — [~$0.25 / 5s] (قفل ملامح الشخصية بالـ LoRA)</option>
                    <option value="MiniMax Camera Controls">📐 9. MiniMax Camera Controls — [~$0.25 / 5s] (تحكم مداري 3D Orbit)</option>
                    <option value="ByteDance Seedance 2.5">💃 10. ByteDance Seedance 2.5 — [~$0.18/s - $1.20] (حتى 30 ثانية ومراجع)</option>
                    <option value="Kling 1.6 Pro Image-to-Video">👑 11. Kling 1.6 Pro I2V — [~$0.49 / 5s] (كادر بداية ونهاية)</option>
                    <option value="Luma Ray 2 Image-to-Video">🌊 12. Luma Ray 2 I2V — [~$0.50 / 5s] (كادر بداية ونهاية)</option>
                    <option value="Kling Motion Control (1080p)">👑 13. Kling Motion Control 1080p — [~$0.63 / 5s] (نقل حركة كامل للممثل)</option>
                    <option value="Topaz Video Upscale">✨ 14. Topaz Video Upscale — [~$0.12 / 5s] (رفع الدقة السينمائية لـ 4K)</option>
                    <option value="Sync Lipsync 2.0">👄 15. Sync Lipsync 2.0 — [~$0.05 / 5s] (مزامنة الشفاه مع الصوت العربي)</option>
                    <option value="MuseTalk LipSync">👄 16. MuseTalk LipSync — [~$0.03 / 5s] (دوبلاج فوري سريع)</option>
                  </optgroup>
                  <optgroup label="📸 موديلات وتعديل الصور والكوادر بالـ LoRA (Fal.ai)">
                    <option value="fal-ai/flux/schnell">⚡ 1. FLUX.1 Schnell — [$0.003 / كادر] (أسرع درافت)</option>
                    <option value="fal-ai/nano-banana">🍌 2. Google Nano Banana — [$0.005 / كادر]</option>
                    <option value="fal-ai/nano-banana-pro">🍌 3. Google Nano Banana Pro — [$0.015 / كادر] (2K Pro)</option>
                    <option value="fal-ai/qwen-image-edit-2511">🪄 4. Qwen-Image-Edit-2511 — [$0.020 / تعديل]</option>
                    <option value="fal-ai/flux/dev">💎 5. FLUX.1 Dev — [$0.025 / كادر] (دقة سينمائية)</option>
                    <option value="blackforestlabs/flux-3/klein/edit-image/lora">⚡ 6. FLUX 3 Klein Edit LoRA — [$0.012 / MP] (تعديل بالـ LoRA)</option>
                    <option value="fal-ai/qwen-image-2512/lora">🪄 7. Qwen Image 2512 LoRA — [$0.035 / MP]</option>
                    <option value="fal-ai/flux-pro/v1.1-ultra">📸 8. FLUX 1.1 Pro Ultra — [$0.060 / كادر] (2K RAW)</option>
                  </optgroup>
                </select>
              </div>
              <div class="md:col-span-4 flex items-center gap-2">
                <button type="button" onclick="executeActiveScreeningPrompt()" class="w-full py-2 bg-gradient-to-r from-amber-500 via-cinema-gold to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-cinema-950 font-black rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-lg transition cursor-pointer">
                  <i class="fa-solid fa-play"></i>
                  <span>ريندر مباشر بالموديل المختار 🚀</span>
                </button>
              </div>
            </div>
          </div>'''

html = html[:pos_h2] + new_h2_block + html[pos_h2_end+5:]
print("Fal.ai Models Selector injected into tab-screening cleanly.")

with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html written successfully!")
