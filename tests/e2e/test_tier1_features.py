"""Tier 1 E2E Feature Coverage Tests (37 tests across FG1-FG7)."""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from tests.e2e import REPO_ROOT, SERVER_URL
from tests.e2e.helpers import (
    HeadlessBrowser,
    IsolatedServerManager,
    RUNTIME_PY_MODULES,
    ast_check_subprocesses,
    extract_html_ids,
    extract_inline_scripts,
    ffprobe_inspect,
    generate_test_mp4,
    generate_test_wav,
    make_valid_png_data_url,
    run_node_check,
    strip_html_comments,
)


def _read_repo_file(rel_path: str) -> str:
    with open(os.path.join(REPO_ROOT, rel_path), "r", encoding="utf-8") as fh:
        return fh.read()


class Tier1Base(unittest.TestCase):
    server: IsolatedServerManager = None

    @classmethod
    def setUpClass(cls):
        if Tier1Base.server is None:
            mgr = IsolatedServerManager()
            mgr.start()
            Tier1Base.server = mgr

    def setUp(self):
        self.server.mock_ext.reset_config()
        self.server.mock_ext.clear_ledger()
        self.server.mock_ff.reset_config()
        self.server.mock_ff.clear_ledger()
        self.server.reset_loras()


def tearDownModule():
    if Tier1Base.server is not None:
        Tier1Base.server.stop()
        Tier1Base.server = None


# =============================================================================
# FG1: R1 Dead Code & UI Cleanup (6 tests)
# =============================================================================
class TestTier1FG1Cleanup(Tier1Base):
    def test_t1_fg1_01_index_no_flow_bridge(self):
        raw = _read_repo_file("index.html")
        visible = strip_html_comments(raw)
        self.assertNotIn("tab-flow", visible)
        self.assertEqual(len(re.findall(r"Flow\s+Bridge", visible, re.IGNORECASE)), 0)
        self.assertNotIn('id="bridge-guide-modal"', visible)
        self.assertNotIn("syncFromFlowTab", visible)

    def test_t1_fg1_02_index_no_google_veo(self):
        raw = _read_repo_file("index.html")
        visible = strip_html_comments(raw)
        self.assertEqual(len(re.findall(r"Google\s+Veo", visible, re.IGNORECASE)), 0)
        self.assertEqual(len(re.findall(r"\bveo\b", visible, re.IGNORECASE)), 0)

    def test_t1_fg1_03_index_no_runpod(self):
        raw = _read_repo_file("index.html")
        visible = strip_html_comments(raw)
        self.assertEqual(len(re.findall(r"\brunpod\b", visible, re.IGNORECASE)), 0)
        for forbidden in (
            "runpod-train-config",
            "wallet-runpod-badge",
            "emergencyStopAllRunpod",
            "اختيار كارت الشاشة تلقائي",
            "إيقاف وحذف جميع أجهزة RunPod المعلقة فوراً",
            "ضبط مفتاح RunPod في الخزنة",
        ):
            self.assertNotIn(forbidden, visible, f"RunPod remnant found: {forbidden}")

    def test_t1_fg1_04_post_studio_r1_clean(self):
        raw = _read_repo_file("post_studio.html")
        visible = strip_html_comments(raw)
        for pat in (r"tab-flow", r"Flow\s+Bridge", r"Google\s+Veo", r"\bveo\b", r"\brunpod\b", r"/api/runpod/", r"/api/bridge/"):
            self.assertEqual(len(re.findall(pat, visible, re.IGNORECASE)), 0, f"Forbidden R1 pattern in post_studio.html: {pat}")

    def test_t1_fg1_05_backend_r1_clean_and_no_flow_bat(self):
        self.assertFalse(
            os.path.exists(os.path.join(REPO_ROOT, "Open-Flow-Bridge-Folder.bat")),
            "Open-Flow-Bridge-Folder.bat must be removed",
        )
        srv = _read_repo_file("cindy_server.py")
        for forbidden in (
            "BRIDGE_TASKS",
            "BRIDGE_RESULTS",
            "EXTENSION_PATHS",
            "runpod_trainer",
            "run_inactivity_watchdog",
            "/api/bridge/",
            "/api/runpod/",
            "Google Veo",
            "fal-ai/veo3",
        ):
            self.assertNotIn(forbidden, srv, f"Dead R1 symbol still in cindy_server.py: {forbidden}")

    def test_t1_fg1_06_live_removed_routes_404(self):
        for path in ("/api/bridge/status", "/api/runpod/status"):
            st, _ = self.server.http_get_json(path)
            self.assertEqual(st, 404, f"GET {path} must return 404, got {st}")
        for path in ("/api/bridge/ack", "/api/runpod/train", "/api/runpod/terminate_all"):
            st, _ = self.server.http_post_json(path, {})
            self.assertEqual(st, 404, f"POST {path} must return 404, got {st}")


