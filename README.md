# Cindy-AI-Director (VirtuFilm Studio AI) 🎬

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Directorial Vision](https://img.shields.io/badge/Director-Ehab%20Fikry-gold?style=for-the-badge)](https://github.com/ehabfikry)
[![AI Architecture](https://img.shields.io/badge/AI%20Architecture-Antigravity%20(Google%20DeepMind)-indigo?style=for-the-badge)](https://github.com/ehabfikry/VirtuFilm-Studio-AI)
[![3D Engine](https://img.shields.io/badge/3D%20Engine-Blender%205.3%20LTS-orange?style=for-the-badge)](https://www.blender.org/)
[![Local Studio](https://img.shields.io/badge/Local%20ComfyUI-24.9%20GB%20VRAM-emerald?style=for-the-badge)](http://127.0.0.1:8765)

An autonomous, end-to-end AI virtual filmmaking studio and directorial platform conceived and directed by **Ehab Fikry** (*المخرج إيهاب فكري*) in software and AI architecture collaboration with **Antigravity (Google DeepMind)**.

Cindy-AI-Director empowers indie filmmakers, directors, and creators to orchestrate full-length feature films by bridging:
1. **Local 3D Pre-vis & Camera Orbits** via **Blender 5.3 LTS**.
2. **Actor Identity-Anchoring** via **RunPod LoRA training** ($0.04 per character).
3. **Multi-Track Master Assembly & Resonant Audio** via **OpenMontage** & **Resonant DAW**.
4. **Cinematic Neural Generation** via ByteDance **Seedance 2.5**, **Kling 4.0 Pro Omni**, **Google Veo 3.1**, and local **ComfyUI**.

---

## 🌟 Key Architectural Capabilities

| Pillar | Technical Mechanism | Benefit for Filmmakers |
| :--- | :--- | :--- |
| **3D Pre-vis & Camera Orbits** | Embedded local Blender 5.3 bridge | Frame shots, plan camera motion (Dolly/Crane/Orbit), and calculate focal lengths with **$0 API cost** before rendering. |
| **Identity Anchoring (LoRA)** | Automated RunPod on-demand GPU pipeline | Train high-fidelity actor identity LoRAs in 5 minutes on an RTX 4090 for **~$0.04** total. |
| **4-Pass Directorial Pipeline** | Script -> 3D Pre-vis -> Neural Video -> 4K Reframe & Polish | Eliminates character drift, limb hallucinations, and erratic camera movements. |
| **2026 Cinema AI Radar** | Dynamic industry tracker (25+ cutting-edge models) | Real-time monitoring of ByteDance Seedance 2.5, Kling 4.0 Pro, OpenMontage timeline, and Resonant DAW. |
| **Zero-Leak Security (BYOK)** | Localhost 127.0.0.1 binding & strictly local secrets | Bring Your Own Key (Fal.ai, RunPod, Gemini, OpenRouter) with zero telemetry and zero unauthorized cloud execution. |

---

## 🚀 Quick Start (Windows)

### 1. One-Click Installation
Clone the repository and run the Windows automated setup:

```bash
git clone https://github.com/ehabfikry/VirtuFilm-Studio-AI.git
cd VirtuFilm-Studio-AI
install_windows.bat
```

### 2. Manual Installation
```bash
# Clone repository
git clone https://github.com/ehabfikry/VirtuFilm-Studio-AI.git
cd VirtuFilm-Studio-AI

# Install dependencies
pip install -r requirements.txt

# Launch Core Studio Server
python cindy_server.py
```
Open your browser at: **`http://127.0.0.1:8765`**

---

## 🌐 Community & Triage Desk (For Developers & Filmmakers)

Cindy includes a dedicated background assistant for managing GitHub issues, community discussions, and technical triage:

```bash
# Launch GitHub Community Desk
launch_director_desk.bat
# Or manually:
python cindy_desk_server.py
```
Open your browser at: **`http://127.0.0.1:8790`**

---

## 🛡️ Security, Privacy & BYOK Standard

* **Localhost-Only Enforcement:** The server binds strictly to `127.0.0.1` and blocks non-local origins.
* **Vault Isolation:** All API credentials reside in `cindy_secrets.json`, which is permanently excluded from Git commits (`.gitignore`) and forbidden from HTTP static file serving.
* **Zero-Cost Guard:** The platform never triggers paid API calls automatically. Every generation requires an explicit modal confirmation.

---

## ⚖️ License & Intellectual Property

* **License:** GNU Affero General Public License v3.0 ([AGPL-3.0](LICENSE)).
* **Creative Ownership:** Users and filmmakers retain **100% full commercial ownership** of all generated shots, videos, storyboards, and final films produced inside the studio.
* **Directorial Vision & Architecture:** Conceived by **Director Ehab Fikry** in architectural collaboration with **Antigravity (Google DeepMind)**.

---

For commercial partnerships, feature film inquiries, or enterprise licensing:  
📧 **ehabfikry@gmail.com**
