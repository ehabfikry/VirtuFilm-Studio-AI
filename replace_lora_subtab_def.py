# Correctly replace switchLoraSubtab in index.html
with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "r", encoding="utf-8") as f:
    html = f.read()

old_switch_exact = """function switchLoraSubtab(tab) {
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
    }"""

new_switch_exact = """function switchLoraSubtab(tab) {
      console.log('switchLoraSubtab triggered:', tab);
      const vTrain = document.getElementById('lora-view-train');
      const vLib = document.getElementById('lora-view-library');
      const vGen = document.getElementById('lora-view-generate');

      const bTrain = document.getElementById('lora-tabbtn-train');
      const bLib = document.getElementById('lora-tabbtn-library');
      const bGen = document.getElementById('lora-tabbtn-generate');

      const activeClass = 'px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow transition flex items-center gap-1.5 font-bold cursor-pointer';
      const inactiveClass = 'px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition flex items-center gap-1.5 font-bold cursor-pointer';

      if (vTrain) vTrain.classList.toggle('hidden', tab !== 'train');
      if (vLib) vLib.classList.toggle('hidden', tab !== 'library');
      if (vGen) vGen.classList.toggle('hidden', tab !== 'generate');

      if (bTrain) bTrain.className = (tab === 'train') ? activeClass : inactiveClass;
      if (bLib) bLib.className = (tab === 'library') ? activeClass : inactiveClass;
      if (bGen) bGen.className = (tab === 'generate') ? activeClass : inactiveClass;

      if (tab === 'library') {
        refreshLoraLibrary();
      }
    }"""

assert old_switch_exact in html, "old_switch_exact not found"
html = html.replace(old_switch_exact, new_switch_exact, 1)

with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("switchLoraSubtab replaced cleanly and definitively!")
