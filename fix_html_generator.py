with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad_snippet = '''  <script src="https://cdn.tailwindcss.com">
  async function checkComfyNodeStatus() {
    try {
      const res = await fetch('/api/comfyui/node_status');
      if (!res.ok) return;
      const data = await res.json();
      if (!data.online) return;
      const setBadge = (id, ok) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.className = ok ? 'text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono' : 'text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 font-mono';
        el.innerText = ok ? 'جاهز' : 'غير مثبت';
      };
      setBadge('badge-node-wan', data.wan21 || data.wan22);
      setBadge('badge-node-hunyuan', data.hunyuan);
      setBadge('badge-node-cogvideo', data.cogvideox);
      setBadge('badge-node-vhs', data.vhs);
    } catch (e) {
      console.warn('Node status check failed:', e);
    }
  }

  async function installComfyNodesNow() {
    const btn = document.getElementById('btn-install-comfy-nodes');
    const msg = document.getElementById('node-install-status-msg');
    if (btn) btn.disabled = true;
    if (msg) {
      msg.classList.remove('hidden');
      msg.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> جاري إرسال أوامر تثبيت حزم الـ Nodes (Wan 2.1/2.2, Hunyuan, CogVideoX, VHS)...';
    }
    try {
      const res = await fetch('/api/comfyui/install_nodes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
      const data = await res.json();
      if (msg) msg.innerHTML = '✓ ' + (data.message || 'تم إرسال أوامر التثبيت بنجاح!');
      setTimeout(() => { checkComfyNodeStatus(); }, 5000);
    } catch (e) {
      if (msg) msg.innerHTML = '✕ فشل إرسال أمر التثبيت: ' + e.message;
    } finally {
      if (btn) btn.disabled = false;
    }
  }
</script>'''

clean_tailwind = '  <script src="https://cdn.tailwindcss.com"></script>'

if bad_snippet in text:
    text = text.replace(bad_snippet, clean_tailwind)
    print("Removed misplaced script from tailwind tag!")

# Now add escaped javascript at the very end before </body>
escaped_js = '''
  <script>
  async function checkComfyNodeStatus() {{
    try {{
      const res = await fetch('/api/comfyui/node_status');
      if (!res.ok) return;
      const data = await res.json();
      if (!data.online) return;
      const setBadge = (id, ok) => {{
        const el = document.getElementById(id);
        if (!el) return;
        el.className = ok ? 'text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono' : 'text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 font-mono';
        el.innerText = ok ? 'جاهز' : 'غير مثبت';
      }};
      setBadge('badge-node-wan', data.wan21 || data.wan22);
      setBadge('badge-node-hunyuan', data.hunyuan);
      setBadge('badge-node-cogvideo', data.cogvideox);
      setBadge('badge-node-vhs', data.vhs);
    }} catch (e) {{
      console.warn('Node status check failed:', e);
    }}
  }}

  async function installComfyNodesNow() {{
    const btn = document.getElementById('btn-install-comfy-nodes');
    const msg = document.getElementById('node-install-status-msg');
    if (btn) btn.disabled = true;
    if (msg) {{
      msg.classList.remove('hidden');
      msg.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> جاري إرسال أوامر تثبيت حزم الـ Nodes (Wan 2.1/2.2, Hunyuan, CogVideoX, VHS)...';
    }}
    try {{
      const res = await fetch('/api/comfyui/install_nodes', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: '{{}}' }});
      const data = await res.json();
      if (msg) msg.innerHTML = '✓ ' + (data.message || 'تم إرسال أوامر التثبيت بنجاح!');
      setTimeout(() => {{ checkComfyNodeStatus(); }}, 5000);
    }} catch (e) {{
      if (msg) msg.innerHTML = '✕ فشل إرسال أمر التثبيت: ' + e.message;
    }} finally {{
      if (btn) btn.disabled = false;
    }}
  }}
  </script>
'''

if 'async function checkComfyNodeStatus()' not in text:
    idx = text.rfind('</body>')
    if idx != -1:
        text = text[:idx] + escaped_js + '\n' + text[idx:]
        print("Injected properly escaped node manager script before </body>!")

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved generate_enhanced_html.py!")