# =============================================================================
# FG2: R3 UI Hygiene, Deduplication & Silent Subprocess (6 tests)
# =============================================================================
class TestTier1FG2Hygiene(Tier1Base):
    def test_t1_fg2_01_index_single_post_button(self):
        visible = strip_html_comments(_read_repo_file("index.html"))
        self.assertNotIn('id="nav-main-reframe"', visible, "#nav-main-reframe duplicate button must be removed")
        post_matches = re.findall(r"<(?:button|a)\b[^>]*?(?:/post|Post-Production)[^>]*>", visible, re.IGNORECASE)
        self.assertEqual(len(post_matches), 1, f"Expected exactly 1 /post launcher in index.html, found {len(post_matches)}")

    def test_t1_fg2_02_post_studio_zero_post_buttons(self):
        visible = strip_html_comments(_read_repo_file("post_studio.html"))
        post_matches = re.findall(r"<(?:button|a)\b[^>]*?(?:window\.open\(['\"]/post|href=['\"]/post|Post-Production)[^>]*>", visible, re.IGNORECASE)
        self.assertEqual(len(post_matches), 0, f"Expected 0 /post launcher buttons in post_studio.html, found {post_matches}")
        self.assertIn('href="/"', visible)

    def test_t1_fg2_03_zero_duplicate_html_ids(self):
        for fname in ("index.html", "post_studio.html"):
            ids = extract_html_ids(_read_repo_file(fname))
            seen = {}
            dups = []
            for tag, id_val, line in ids:
                if id_val in seen:
                    dups.append(f"{id_val} (L{seen[id_val]} & L{line})")
                seen[id_val] = line
            self.assertEqual(dups, [], f"Duplicate IDs in {fname}: {dups}")

    def test_t1_fg2_04_ast_silent_subprocesses(self):
        violations = []
        for mod in RUNTIME_PY_MODULES:
            full = os.path.join(REPO_ROOT, mod)
            if os.path.isfile(full):
                violations.extend(ast_check_subprocesses(full))
        self.assertEqual(violations, [], f"Subprocess silent flag violations: {violations}")

    def test_t1_fg2_05_launcher_silent_flags(self):
        bat_path = os.path.join(REPO_ROOT, "Open-Cindy-Director.bat")
        self.assertTrue(os.path.isfile(bat_path))
        bat = _read_repo_file("Open-Cindy-Director.bat")
        self.assertNotIn("Minimized", bat, "Open-Cindy-Director.bat must not flash a minimized window")
        self.assertTrue(
            ("-WindowStyle Hidden" in bat) or ("launch_cindy_silent.vbs" in bat) or ("wscript" in bat.lower()),
            "Open-Cindy-Director.bat must launch silently",
        )
        for vbs in ("launch_cindy_silent.vbs", "launch_cindy_post.vbs"):
            if os.path.isfile(os.path.join(REPO_ROOT, vbs)):
                content = _read_repo_file(vbs)
                self.assertIn(", 0,", content, f"{vbs} must launch with window style 0 (hidden)")

    def test_t1_fg2_06_dead_ui_sections_removed(self):
        visible = strip_html_comments(_read_repo_file("index.html"))
        for dead_id in ('id="tab-reframe"', 'id="tab-vault"', 'id="local-vfx-modal"'):
            self.assertNotIn(dead_id, visible, f"Dead section {dead_id} still present in index.html")


