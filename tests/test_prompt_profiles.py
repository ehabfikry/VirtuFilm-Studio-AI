"""Tests for cindy_prompt_profiles (pure Python):  python -m unittest tests.test_prompt_profiles -v"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cindy_prompt_profiles import (Beat, CameraStage, ShotSpec, PROFILES, render, render_all,  # noqa: E402
                                   classify_camera_path, endpoint_to_tool_id, apply_endpoint_prompt_profile)


def make_spec(**kw):
    base = dict(
        environment="modern office with a steel desk and warm window light",
        lighting="soft key from camera left, cool rim from behind",
        cast=[{"name": "Abdelaziz", "appearance": "young man in a flowered shirt and flared jeans"},
              {"name": "Abdelshakoor", "appearance": "older man in a worn brown leather jacket", "locked_prop": "a pen"}],
        beats=[Beat(0, 2.5, "Abdelaziz", "walks toward the desk"),
               Beat(1.5, 4.5, "Abdelshakoor", "rises from his chair and smiles")],
        camera=[CameraStage(0, 2, "push_in"), CameraStage(2, 4, "orbit_left"), CameraStage(4, 5, "crane_up")],
        duration_s=5.0, has_start_frame=False, ambience="quiet office room tone",
        references=["Abdelaziz", "Abdelshakoor"])
    base.update(kw)
    return ShotSpec(**base)


class TestRender(unittest.TestCase):
    def test_every_profile_renders_nonempty(self):
        for tid, out in render_all(make_spec()).items():
            self.assertTrue(out["prompt"].strip(), tid)
            self.assertIn("evidence", out)

    def test_tools_produce_different_prompts(self):
        prompts = {t: o["prompt"] for t, o in render_all(make_spec()).items()}
        self.assertEqual(len(set(prompts.values())), len(prompts), "two tools got an identical prompt")

    def test_luma_has_no_negative_and_uses_concept_tokens(self):
        out = render(make_spec(), "LUMA_RAY2")
        self.assertIsNone(out["negative_prompt"])
        for tok in ("push_in", "orbit_left", "crane_up"):
            self.assertIn(tok, out["prompt"])
        self.assertNotRegex(out["prompt"].lower(), r"\b(avoid|no music|no logo)\b")
        self.assertTrue(any("camera moves" in w for w in out["warnings"]))   # 3 distinct > 2

    def test_kling_respects_char_cap_even_for_huge_spec(self):
        huge = make_spec(environment="a vast hall " * 400)
        out = render(huge, "KLING")
        self.assertLessEqual(out["char_count"], 2500)
        self.assertIsNotNone(out["negative_prompt"])
        self.assertEqual(out["api_params"]["cfg_scale"], 0.5)

    def test_veo_duration_snaps_and_dialogue_format(self):
        out = render(make_spec(duration_s=7, dialogue=[("Abdelaziz", "You came back.")]), "VEO3")
        self.assertEqual(out["api_params"]["duration"], "8s")
        self.assertIn('Abdelaziz: "You came back."', out["prompt"])
        self.assertIn("Audio: quiet office room tone", out["prompt"])

    def test_dialogue_dropped_with_warning_where_no_native_audio(self):
        out = render(make_spec(dialogue=[("Abdelaziz", "Hello")]), "WAN_2_2")
        self.assertNotIn("Hello", out["prompt"])
        self.assertTrue(any("dialogue dropped" in w for w in out["warnings"]))

    def test_seedance_tags_references_and_appends_inline_negatives(self):
        out = render(make_spec(), "SEEDANCE_2_5")
        self.assertIn("@Image1", out["prompt"])
        self.assertIn("@Image2", out["prompt"])
        self.assertIsNone(out["negative_prompt"])
        self.assertRegex(out["prompt"], r"- no music|- no logo|- avoid")
        self.assertEqual(out["prompt"].count("avoid jitter"), 1, "inline negatives must appear exactly once")
        self.assertLessEqual(out["word_count"], 100)

    def test_sentences_start_capitalised(self):
        for tid, out in render_all(make_spec()).items():
            body = out["prompt"].split(" - ")[0]          # inline negatives are deliberately lowercase
            if tid == "LUMA_RAY2":
                body = body.rsplit(". ", 1)[0]            # trailing camera-concept tokens are case-sensitive
            for sent in body.split(". "):
                s = sent.strip()
                if s and s[0].isalpha():
                    self.assertTrue(s[0].isupper(), f"{tid}: sentence starts lowercase: {s[:40]!r}")

    def test_ttm_describes_appearance_only(self):
        out = render(make_spec(lighting="soft key light from the left, cool rim from behind"), "TTM")
        low = out["prompt"].lower()
        for bad in ("walks", "rises", "camera", "orbit", "crane"):
            self.assertNotIn(bad, low)
        self.assertIn("Abdelaziz", out["prompt"])

    def test_wan_i2v_is_motion_only_and_short(self):
        out = render(make_spec(has_start_frame=True), "WAN_2_2")
        self.assertLessEqual(out["word_count"], 100)
        self.assertNotIn("flowered shirt", out["prompt"])     # frame already shows it
        self.assertIn("walks toward the desk", out["prompt"])

    def test_wan_t2v_trims_to_budget(self):
        long_style = ", ".join(["richly textured volumetric film look"] * 30)
        out = render(make_spec(style=long_style, lighting=long_style), "WAN_2_2")
        self.assertLessEqual(out["word_count"], 120)
        self.assertTrue(any("dropped" in w for w in out["warnings"]))

    def test_hunyuan_flags_approximated_camera_moves(self):
        out = render(make_spec(), "HUNYUAN_VIDEO")
        self.assertTrue(any("approximated" in w for w in out["warnings"]))
        self.assertIn("around left", out["prompt"])

    def test_too_many_camera_stages_for_duration_warns(self):
        spec = make_spec(duration_s=3.0)
        out = render(spec, "KLING")
        self.assertTrue(any("<2s each" in w for w in out["warnings"]))

    def test_unknown_tool_raises(self):
        with self.assertRaises(KeyError):
            render(make_spec(), "NOPE")


def path(points, fps=24.0, target=(0, 0, 1.2)):
    """Build samples from [(t, pos)] with the camera always looking at `target`."""
    out = []
    for t, pos in points:
        d = (target[0] - pos[0], target[1] - pos[1], target[2] - pos[2])
        n = math.sqrt(sum(c * c for c in d))
        out.append({"t": t, "pos": pos, "fwd": (d[0] / n, d[1] / n, d[2] / n), "target": target})
    return out


class TestCameraClassifier(unittest.TestCase):
    def test_push_in(self):
        s = path([(i * 0.25, (0, -6 + i * 0.35, 1.2)) for i in range(13)])
        self.assertEqual([c.move for c in classify_camera_path(s)], ["push_in"])

    def test_pull_out(self):
        s = path([(i * 0.25, (0, -3 - i * 0.35, 1.2)) for i in range(13)])
        self.assertEqual([c.move for c in classify_camera_path(s)], ["pull_out"])

    def test_orbit_left_is_clockwise_from_above(self):
        r = 5.0
        pts = []
        for i in range(17):
            ang = math.radians(-90 - i * 7.5)       # decreasing angle = camera moving to its left
            pts.append((i * 0.25, (r * math.cos(ang), r * math.sin(ang), 1.5)))
        self.assertEqual([c.move for c in classify_camera_path(path(pts))], ["orbit_left"])

    def test_orbit_right_mirrors(self):
        r = 5.0
        pts = []
        for i in range(17):
            ang = math.radians(-90 + i * 7.5)
            pts.append((i * 0.25, (r * math.cos(ang), r * math.sin(ang), 1.5)))
        self.assertEqual([c.move for c in classify_camera_path(path(pts))], ["orbit_right"])

    def test_crane_up(self):
        s = path([(i * 0.25, (0, -5, 1.0 + i * 0.3)) for i in range(13)])
        self.assertEqual([c.move for c in classify_camera_path(s)], ["crane_up"])

    def test_compound_dolly_then_orbit_then_crane_keeps_order(self):
        pts, t = [], 0.0
        for i in range(9):                                            # dolly in
            pts.append((t, (0, -7 + i * 0.3, 1.2))); t += 0.25
        cx, cy = 0.0, -4.6
        r0 = 4.6
        for i in range(1, 13):                                        # orbit left around origin
            ang = math.radians(-90 - i * 7.0)
            pts.append((t, (r0 * math.cos(ang), r0 * math.sin(ang), 1.2))); t += 0.25
        last = pts[-1][1]
        for i in range(1, 11):                                        # crane up
            pts.append((t, (last[0], last[1], 1.2 + i * 0.3))); t += 0.25
        moves = [c.move for c in classify_camera_path(path(pts))]
        self.assertEqual(moves, ["push_in", "orbit_left", "crane_up"])


class TestEndpointProfileMiddleware(unittest.TestCase):
    def test_luma_strips_negative_prompt_and_uses_concept_token(self):
        body = {"prompt": "Two actors face off across a desk, orbit_left", "negative_prompt": "blurry, bad hands"}
        apply_endpoint_prompt_profile("fal-ai/luma-dream-machine/ray-2/image-to-video", body, {"camera_motion": "orbit_left"})
        self.assertNotIn("negative_prompt", body)
        self.assertTrue(body["prompt"].endswith("orbit_left."))

    def test_seedance_injects_image_tags_and_inline_negatives(self):
        body = {
            "prompt": "Two men talk in an office",
            "negative_prompt": "blurry",
            "image_urls": ["https://x/a.jpg", "https://x/b.jpg"],
        }
        apply_endpoint_prompt_profile("bytedance/seedance-2.5/reference-to-video", body, {})
        self.assertNotIn("negative_prompt", body)
        self.assertIn("@Image1 and @Image2", body["prompt"])
        self.assertIn("- no music, no logo", body["prompt"])

    def test_kling_caps_2500_chars_and_adds_cfg_scale(self):
        body = {"prompt": "Cinematic confrontation in an office. " * 100}
        res = apply_endpoint_prompt_profile("fal-ai/kling-video/v3/pro/text-to-video", body, {})
        self.assertLessEqual(len(body["prompt"]), 2500)
        self.assertEqual(body["cfg_scale"], 0.5)
        self.assertIn("negative_prompt", body)
        self.assertTrue(res["warnings"])

    def test_wan_translates_camera_motion_and_sets_tailored_negative(self):
        body = {"prompt": "Actor walks toward desk, orbit_left"}
        apply_endpoint_prompt_profile("fal-ai/wan-i2v", body, {"camera_motion": "orbit_left"})
        self.assertIn("Camera: orbital arc to the left.", body["prompt"])
        self.assertIn("jittery camera", body["negative_prompt"])


class TestServerAndUiRoutingConsistency(unittest.TestCase):
    def test_ui_dropdowns_match_reference_rules_costs_and_server_endpoints(self):
        import os
        import re
        import html
        import cindy_server

        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(repo, "index.html"), "r", encoding="utf-8") as fh:
            html_src = fh.read()
        with open(os.path.join(repo, "cindy_server.py"), "r", encoding="utf-8") as fh:
            srv_src = fh.read()

        def extract_select_options(select_id):
            m = re.search(rf'<select[^>]+id="{re.escape(select_id)}"[^>]*>(.*?)</select>', html_src, re.DOTALL)
            self.assertIsNotNone(m, f"Missing <select id='{select_id}'>")
            raw_vals = re.findall(r'<option[^>]+value="([^"]+)"', m.group(1))
            return [html.unescape(v) for v in raw_vals]

        top_video_opts = extract_select_options("active-video-model")
        top_image_opts = extract_select_options("active-image-model")
        scr_all_opts = extract_select_options("screening-fal-model-select")

        # 1. Every top-bar video and image model option must exist in the screening studio dropdown (and vice versa)
        self.assertEqual(set(top_video_opts) | set(top_image_opts), set(scr_all_opts))

        # 2. Extract keys of MODEL_REFERENCE_RULES and MODEL_COST_MAP in index.html
        ref_block = re.search(r'const\s+MODEL_REFERENCE_RULES\s*=\s*\{(.*?)\n\s*\};', html_src, re.DOTALL)
        self.assertIsNotNone(ref_block)
        ref_keys = set(re.findall(r"'([^']+)'\s*:\s*\{", ref_block.group(1)))

        cost_block = re.search(r'const\s+MODEL_COST_MAP\s*=\s*\{(.*?)\n\s*\};', html_src, re.DOTALL)
        self.assertIsNotNone(cost_block)
        cost_keys = set(re.findall(r"'([^']+)'\s*:", cost_block.group(1)))

        dur_block = re.search(r'const\s+MODEL_DURATION_SPECS\s*=\s*\{(.*?)\n\s*\};', html_src, re.DOTALL)
        self.assertIsNotNone(dur_block)
        dur_keys = set(re.findall(r"'([^']+)'\s*:\s*\[", dur_block.group(1)))

        # 3. Extract keys of endpoint_mapping in cindy_server.py
        ep_block = re.search(r'endpoint_mapping\s*=\s*\{(.*?)\n\s*\}', srv_src, re.DOTALL)
        self.assertIsNotNone(ep_block)
        ep_keys = set(re.findall(r'"([^"]+)"\s*:', ep_block.group(1)))
        ep_pairs = dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', ep_block.group(1)))
        ref_cat_pairs = dict(re.findall(r"'([^']+)'\s*:\s*\{\s*category:\s*'([^']+)'", ref_block.group(1)))

        for opt in top_video_opts:
            self.assertIn(opt, dur_keys, f"Video model '{opt}' missing from MODEL_DURATION_SPECS")

        for opt in scr_all_opts:
            self.assertIn(opt, ref_keys, f"Model '{opt}' missing from MODEL_REFERENCE_RULES")
            self.assertIn(opt, cost_keys, f"Model '{opt}' missing from MODEL_COST_MAP")
            self.assertTrue(
                opt in ep_keys or opt.startswith("fal-ai/") or "/" in opt,
                f"Model '{opt}' missing from cindy_server.py endpoint_mapping"
            )
            # Ensure pure text-to-video models never map to an image-to-video endpoint by default
            if opt in top_video_opts and ref_cat_pairs.get(opt) == "text":
                mapped_ep = ep_pairs.get(opt, opt)
                self.assertNotIn(
                    "image-to-video",
                    mapped_ep,
                    f"Pure Text-to-Video model '{opt}' maps to I2V endpoint '{mapped_ep}' causing stale image hijacking",
                )

        # 4. Verify Shot Card <select id="${cardId}-model"> options are all valid and registered
        shot_card_sel = re.search(r'<select id="\$\{cardId\}-model".*?</select>', html_src, re.DOTALL)
        self.assertIsNotNone(shot_card_sel)
        shot_card_opts = re.findall(r'<option\s+value="([^"]+)"', shot_card_sel.group(0))
        self.assertGreaterEqual(len(shot_card_opts), 30)
        for s_opt in shot_card_opts:
            self.assertIn(s_opt, ref_keys, f"Shot Card model '{s_opt}' missing from MODEL_REFERENCE_RULES")
            self.assertIn(s_opt, scr_all_opts, f"Shot Card model '{s_opt}' missing from canonical studio dropdowns")

    def test_synthesize_shot_spec_and_profiles_helper(self):
        import cindy_server
        res = cindy_server.synthesize_shot_spec_and_profiles(
            previs_spec={
                "title": "Office Confrontation",
                "duration_sec": 6.0,
                "actors": [
                    {"name": "Karim", "keyframes": [{"time_sec": 0.0, "pose": "WALK"}, {"time_sec": 6.0, "pose": "STAND"}]},
                    {"name": "Nadia", "keyframes": [{"time_sec": 0.0, "pose": "SIT"}, {"time_sec": 6.0, "pose": "SIT"}]},
                ],
                "camera_beats": [
                    {"time_sec": 0.0, "framing": "MEDIUM_TWO", "lens_mm": 35.0},
                    {"time_sec": 6.0, "framing": "FACE_CLOSE_UP", "lens_mm": 50.0},
                ],
            },
            target_model="Kling 4.0 Pro Omni"
        )
        self.assertEqual(res["target_profile_id"], "KLING")
        self.assertIn("KLING", res["all_tool_prompts"])
        self.assertIn("WAN_2_2", res["all_tool_prompts"])
        self.assertIn("SEEDANCE_2_5", res["all_tool_prompts"])
        self.assertTrue(res["selected_profile"]["prompt"])

    def test_latest_previs_result_contains_depth_audit_and_all_7_profiles(self):
        import json
        import os
        import cindy_prompt_profiles as cpp
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        res_path = os.path.join(repo, "outputs", "blender_guides", "latest_previs_result.json")
        self.assertTrue(os.path.exists(res_path), "latest_previs_result.json must exist")
        with open(res_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertTrue(data.get("depth_url"), "depth_url must be non-empty")
        self.assertTrue(data.get("rgb_url"), "rgb_url must be non-empty")
        self.assertTrue(data.get("audit", {}).get("passed"), f"Previs audit did not pass: {data.get('audit')}")
        all_p = data.get("prompt_package", {}).get("all_tool_prompts", {})
        for tool_id in cpp.PROFILES:
            self.assertIn(tool_id, all_p, f"Missing tool profile {tool_id} in all_tool_prompts")
            self.assertTrue(all_p[tool_id].get("prompt"), f"Empty prompt for {tool_id}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
