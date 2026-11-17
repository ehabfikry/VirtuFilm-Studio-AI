# CINDY-AI-DIRECTOR (VirtuFilm Studio AI)
## LEGAL CLEARANCE, INTELLECTUAL PROPERTY & CREATIVE PROTECTION SPECIFICATION

**Project Title:** Cindy-AI-Director / VirtuFilm Studio AI  
**Directorial Vision, Screenplay & Creator:** Ehab Fikry (المخرج إيهاب فكري)  
**Autonomous Systems Architecture & AI Engineering:** Antigravity (Google DeepMind)  
**Governing Standard:** Open-Core Architecture under GNU AGPL-3.0 with Commercial SaaS Reservation  
**International Legal Framework:** WIPO Berne Convention for the Protection of Literary and Artistic Works (181 Countries)  
**Cryptographic Timestamp & Proof of Creation:** SHA-256 Git Timestamp Ledger  

---

### 1. CREATIVE INTEGRITY & FILMMAKER'S OWNERSHIP (حماية حقوق المخرج الإبداعية)

1. **Absolute Ownership of Creative Outputs:**
   * **100% Commercial Filmmaker Rights:** All screenplay texts, character concepts, storyboards, 3D blocking arrangements, rendered video frames, dialogues, and final feature film exports generated within Cindy-AI-Director are the **exclusive property of the director / creator**.
   * **Zero Royalty & Zero Platform Claim:** Neither the software maintainers nor downstream AI model providers hold any intellectual property claim, copyright share, or distribution royalties over films produced using this platform.

2. **Character & Cast Protection (حماية الهوية والشخصيات الدرامية):**
   * **Private Identity Anchoring:** Actor LoRA weights, facial biometric vectors, and reference photography remain strictly localized on the user's host machine or private cloud storage pods (RunPod/Fal BYOK).
   * **No Public Scraping or Training:** Cindy-AI-Director contains no telemetry or central data harvesting. Characters and proprietary actors (such as *Abdelaziz*, *Abdelshakoor*, and others) are never uploaded to public model hubs or public repositories without explicit directorial consent.

---

### 2. ARCHITECTURAL PRIOR-ART DISCLOSURE (معمارية الابتكار وحماية السبق البرمجي)

Cindy-AI-Director resolves the three fundamental defects of generative video AI (character drift, erratic camera motion, and anatomy hallucinations) through a decoupled **4-Pass Directorial Pipeline**:

1. **Pillar 1: Neural Identity Anchoring Module (NIAM)**
   * Decouples character identity from temporal video generation.
   * Utilizes on-demand low-rank adaptation (LoRA) checkpoint matrices ($0.04/run on RTX 4090).
   * Generates a 2D seed keyframe establishing facial fidelity, costume texture, and lighting continuity before motion synthesis.

2. **Pillar 2: Spatial Geometry & Camera Pre-vis Engine (Blender 5.3 LTS)**
   * Binds locally to Blender 5.3 to calculate true 6-Degrees-of-Freedom (6-DoF) camera trajectories (Dolly, Track, Crane, Radial Orbit).
   * Bakes depth maps and spatial blocking coordinates with **$0 API cost** prior to video rendering, preventing erratic drone float.

3. **Pillar 3: Constrained Temporal Neural Dispatcher (CTND)**
   * Dispatches generation tasks across leading neural engines (ByteDance Seedance 2.5, Kling 4.0 Pro Omni, Google Veo 3.1, or local ComfyUI).
   * Dynamically injects negative anatomical penalty vectors to prevent extremity distortions (extra fingers, deformed limbs).

4. **Pillar 4: Dual-Engine Master Assembly (OpenMontage & Resonant DAW)**
   * Directorial timeline assembly with automated dialogue sync and sound environment design.

---

### 3. LEGAL CLEARANCE & OPEN-SOURCE COMPLIANCE (التوافق القانوني ونظام التراخيص)

1. **BYOK Standard (Bring Your Own Key):**
   * Cindy-AI-Director distributes **zero proprietary model weights** and **zero paid cloud subscriptions**.
   * All API calls are executed directly from the user's local server to official provider endpoints (Fal.ai, RunPod, Gemini, OpenRouter) using the user's private keys stored in `cindy_secrets.json`.
   * The platform acts purely as an open-source directorial workflow orchestrator, exempt from third-party hosting liabilities.

2. **GPL & Subprocess Compliance:**
   * External open-source engines (e.g., Blender 5.3 and FFmpeg) are executed strictly via standalone command-line subprocesses and standard IPC pipes, fully complying with GPL/LGPL licensing standards.

3. **Commercial SaaS & Multi-Tenant Reservation:**
   * While individual filmmakers, indie studios, researchers, and students are free to use, modify, and build upon Cindy-AI-Director for free under the **GNU AGPL-3.0 License**, any deployment of this platform as a hosted, multi-tenant commercial SaaS service requires an explicit commercial agreement with **Director Ehab Fikry**.

---

### 4. LIMITATION OF LIABILITY & DISCLAIMER (إخلاء المسؤولية القانونية المعتمد)

* **As-Is Provision:** The software is provided "AS IS", without warranty of any kind, express or implied.
* **Actor Consent Compliance:** The user warrants that they possess lawful consent, likeness clearance, and commercial rights for any individual or performer whose photography is utilized for training LoRA identity checkpoints.
* **No Unlawful Generation:** The platform strictly prohibits the generation of non-consensual deepfakes, defamatory media, or content violating international cyber-safety regulations.

---

**Certified & Recorded:** November 2026  
**Creator & Director:** Ehab Fikry (المخرج إيهاب فكري)  
**Systems Architecture:** Antigravity (Google DeepMind)