# =============================================================================
# FG3: Static Syntax & Server Startup (5 tests)
# =============================================================================
class TestTier1FG3StaticAndStartup(Tier1Base):
    def test_t1_fg3_01_python_py_compile(self):
        for mod in RUNTIME_PY_MODULES:
            full = os.path.join(REPO_ROOT, mod)
            proc = subprocess.run(
                [sys.executable, "-m", "py_compile", full],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0, f"py_compile failed for {mod}: {proc.stderr}")

    def test_t1_fg3_02_frontend_js_node_check(self):
        for fname in ("index.html", "post_studio.html"):
            blocks = extract_inline_scripts(_read_repo_file(fname))
            self.assertGreater(len(blocks), 0)
            for line, stype, code in blocks:
                rc, stderr = run_node_check(code, is_module=(stype == "module"))
                self.assertEqual(rc, 0, f"node --check failed in {fname} script@{line}: {stderr}")

    def test_t1_fg3_03_server_startup_and_index_200(self):
        for route in ("/", "/index.html"):
            st, hdrs, raw = self.server.http_raw("GET", route)
            self.assertEqual(st, 200)
            ctype = hdrs.get("Content-Type", hdrs.get("content-type", ""))
            self.assertIn("text/html", ctype.lower())
            self.assertIn(b"VirtuFilm", raw)

    def test_t1_fg3_04_post_200_and_api_status(self):
        for route in ("/post", "/post_studio.html"):
            st, hdrs, raw = self.server.http_raw("GET", route)
            self.assertEqual(st, 200)
            ctype = hdrs.get("Content-Type", hdrs.get("content-type", ""))
            self.assertIn("text/html", ctype.lower())
            self.assertIn(b"Post-Production", raw)
        st, data = self.server.http_get_json("/api/status")
        self.assertEqual(st, 200)
        self.assertEqual(data.get("status"), "online")

    def test_t1_fg3_05_headless_browser_zero_console_errors(self):
        browser = HeadlessBrowser(stub_https=True).start()
        try:
            for route in ("/", "/post"):
                browser.navigate(f"{SERVER_URL}{route}", settle_sec=1.0)
                self.assertEqual(browser.page_exceptions, [], f"Uncaught page errors on {route}: {browser.page_exceptions}")
                self.assertEqual(browser.console_errors, [], f"Console errors on {route}: {browser.console_errors}")
        finally:
            browser.close()


