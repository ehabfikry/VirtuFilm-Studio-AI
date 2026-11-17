"""
=============================================================================
CINDY GITHUB COMMUNITY & TRIAGE DESK
(مكتب مجتمع سيندي على GitHub للرد الآلي والدعم الفني والتقني)
=============================================================================
مخصص للمخرج إيهاب فكري لإدارة ومتابعة مشروعه على GitHub:
1. متابعة الـ Issues, Pull Requests, Stars, Forks بمجرد إتاحة المستودع.
2. الرد الذكي الفوري (Technical & Directorial AI Responder) نيابة عن المخرج:
   - يقرأ استفسار المطور أو المستخدم (بالعربية أو الإنجليزية).
   - يصيغ رداً هندسياً وإخراجياً متكاملاً يشرح كيفية استخدام الأداة بدقة.
   - يعطي كود الإجابة المقترح بأسلوب احترافي لنسخه إلى GitHub بنقرة زر أو إرساله عبر API.
3. قوالب ردود جاهزة لأشهر الأسئلة الشائعة (FAQ / Known Issues).
=============================================================================
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser

PORT = 8790
SERVER_ROOT = os.path.dirname(os.path.abspath(__file__))
SECRETS_FILE = os.path.join(SERVER_ROOT, "cindy_secrets.json")

def load_secrets():
    if os.path.exists(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def fetch_github_repo_stats(repo_slug="ehabfikry/VirtuFilm-Studio-AI"):
    """Fetches public stats from GitHub API without requiring auth, or handles simulated offline mode."""
    url = f"https://api.github.com/repos/{repo_slug}"
    headers = {"User-Agent": "Cindy-GitHub-Desk/1.0", "Accept": "application/vnd.github.v3+json"}
    
    secrets = load_secrets()
    gh_token = secrets.get("github_token") or secrets.get("github_pat") or ""
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "online": True,
                "name": data.get("full_name", repo_slug),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "watchers": data.get("subscribers_count", 0),
                "default_branch": data.get("default_branch", "main"),
                "status_label": "المستودع متاح علناً على GitHub 🟢"
            }
    except Exception:
        return {
            "online": False,
            "name": repo_slug,
            "stars": 0,
            "forks": 0,
            "open_issues": 0,
            "watchers": 0,
            "default_branch": "main",
            "status_label": "بانتظار الضغط على نشر المستودع (Draft Mode / Ready to Publish) 🟡"
        }

def call_llm_for_triage(issue_title, issue_body, issue_category="issue"):
    secrets = load_secrets()
    openrouter_key = secrets.get("openrouter_api_key", "").strip()
    fal_key = secrets.get("fal_api_key", "").strip()

    system_instruction = """You are the official GitHub AI Lead Engineer & Directorial Triage Assistant for 'Cindy-AI-Director' (VirtuFilm Studio AI), representing Film Director Ehab Fikry and Google DeepMind Antigravity.
Your mission:
1. Provide authoritative, friendly, highly professional technical responses to developers and filmmakers opening GitHub Issues, Discussions, or Pull Requests.
2. Format answers in clean GitHub-Flavored Markdown (with code blocks, bullet points, and step-by-step instructions).
3. If the user writes in Arabic, respond in clear, professional Arabic. If they write in English, respond in idiomatic English.
4. Always clarify:
   - Architecture: Cindy is a hybrid Local + Cloud AI Directorial platform (Blender 5.3 3D Previs + ComfyUI local 24GB + Fal.ai/RunPod Cloud BYOK).
   - No hidden API costs or unauthorized charges (Zero-Cost Balance Guard).
   - Film Direction First: Directorial framing, camera orbits, identity-locking via LoRA, and master timeline assembly.
5. Provide a 'Ready-to-Post Response' that Director Ehab Fikry can review and copy-paste directly to GitHub in one second.
"""

    prompt = f"""
A developer/user posted a GitHub {issue_category.upper()}:
**Title:** {issue_title}
**Body / Question:**
{issue_body}

