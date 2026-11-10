# Fix switchLoraSubtab and render lora-library-grid in refreshLoraLibrary
with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace switchLoraSubtab to properly handle 'train', 'library', 'generate'
old_switch = '''    function switchLoraSubtab(tab) {
      const testSec = document.getElementById('lora-subtab-test');
      const trainSec = document.getElementById('lora-subtab-train');
      const btnTest = document.getElementById('lora-btn-subtab-test');
      const btnTrain = document.getElementById('lora-btn-subtab-train');
      if (tab === 'test') {
        if (testSec) testSec.classList.remove('hidden');
        if (trainSec) trainSec.classList.add('hidden');
        if (btnTest) btnTest.className = 'px-4 py-2 rounded-xl bg-purple-600 text-white font-bold text-xs shadow';
        if (btnTrain) btnTrain.className = 'px-4 py-2 rounded-xl bg-cinema-800 text-slate-400 font-bold text-xs hover:text-white';
      } else {
        if (testSec) testSec.classList.add('hidden');
        if (trainSec) trainSec.classList.remove('hidden');
        if (btnTrain) btnTrain.className = 'px-4 py-2 rounded-xl bg-purple-600 text-white font-bold text-xs shadow';
        if (btnTest) btnTest.className = 'px-4 py-2 rounded-xl bg-cinema-800 text-slate-400 font-bold text-xs hover:text-white';
      }
    }'''

new_switch = '''    function switchLoraSubtab(tab) {
      const vTrain = document.getElementById('lora-view-train');
      const vLib = document.getElementById('lora-view-library');
      const vGen = document.getElementById('lora-view-generate');

      const bTrain = document.getElementById('lora-tabbtn-train');
      const bLib = document.getElementById('lora-tabbtn-library');
      const bGen = document.getElementById('lora-tabbtn-generate');

      const activeClass = 'px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow transition flex items-center gap-1.5 font-bold';
      const inactiveClass = 'px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition flex items-center gap-1.5 font-bold';

      if (vTrain) vTrain.classList.toggle('hidden', tab !== 'train');
      if (vLib) vLib.classList.toggle('hidden', tab !== 'library');
      if (vGen) vGen.classList.toggle('hidden', tab !== 'generate');

      if (bTrain) bTrain.className = (tab === 'train') ? activeClass : inactiveClass;
      if (bLib) bLib.className = (tab === 'library') ? activeClass : inactiveClass;
      if (bGen) bGen.className = (tab === 'generate') ? activeClass : inactiveClass;

      if (tab === 'library') {
        refreshLoraLibrary();
      }
    }'''

assert old_switch in html, "old_switch not found"
html = html.replace(old_switch, new_switch, 1)
print("index.html: switchLoraSubtab updated to show train/library/generate correctly.")

# 2. Update toggleImportLoraModal
old_modal_toggle = '''    function toggleImportLoraModal(show) {
      const m = document.getElementById('import-lora-modal');
      if (m) m.classList.toggle('hidden', !show);
    }'''

new_modal_toggle = '''    function toggleImportLoraModal(show) {
      const card = document.getElementById('lora-import-card');
      if (card) {
        if (typeof show === 'boolean') {
          card.classList.toggle('hidden', !show);
        } else {
          card.classList.toggle('hidden');
        }
      }
    }'''

if old_modal_toggle in html:
    html = html.replace(old_modal_toggle, new_modal_toggle, 1)
    print("index.html: toggleImportLoraModal fixed.")

# 3. Update refreshLoraLibrary to render cards in lora-library-grid
old_refresh = '''    function refreshLoraLibrary() {
      try {
        const res = await fetch(`${API_BASE}/api/lora/list`);
        if (!res.ok) return;
        const d = await res.json();
        const sel = document.getElementById('lora-select');
        if (sel && d.models) {
          sel.innerHTML = d.models.map(m => `<option value="${m.path || m.name}" data-trigger="${m.trigger_word || ''}">${m.name} (${m.trigger_word || 'LoRA'})</option>`).join('');
          onLoraSelectChanged();
        }
      } catch (e) {}
    }'''