# =============================================================================
# FG4: /api/upload, /api/execute, /api/generate & 4. التوليد + Parity (5 tests)
# =============================================================================
class TestTier1FG4ExecutionAndParity(Tier1Base):
    def test_t1_fg4_01_api_upload_happy_path(self):
        png_url = make_valid_png_data_url(32, 32, seed=2)
        for key in ("data_url", "data"):
            st, data = self.server.http_post_json("/api/upload", {key: png_url, "filename": f"ref_{key}.png"})
            self.assertEqual(st, 200, f"/api/upload with {key} failed: {st} {data}")
            self.assertTrue(data.get("success"), f"Expected success=True for {key}: {data}")
            url = data.get("url", "")
            self.assertTrue(url.startswith("/outputs/"), f"Unexpected upload url: {url}")
            gst, _, graw = self.server.http_raw("GET", url)
            self.assertEqual(gst, 200)
            self.assertTrue(graw.startswith(b"\x89PNG"))

    def test_t1_fg4_02_api_execute_free_modal(self):
        st, data = self.server.http_post_json(
            "/api/execute",
            {"prompt": "Wide shot of Cairo street at dusk", "model": "Modal LTX-2.5"},
        )
        self.assertEqual(st, 200, f"Free Modal LTX-2.5 should execute without user_confirmed: {st} {data}")
        self.assertTrue(data.get("success") or data.get("status") == "success")
        out_url = data.get("video_url") or data.get("url") or ""
        self.assertTrue(out_url.startswith("/outputs/"))
        gst, _, _ = self.server.http_raw("GET", out_url)
        self.assertEqual(gst, 200)

    def test_t1_fg4_03_api_execute_paid_fal_confirmed(self):
        st, data = self.server.http_post_json(
            "/api/execute",
            {"prompt": "Tracking shot through neon alley", "model": "Kling 4.0 Pro Omni", "user_confirmed": True},
        )
        self.assertEqual(st, 200, f"Confirmed Paid Fal execute failed: {st} {data}")
        self.assertTrue(data.get("success") or data.get("status") == "success")
        self.assertTrue(data.get("url") or data.get("video_url"))
        self.assertTrue(
            any("/__mock__/queue.fal.run/" in e["path"] for e in self.server.mock_ext.ledger),
            "Expected mocked Fal queue call",
        )

    def test_t1_fg4_04_gen_wing_switcher_dom(self):
        browser = HeadlessBrowser(stub_https=True).start()
        try:
            browser.navigate(f"{SERVER_URL}/", settle_sec=0.8)
            res = browser.eval_js(
                """(() => {
                    switchTab('comfy');
                    switchGenWing('paid');
                    const paidVis = !document.getElementById('gen-wing-paid-panel').classList.contains('hidden');
                    const freeHid = document.getElementById('gen-wing-modal-quick').classList.contains('hidden');
                    switchGenWing('free');
                    const freeVis = !document.getElementById('gen-wing-modal-quick').classList.contains('hidden');
                    const paidHid = document.getElementById('gen-wing-paid-panel').classList.contains('hidden');
                    return { paidVis, freeHid, freeVis, paidHid };
                })()"""
            )
            self.assertEqual(res, {"paidVis": True, "freeHid": True, "freeVis": True, "paidHid": True})
        finally:
            browser.close()

    def test_t1_fg4_05_active_model_parity_and_paid_confirm(self):
        html_src = _read_repo_file("index.html")
        srv_src = _read_repo_file("cindy_server.py")

        def _extract_opts(sel_id):
            m = re.search(rf'<select[^>]+id="{re.escape(sel_id)}"[^>]*>(.*?)</select>', html_src, re.DOTALL)
            if not m:
                return None
            return set(re.findall(r'<option[^>]+value="([^"]+)"', m.group(1)))

        top_v = _extract_opts("active-video-model")
        top_i = _extract_opts("active-image-model")
        self.assertIsNotNone(top_v)
        self.assertIsNotNone(top_i)
        scr = _extract_opts("screening-fal-model-select")
        if scr is not None:
            self.assertEqual(top_v | top_i, scr, "Top-bar video/image models must match #screening-fal-model-select")

        for modal_m in ("Modal LTX-2.5", "Modal MiniMax H3", "Modal Wan 2.2 Camera"):
            self.assertIn(modal_m, top_v, f"{modal_m} missing in #active-video-model")
            self.assertIn(f"'{modal_m}'", html_src, f"{modal_m} missing in index.html JS maps")
            self.assertIn(modal_m, srv_src, f"{modal_m} missing in cindy_server.py")

        # Verify runQuickWingGen('paid') includes user_confirmed
        m_quick = re.search(r"async function runQuickWingGen\(wing\)\s*\{(.*?)\n\s*\}", html_src, re.DOTALL)
        self.assertIsNotNone(m_quick)
        self.assertIn("user_confirmed", m_quick.group(1), "runQuickWingGen must pass user_confirmed")