Compose the official response for Director Ehab Fikry to publish on GitHub. Include:
1. Executive acknowledgment & greeting.
2. Root Cause / Technical explanation.
3. Exact step-by-step fix or code snippet.
4. Closing note of appreciation.
"""

    # Try OpenRouter
    if openrouter_key:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:8790",
                "X-Title": "Cindy GitHub Desk"
            }
            body = {
                "model": "meta-llama/llama-3.3-70b-instruct",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print("[OpenRouter Triage Warn]:", e)

    # Try Fal Any-LLM
    if fal_key:
        try:
            url = "https://fal.run/fal-ai/any-llm"
            headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
            body = {
                "prompt": f"{system_instruction}\\n\\n{prompt}",
                "model": "google/gemini-2.5-flash-lite"
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("output", "")
        except Exception as e:
            print("[Fal Triage Warn]:", e)

    # Built-in High-Level Templates
    return generate_fallback_triage_answer(issue_title, issue_body)

def generate_fallback_triage_answer(title, body):
    t_lower = (title + " " + body).lower()
    if "install" in t_lower or "requirement" in t_lower or "تثبيت" in t_lower:
        return """### Hello and welcome to Cindy-AI-Director! 👋

Thank you for opening this issue. Here is the direct resolution for your installation query:

#### Recommended Environment:
* **OS:** Windows 10/11 (or Ubuntu 22.04 LTS)
* **Python:** 3.10.x - 3.11.x (PyTorch 2.4+ with CUDA 12.4 support)
* **3D Engine:** Blender 5.3 LTS (installed in default location or symlinked)

#### One-Click Resolution:
```bash
# 1. Clone repository
git clone https://github.com/ehabfikry/VirtuFilm-Studio-AI.git
cd VirtuFilm-Studio-AI

# 2. Run Windows Setup
install_windows.bat
# Or manually:
pip install -r requirements.txt
python cindy_server.py
```
If you encounter missing wheel packages, ensure Microsoft C++ Build Tools are installed.

Best regards,  
**Director Ehab Fikry & Antigravity (Google DeepMind)**
"""
    elif "api" in t_lower or "key" in t_lower or "cost" in t_lower or "مفتاح" in t_lower:
        return """### Hello! 👋

Thank you for reaching out regarding API key setup and cloud execution.

`Cindy-AI-Director` is strictly architected on the **BYOK (Bring Your Own Key)** standard:
1. **Zero Secret Leakage:** Keys are stored exclusively in your local `cindy_secrets.json`, which is permanently bound to `127.0.0.1` and git-ignored.
2. **Zero-Cost Balance Guard:** The platform never executes billable runs without explicit modal confirmation.
3. **Local Alternatives:** If you do not have cloud API keys, switch to **Local ComfyUI Mode** or **Blender 5.3 3D Previs** for 100% free, zero-API cost workflows.

Best regards,  
**Director Ehab Fikry & Antigravity**
"""
    else:
        return f"""### Thank you for your contribution to Cindy-AI-Director! 👋

We have registered this query regarding: **{title}**

#### Preliminary Directorial & Technical Guidance:
1. Please confirm that your local Cindy Server is running on `http://127.0.0.1:8765`.
2. Check your browser developer console (`F12`) to verify websocket and API responses.
3. For reproducible bug reports, kindly provide your OS version, GPU VRAM size, and model choice (e.g., Seedance 2.5, Kling 4.0, or ComfyUI Local).

We are actively reviewing this and will provide additional code patches if necessary.

Warm regards,  
**Director Ehab Fikry & Antigravity AI Team**
"""

class CommunityDeskHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(SERVER_ROOT, "director_desk.html"), "rb") as f:
                self.wfile.write(f.read())
            return
        elif parsed.path == "/api/desk/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            stats = fetch_github_repo_stats()
            self.wfile.write(json.dumps({"success": True, "stats": stats}, ensure_ascii=False).encode("utf-8"))
            return
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/desk/triage":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8")
            try:
                req_data = json.loads(post_body)
                title = req_data.get("title", "").strip()
                body = req_data.get("body", "").strip()
                category = req_data.get("category", "issue")
            except Exception:
                title = ""
                body = ""
                category = "issue"

            if not title and not body:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "البيانات فارغة"}).encode("utf-8"))
                return

            response_markdown = call_llm_for_triage(title, body, category)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "response": response_markdown}, ensure_ascii=False).encode("utf-8"))
            return

        super().do_POST()

def run_desk():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, CommunityDeskHandler)
    print(f"==================================================================")
    print(f"🌐 CINDY GITHUB COMMUNITY DESK IS RUNNING ON: http://127.0.0.1:{PORT}")
    print(f"==================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCommunity Desk Stopped.")

if __name__ == "__main__":
    run_desk()
