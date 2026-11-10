import os, sys

target_file = r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py'
with open(target_file, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Insert cost badge into #smart-ref-hub
target_hub = """            <!-- 4. State: Video-to-Video Edit (Original Video to Restyle) -->
            <div id="ref-mode-v2v-panel" class="hidden flex items-center gap-2 bg-blue-950/30 border border-blue-500/40 rounded-xl px-2.5 py-1 shadow-inner">
              <input type="file" id="v2v-source-file-input" accept="video/*" class="hidden" onchange="handleV2VSourceSelected(event)">
              <span class="text-blue-300 font-bold text-[10px] flex items-center gap-1">
                <i class="fa-solid fa-film"></i> الفيديو الأصلي للتعديل:
              </span>
              <div id="v2v-source-empty" class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('v2v-source-file-input').click()" class="px-2 py-0.5 rounded-lg bg-blue-700 hover:bg-blue-600 text-white font-bold text-[10px] flex items-center gap-1 shadow">
                  رفع فيديو MP4
                </button>
              </div>
              <div id="v2v-source-active" class="hidden flex items-center gap-1.5">
                <span id="v2v-source-badge" class="text-[10px] font-bold text-blue-300 bg-blue-500/20 px-2 py-0.5 rounded border border-blue-500/30">✓ الفيديو محدد</span>
                <button type="button" onclick="clearV2VSource()" class="text-rose-400 text-xs px-0.5">✕</button>
              </div>
            </div>"""

cost_badge = """            <!-- Active Model Cost Estimate Badge -->
            <div id="model-cost-estimate-badge" class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cinema-950/90 border border-amber-500/30 text-[10px] text-slate-300 font-semibold cursor-pointer shrink-0 shadow" onclick="openDailyPricingModal()" title="عرض مؤشر أسعار الأدوات والخدمات السحابية">
              <i class="fa-solid fa-coins text-amber-400 text-xs"></i>
              <span class="text-slate-400">التكلفة:</span>
              <span id="active-model-cost-val" class="text-amber-300 font-mono font-bold">~$0.63 / 5s</span>
            </div>"""

if target_hub in text and 'model-cost-estimate-badge' not in text:
    text = text.replace(target_hub, target_hub + "\n\n" + cost_badge, 1)
    print("Cost badge added to #smart-ref-hub.")

# 2. Update updateReferenceInputsForModel to set cost tag
old_fn = "function updateReferenceInputsForModel(modelName) {{"
new_fn = """function updateReferenceInputsForModel(modelName) {{
      const costVal = document.getElementById('active-model-cost-val');
      if (costVal) {{
        costVal.innerText = MODEL_COST_MAP[modelName] || '~$0.50 / 5s';
      }}"""

if old_fn in text and 'costVal.innerText = MODEL_COST_MAP' not in text:
    text = text.replace(old_fn, new_fn, 1)
    print("updateReferenceInputsForModel updated with price map logic.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patching complete.")