# =============================================================================
# FG5: /api/reframe/process, /api/upscale/process, /api/post/* (5 tests)
# =============================================================================
class TestTier1FG5PostProduction(Tier1Base):
    def test_t1_fg5_01_upscale_local_ffmpeg(self):
        with tempfile.TemporaryDirectory() as td:
            mp4 = generate_test_mp4(os.path.join(td, "in.mp4"), duration=0.8, width=160, height=90)
            with open(mp4, "rb") as fh:
                self.server.seed_output_file("t1_upscale_src.mp4", fh.read())
        st, data = self.server.http_post_json(
            "/api/upscale/process",
            {"video_url": "/outputs/t1_upscale_src.mp4", "target_scale": "1080p", "engine": "local_ffmpeg"},
            timeout=45,
        )
        self.assertEqual(st, 200, f"Upscale failed: {st} {data}")
        url = data.get("video_url") or data.get("output_url") or ""
        self.assertTrue(url.startswith("/outputs/") and url.endswith(".mp4"), f"Unexpected upscale URL: {url}")
        gst, _, _ = self.server.http_raw("GET", url)
        self.assertEqual(gst, 200)

    def test_t1_fg5_02_reframe_smart_ambient_both_keys(self):
        with tempfile.TemporaryDirectory() as td:
            mp4 = generate_test_mp4(os.path.join(td, "in.mp4"), duration=0.8, width=320, height=180)
            with open(mp4, "rb") as fh:
                self.server.seed_output_file("t1_ref_src.mp4", fh.read())
        for ratio_key in ("target_ratio", "ratio"):
            st, data = self.server.http_post_json(
                "/api/reframe/process",
                {"video_url": "/outputs/t1_ref_src.mp4", ratio_key: "9:16", "mode": "smart_ambient"},
                timeout=45,
            )
            self.assertEqual(st, 200, f"Reframe via {ratio_key} failed: {st} {data}")
            url = data.get("video_url") or data.get("output_url") or ""
            self.assertTrue(url.endswith(".mp4"))
            out_local = os.path.join(REPO_ROOT, "outputs", os.path.basename(url))
            probe = ffprobe_inspect(out_local)
            vstream = next(s for s in probe["streams"] if s["codec_type"] == "video")
            self.assertLess(vstream["width"], vstream["height"], f"Expected 9:16 portrait when passing {ratio_key}")

    def test_t1_fg5_03_post_mux_audio_replace_and_mix_silent(self):
        with tempfile.TemporaryDirectory() as td:
            v_aud = generate_test_mp4(os.path.join(td, "va.mp4"), duration=0.8, with_audio=True)
            v_sil = generate_test_mp4(os.path.join(td, "vs.mp4"), duration=0.8, with_audio=False)
            wav = generate_test_wav(os.path.join(td, "a.wav"), duration=0.8)
            with open(v_aud, "rb") as fh:
                self.server.seed_output_file("t1_mux_va.mp4", fh.read())
            with open(v_sil, "rb") as fh:
                self.server.seed_output_file("t1_mux_vs.mp4", fh.read())
            with open(wav, "rb") as fh:
                self.server.seed_output_file("t1_mux_a.wav", fh.read())

        st1, d1 = self.server.http_post_json(
            "/api/post/mux_audio",
            {"video_file": "t1_mux_va.mp4", "audio_file": "t1_mux_a.wav", "replace_audio": True},
            timeout=30,
        )
        self.assertEqual(st1, 200, f"mux_audio replace failed: {st1} {d1}")
        st2, d2 = self.server.http_post_json(
            "/api/post/mux_audio",
            {"video_file": "t1_mux_vs.mp4", "audio_file": "t1_mux_a.wav", "replace_audio": False},
            timeout=30,
        )
        self.assertEqual(st2, 200, f"mux_audio mix on silent video failed: {st2} {d2}")

    def test_t1_fg5_04_post_merge_clips(self):
        with tempfile.TemporaryDirectory() as td:
            c1 = generate_test_mp4(os.path.join(td, "c1.mp4"), duration=0.6, color="red")
            c2 = generate_test_mp4(os.path.join(td, "c2.mp4"), duration=0.6, color="green")
            with open(c1, "rb") as fh:
                self.server.seed_output_file("t1_merge_1.mp4", fh.read())
            with open(c2, "rb") as fh:
                self.server.seed_output_file("t1_merge_2.mp4", fh.read())
        st, data = self.server.http_post_json(
            "/api/post/merge_clips",
            {"files": ["t1_merge_1.mp4", "t1_merge_2.mp4"]},
            timeout=45,
        )
        self.assertEqual(st, 200, f"merge_clips failed: {st} {data}")
        url = data.get("video_url") or data.get("output_url") or ""
        self.assertTrue(url.startswith("/outputs/") and url.endswith(".mp4"))

    def test_t1_fg5_05_post_studio_tabs_controls_and_target_ratio(self):
        post_html = _read_repo_file("post_studio.html")
        self.assertIn("target_ratio", post_html, "runPostReframe must send target_ratio")
        browser = HeadlessBrowser(stub_https=True).start()
        try:
            browser.navigate(f"{SERVER_URL}/post", settle_sec=0.8)
            res = browser.eval_js(
                """(() => {
                    switchPostTab('reframe');
                    const refVis = !document.getElementById('panel-reframe').classList.contains('hidden');
                    const ratios = Array.from(document.getElementById('post-reframe-ratio').options).map(o => o.value);
                    switchPostTab('merge');
                    const mergeVis = !document.getElementById('panel-merge').classList.contains('hidden');
                    switchPostTab('upscale');
                    const upEng = !!document.getElementById('post-upscale-engine');
                    const audSel = !!document.getElementById('post-audio-select');
                    return { refVis, ratios, mergeVis, upEng, audSel };
                })()"""
            )
            self.assertTrue(res["refVis"])
            self.assertIn("4:5", res["ratios"])
            self.assertTrue(res["mergeVis"])
            self.assertTrue(res["upEng"])
            self.assertTrue(res["audSel"])
        finally:
            browser.close()


