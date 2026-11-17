# VirtuFilm Studio AI (feat. Cindy AI Assistant) 🎬

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Creator](https://img.shields.io/badge/Conceived%20by-Ehab%20Fikry-gold?style=for-the-badge)](https://github.com/ehabfikry)
[![Role](https://img.shields.io/badge/Role-Cinema%20Enthusiast%20&%20Storyteller-purple?style=for-the-badge)](https://github.com/ehabfikry)
[![Primary OS](https://img.shields.io/badge/Primary%20Environment-Windows%2010%2F11%20(Fully%20Tested)-success?style=for-the-badge)](https://github.com/ehabfikry/VirtuFilm-Studio-AI)
[![Experimental](https://img.shields.io/badge/macOS%20%26%20Linux-Experimental%20%2F%20Community%20Preview-amber?style=for-the-badge)](https://github.com/ehabfikry/VirtuFilm-Studio-AI)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=for-the-badge)](https://www.python.org/)

An open-source workflow and visual experimentation studio conceived by **Ehab Fikry** (*إيهاب فكري*), an independent cinema enthusiast, storyteller, and creative thinker, in technical and AI implementation collaboration with **Antigravity (Google DeepMind)**.

VirtuFilm Studio AI is designed to explore the intersection between open-source computer graphics tools and modern generative AI models, making cinematic experimentation accessible, budget-conscious, and structured for independent creators.

---

## 💡 Origin & Open-Source Philosophy (فلسفة المشروع والتواضع التقني)

This project does not claim to invent new generative neural architectures from scratch. Instead, it proudly stands on the shoulders of the global open-source community, synthesizing and bridging several proven open technologies into a unified personal experimentation environment:

1. **3D Spatial Staging:** Utilizing **Blender LTS** purely as a local spatial blocking tool (calculating camera angles and perspective orbits) before generating frames.
2. **Community Ecosystem Integration:** Respectfully learning from and integrating workflow patterns inspired by community milestones such as **ComfyUI**, **Clapper**, **OpenMontage**, and the broader open-weights ecosystem.
3. **Actor Continuity Experiments:** Experimenting with standard Low-Rank Adaptation (LoRA) pipelines to study face consistency across sequential narrative scenes.
4. **Multi-Model Orchestration:** Providing clean local scripts to test multi-model generations (Fal.ai, RunPod, and local setups) under a strict BYOK (Bring Your Own Key) policy.

---

## 🛠️ What This Studio Provides

* **Pre-visualization Bridge:** Local interface to experiment with camera tracks and angles in 3D prior to video diffusion.
* **Cost Guardrails:** Clear estimates and zero-cost local alternatives (ComfyUI local mode) to prevent accidental cloud spend.
* **Multilingual UI (4 Languages):** Native interface support for English, Arabic, French, and Spanish (`en`, `ar`, `fr`, `es`) tailored for independent storytelling experimentation.
* **Community Triage Desk:** A lightweight assistant to help answer technical setup questions and organize community feedback.

---

## 💻 Supported Environments & Compatibility Status (حالة التوافق وبيئات التشغيل)

| Operating System | Testing Status | Hardware / GPU | 3D Engine Setup | Launch Command |
| :--- | :--- | :--- | :--- | :--- |
| **Windows 10 / 11** | **Verified & Fully Tested 🟢** | NVIDIA RTX (CUDA) or CPU | Blender 5.3 LTS (Auto-detected) | `install_windows.bat` (Recommended) |
| **macOS (Apple Silicon / Intel)** | **Experimental / Community Preview 🟡** | Apple Metal (MPS) or CPU | Blender LTS (`/Applications/Blender.app`) | `./install_mac_linux.sh` |
| **Linux (Ubuntu 22.04+)** | **Experimental / Community Preview 🟡** | NVIDIA CUDA or CPU | Blender LTS (System PATH) | `./install_mac_linux.sh` |

> [!NOTE]
> **Honest Engineering Transparency (الشفافية الهندسية الصريحة):**
> This repository was developed and benchmarked on a **Windows 11 workstation with local Blender 5.3 and NVIDIA CUDA runtime**. 
> While the code is written in cross-platform standard Python 3 and web standards, and includes `install_mac_linux.sh` for Unix environments, full runtime testing on native macOS (Apple Silicon MPS) and Linux distributions is currently in **Community Preview**. Feedback and Pull Requests from Mac and Linux users are warmly welcomed.

* **Python Runtime:** Python 3.10.x or 3.11.x (Recommended: isolated virtualenv `.venv`).
* **GPU Memory (Optional for Local Nodes):** 8GB–24GB VRAM for local ComfyUI diffusion, or zero local VRAM requirements when utilizing cloud BYOK dispatchers (Fal.ai / RunPod).

## 🚀 Quick Start (Windows, macOS & Linux)

### 🪟 Windows Setup (One-Click)
```bash
git clone https://github.com/ehabfikry/VirtuFilm-Studio-AI.git
cd VirtuFilm-Studio-AI
install_windows.bat
```

### 🍎 macOS & Linux Setup (Apple Silicon M1/M2/M3/M4 & Intel)
```bash
git clone https://github.com/ehabfikry/VirtuFilm-Studio-AI.git
cd VirtuFilm-Studio-AI
chmod +x install_mac_linux.sh
./install_mac_linux.sh
```
The studio will automatically open in your browser at: **`http://127.0.0.1:8765`**

---

## ❓ Frequently Asked Questions (FAQ / أسئلة شائعة وإجابات صريحة)

<details>
<summary><b>1. Is VirtuFilm Studio AI claiming to invent new AI models or replace tools like ComfyUI / Clapper?</b></summary>
<br>

**No, absolutely not.**  
This project is conceived by an independent cinema enthusiast and storyteller. It does not invent new neural algorithms or claim novelty over existing solutions. It is an experimental personal workflow designed to connect proven open technologies (Blender for spatial staging, ComfyUI for local nodes, and community diffusion pipelines) into an accessible interface for testing scene continuity. We deeply respect and stand on the shoulders of the global open-source ecosystem.
</details>

<details>
<summary><b>2. How does 3D Pre-visualization work with Blender LTS?</b></summary>
<br>

Blender is used strictly as a local coordinate calculator (Pre-vis). Instead of burning cloud GPU credits guessing camera trajectories, you can plan your 6-DoF camera moves (Dolly, Crane, Orbit, Track) inside Blender to extract spatial perspective before dispatching prompts to neural video backends.
</details>

<details>
<summary><b>3. Are my API keys safe, and does this studio incur hidden cloud charges?</b></summary>
<br>

**100% Safe (BYOK Standard).**  
All operations run locally bound to `127.0.0.1`. Your API credentials remain exclusively inside your local `cindy_secrets.json`, which is permanently excluded from version control. The studio will never execute paid external generation calls without your explicit modal confirmation. You can also run 100% free locally using ComfyUI.
</details>

<details>
<summary><b>4. Who owns the rights to films and images generated with this studio?</b></summary>
<br>

**You do (100% Filmmaker Ownership).**  
Under the AGPL-3.0 license, while the workflow engine is open-source, all original stories, characters, prompts, rendered frames, and final movies produced by you belong entirely to you with zero royalty claims from us.
</details>

<details>
<summary><b>5. How can I train actor identity LoRAs economically?</b></summary>
<br>

By preparing 15–20 clear, diverse reference photos of your performer and running standard LoRA training scripts on an on-demand cloud GPU (like an RTX 4090 on RunPod), a complete character checkpoint typically finishes in 5–6 minutes for approximately **$0.04** total.
</details>

## 🛡️ Attribution, Legal Clearance & Disclaimers

* **Independent Non-Commercial Vision:** This repository represents personal creative research by a cinema enthusiast seeking practical solutions for narrative consistency in AI video.
* **Open Source Attribution:** All third-party tools, frameworks, and model weights (Blender, ComfyUI, PyTorch, Fal endpoints) remain the sole property and trademarks of their respective creators and organizations.
* **BYOK Standard:** Users provide their own API credentials. No proprietary weights or private keys are bundled or hosted.
* **License:** Licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE). Creative outputs and stories generated by users belong entirely to them.

---

For collaborative ideas or feedback:  
📧 **ehabfikry@gmail.com**