new_refresh = '''    async function refreshLoraLibrary() {
      try {
        const res = await fetch(`${API_BASE}/api/lora/list`);
        if (!res.ok) return;
        const d = await res.json();
        const list = d.loras || d.models || [];

        // 1. Update dropdown in LoRA Generator View
        const sel = document.getElementById('lora-select');
        if (sel) {
          sel.innerHTML = list.map(m => `<option value="${m.weights_url || m.path || m.model_name}" data-trigger="${m.trigger_word || ''}">${m.model_name || m.name} (Trigger: ${m.trigger_word || 'lora'})</option>`).join('');
          onLoraSelectChanged();
        }

        // 2. Update Visual Cards Grid in Library View
        const grid = document.getElementById('lora-library-grid');
        if (grid) {
          if (!list.length) {
            grid.innerHTML = '<div class="col-span-full text-center py-10 text-slate-400 bg-cinema-900/50 rounded-2xl border border-cinema-800"><i class="fa-solid fa-box-open text-3xl mb-2 text-purple-400"></i><p class="font-bold text-xs">لا توجد نماذج LoRA مضافة بعد. اضغط على زر الاستيراد لإضافة نموذجك السحابي فوراً.</p></div>';
          } else {
            grid.innerHTML = list.map(m => `
              <div class="bg-cinema-900 border border-purple-500/30 hover:border-purple-400 rounded-2xl p-4 shadow-xl flex flex-col justify-between space-y-3 transition">
                <div class="flex items-start justify-between gap-2">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-purple-600/20 text-purple-300 border border-purple-500/30 flex items-center justify-center text-lg shadow">
                      🎭
                    </div>
                    <div>
                      <h4 class="font-black text-sm text-white">${escapeHtml(m.model_name || 'Actor LoRA')}</h4>
                      <p class="text-[11px] text-amber-300 font-mono">Trigger: <span class="bg-cinema-950 px-1.5 py-0.5 rounded border border-cinema-700">${escapeHtml(m.trigger_word || 'cindy_actor')}</span></p>
                    </div>
                  </div>
                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30 shrink-0">جاهز ✓</span>
                </div>

                <div class="bg-cinema-950/80 p-2.5 rounded-xl border border-cinema-800 text-[10px] font-mono text-slate-400 break-all select-all">
                  <span class="text-slate-500">الرابط السحابي:</span><br>
                  ${escapeHtml(m.weights_url || m.path || 'محفوظ محلياً')}
                </div>

                <div class="flex items-center justify-between pt-1 border-t border-cinema-800 text-xs">
                  <button type="button" onclick="navigator.clipboard.writeText('${escapeHtml(m.weights_url || '')}'); showToast('تم نسخ الرابط السحابي! 📋', 'success');" class="text-purple-300 hover:text-white font-bold flex items-center gap-1">
                    <i class="fa-solid fa-copy"></i> نسخ الرابط
                  </button>
                  <button type="button" onclick="deleteLoraEntry('${m.id}')" class="text-rose-400 hover:text-rose-300 font-bold" title="حذف من المكتبة">
                    <i class="fa-solid fa-trash-can"></i>
                  </button>
                </div>
              </div>
            `).join('');
          }
        }
      } catch (e) {
        console.warn('Failed to refresh LoRA library:', e);
      }
    }

    async function deleteLoraEntry(id) {
      if (!id || !confirm('هل أنت متأكد من حذف هذا الموديل من مكتبتك؟')) return;
      try {
        const res = await fetch(`${API_BASE}/api/lora/delete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id })
        });
        const d = await res.json();
        if (d.success) {
          showToast('تم حذف النموذج من المكتبة.', 'info');
          refreshLoraLibrary();
        }
      } catch (e) {}
    }'''

assert old_refresh in html, "old_refresh not found"
html = html.replace(old_refresh, new_refresh, 1)
print("index.html: refreshLoraLibrary updated with full grid rendering and delete.")

with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html fixed successfully!")