# =============================================================================
# FG6: 3. LoRA (Fal.ai Fast API) (5 tests)
# =============================================================================
class TestTier1FG6LoraFal(Tier1Base):
    def test_t1_fg6_01_lora_ui_fal_only_and_selectors(self):
        browser = HeadlessBrowser(stub_https=True).start()
        try:
            browser.navigate(f"{SERVER_URL}/", settle_sec=0.8)
            res = browser.eval_js(
                """(() => {
                    switchTab('lora');
                    const falRadio = document.querySelector('input[name="lora-train-backend"][value="fal"]');
                    const rpRadio = document.querySelector('input[name="lora-train-backend"][value="runpod"]');
                    const hasImportCard = !!document.getElementById('lora-import-card');
                    const hasThumbs = !!document.getElementById('lora-thumbs-container');
                    const hasModeImg = !!document.getElementById('lora-mode-btn-image');
                    const hasModeVid = !!document.getElementById('lora-mode-btn-video');
                    return {
                        falChecked: !!(falRadio && falRadio.checked),
                        hasRunpodRadio: !!rpRadio,
                        hasImportCard,
                        hasThumbs,
                        hasModeImg,
                        hasModeVid,
                    };
                })()"""
            )
            self.assertTrue(res["falChecked"])
            self.assertFalse(res["hasRunpodRadio"])
            self.assertTrue(res["hasImportCard"])
            self.assertTrue(res["hasThumbs"])
            self.assertTrue(res["hasModeImg"])
            self.assertTrue(res["hasModeVid"])
        finally:
            browser.close()

    def test_t1_fg6_02_api_lora_upload(self):
        import base64
        payload_b64 = base64.b64encode(b'{"__metadata__":{"test":"lora"}}\x00' + b"\x00" * 512).decode("ascii")
        st, data = self.server.http_post_json(
            "/api/lora/upload",
            {"model_name": "HeroKarim", "trigger_word": "karim_e2e", "filename": "karim.safetensors", "data": payload_b64},
            timeout=30,
        )
        self.assertEqual(st, 200, f"/api/lora/upload failed: {st} {data}")
        self.assertTrue(data.get("success") or data.get("status") == "success")
        url = data.get("url") or data.get("cloud_url") or (data.get("lora") or {}).get("weights_url") or ""
        self.assertTrue(url)

    def test_t1_fg6_03_api_lora_train_and_job_status(self):
        imgs = [{"data": make_valid_png_data_url(64, 64, seed=i + 10)} for i in range(4)]
        st, data = self.server.http_post_json(
            "/api/lora/train",
            {"model_name": "KarimTrain", "trigger_word": "karim_tr", "steps": 500, "images": imgs, "auto_caption": True},
            timeout=30,
        )
        self.assertEqual(st, 200, f"/api/lora/train failed: {st} {data}")
        job_id = data.get("job_id")
        self.assertTrue(job_id, f"Missing job_id in train response: {data}")
        self.assertFalse(str(job_id).startswith("rp_"), f"RunPod hijack triggered: {job_id}")

        deadline = time.time() + 12.0
        final_state = ""
        while time.time() < deadline:
            jst, jdata = self.server.http_get_json(f"/api/lora/job_status?job_id={job_id}")
            if jst == 200:
                state = (jdata.get("state") or (jdata.get("job") or {}).get("status") or "").lower()
                final_state = state
                if state in ("completed", "failed"):
                    break
            time.sleep(0.5)
        self.assertEqual(final_state, "completed", f"Expected completed job status via ?job_id=, got {final_state!r}")

    def test_t1_fg6_04_api_lora_import_list_delete(self):
        st, data = self.server.http_post_json(
            "/api/lora/import",
            {
                "model_name": "ImportedHero",
                "trigger_word": "hero_imp",
                "weights_url": "https://v3b.fal.media/files/mock/hero.safetensors",
                "url": "https://v3b.fal.media/files/mock/hero.safetensors",
            },
        )
        self.assertEqual(st, 200, f"/api/lora/import failed: {st} {data}")
        lora_id = (data.get("lora") or {}).get("id")
        self.assertTrue(lora_id)

        lst_st, lst_data = self.server.http_get_json("/api/lora/list")
        self.assertEqual(lst_st, 200)
        self.assertTrue(any(l.get("id") == lora_id for l in lst_data.get("loras", [])))

        del_st, _ = self.server.http_post_json("/api/lora/delete", {"id": lora_id})
        self.assertEqual(del_st, 200)
        lst_st2, lst_data2 = self.server.http_get_json("/api/lora/list")
        self.assertEqual(lst_st2, 200)
        self.assertFalse(any(l.get("id") == lora_id for l in lst_data2.get("loras", [])))

    def test_t1_fg6_05_api_lora_execute_mocked_fal(self):
        st, data = self.server.http_post_json(
            "/api/lora/execute",
            {
                "safetensors_url": f"{self.server.mock_ext.base_url}/__mock__/v3b.fal.media/files/mock_lora.safetensors",
                "prompt": "karim_e2e standing in a sunlit studio",
                "media_type": "image",
                "aspect_ratio": "landscape_16_9",
            },
            timeout=25,
        )
        self.assertEqual(st, 200, f"/api/lora/execute failed: {st} {data}")
        self.assertTrue(data.get("url"))


