# Add syncScreeningStudioModel right before function executeActiveScreeningPrompt
with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "r", encoding="utf-8") as f:
    html = f.read()

target = "function executeActiveScreeningPrompt() {"

helper = """function syncScreeningStudioModel(val) {
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

    function executeActiveScreeningPrompt() {"""

if 'function syncScreeningStudioModel' not in html:
    assert target in html, "target not found"
    html = html.replace(target, helper, 1)
    with open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("syncScreeningStudioModel injected successfully!")
else:
    print("syncScreeningStudioModel already present.")