# =============================================================================
# FG7: handle_chat (CHARACTER LOCK), 1. الإخراج, 2. السيناريو & FreeField (5 tests)
# =============================================================================
class TestTier1FG7ChatAndFreeField(Tier1Base):
    def test_t1_fg7_01_chat_character_lock_rules_and_reply(self):
        srv_src = _read_repo_file("cindy_server.py")
        m_chat = re.search(r"def handle_chat\(self, payload\):(.*?)(?:\n    def |\Z)", srv_src, re.DOTALL)
        self.assertIsNotNone(m_chat)
        chat_src = m_chat.group(1)
        self.assertIn("CHARACTER LOCK PROTOCOL", chat_src)
        self.assertNotIn('"4. When should you set', chat_src, "Duplicate rule '4.' must be renumbered to '6.'")

        st, data = self.server.http_post_json(
            "/api/chat",
            {
                "message": "عايزين مشهد لبطلنا Karim, 32yo Egyptian man in a navy trench coat and silver signet ring ماشي في الشارع.",
                "history": [],
            },
        )
        self.assertEqual(st, 200)
        self.assertTrue(data.get("reply"))
        self.assertTrue(data.get("character_locks") or "navy trench coat" in ((data.get("shot") or {}).get("prompt") or "").lower())

    def test_t1_fg7_02_tab1_chat_input_and_tts_toggle_dom(self):
        browser = HeadlessBrowser(stub_https=True).start()
        try:
            browser.navigate(f"{SERVER_URL}/", settle_sec=0.8)
            res = browser.eval_js(
                """(() => {
                    const inp = document.getElementById('chat-input');
                    inp.value = 'hero walking';
                    insertTagIntoPrompt('[Cinematic]');
                    const afterInsert = inp.value;
                    const beforeHtml = document.getElementById('tts-toggle-btn').innerHTML;
                    toggleVoiceOutput();
                    const afterHtml = document.getElementById('tts-toggle-btn').innerHTML;
                    return { afterInsert, changed: beforeHtml !== afterHtml };
                })()"""
            )
            self.assertIn("[Cinematic]", res["afterInsert"], "insertTagIntoPrompt must target #chat-input")
            self.assertTrue(res["changed"], "toggleVoiceOutput must update #tts-toggle-btn")
        finally:
            browser.close()

    def test_t1_fg7_03_tab2_storyboard_and_video_ref_controls(self):
        browser = HeadlessBrowser(stub_https=True).start()
        try:
            browser.navigate(f"{SERVER_URL}/", settle_sec=0.8)
            png_url = make_valid_png_data_url(16, 16, seed=3)
            res = browser.eval_js(
                f"""(() => {{
                    switchTab('storyboard');
                    const stitchBtn = document.getElementById('sb-stitch-episode-btn');
                    const stitchHidden = stitchBtn ? stitchBtn.classList.contains('hidden') : false;
                    setAsVideoReference({json.dumps(png_url)});
                    const activeVisible = !document.getElementById('video-ref-active-state').classList.contains('hidden');
                    clearVideoReference();
                    const emptyRestored = !document.getElementById('video-ref-empty-state').classList.contains('hidden');
                    return {{ stitchHidden, activeVisible, emptyRestored }};
                }})()"""
            )
            self.assertTrue(res["stitchHidden"], "#sb-stitch-episode-btn should stay hidden when no shots rendered")
            self.assertTrue(res["activeVisible"])
            self.assertTrue(res["emptyRestored"])
        finally:
            browser.close()

    def test_t1_fg7_04_freefield_404_models_noop(self):
        if REPO_ROOT not in sys.path:
            sys.path.insert(0, REPO_ROOT)
        import cindy_modal_freefield as cmf

        self.server.mock_ff.models_mode = "404"
        with mock.patch.object(cmf, "FREEFIELD_BASE", self.server.mock_ff.base_url), mock.patch.object(
            cmf, "_is_port_open", return_value=True
        ):
            cmf._ensure_pack_downloaded("upscale", wait_sec=5)
        self.assertFalse(
            any(e["path"] == "/api/models/download" for e in self.server.mock_ff.ledger),
            "404 on /api/models must be treated as Modal-managed no-op without calling download",
        )

    def test_t1_fg7_05_freefield_run_modal_video_app_success(self):
        if REPO_ROOT not in sys.path:
            sys.path.insert(0, REPO_ROOT)
        import cindy_modal_freefield as cmf

        self.server.mock_ff.models_mode = "404"
        self.server.mock_ff.run_terminal_status = "succeeded"
        with tempfile.TemporaryDirectory() as td:
            in_mp4 = generate_test_mp4(os.path.join(td, "in.mp4"), duration=0.5)
            out_mp4 = os.path.join(td, "out.mp4")
            with mock.patch.object(cmf, "FREEFIELD_BASE", self.server.mock_ff.base_url), mock.patch.object(
                cmf, "_is_port_open", return_value=True
            ):
                res_path = cmf.run_modal_video_app("upscale-video", "upscale", in_mp4, out_mp4, poll_timeout=15)
            self.assertEqual(res_path, out_mp4)
            self.assertTrue(os.path.isfile(out_mp4) and os.path.getsize(out_mp4) > 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)
