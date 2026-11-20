"""Shared E2E test helpers: isolated server lifecycle, mock external/FreeField servers,
FFmpeg fixture generators, AST/HTML/Node static checkers, and pure-stdlib CDP headless browser."""

import ast
import atexit
import base64
import hashlib
import html.parser
import http.server
import json
import os
import re
import shutil
import socket
import socketserver
import struct
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib

from tests.e2e import REPO_ROOT, SERVER_HOST, SERVER_PORT, SERVER_URL

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0

RUNTIME_PY_MODULES = [
    "cindy_server.py",
    "cindy_modal_freefield.py",
    "cindy_reframe_engine.py",
    "cindy_storyboard.py",
    "cindy_previs_engine.py",
    "cindy_blender_bridge.py",
]

DEFAULT_DUMMY_SECRETS = {
    "fal_api_key": "fal_test_e2e_dummy_key_000000",
    "gemini_api_key": "gemini_test_e2e_dummy_key_000000",
}

_ACTIVE_MANAGERS = set()


def _cleanup_all_managers():
    for mgr in list(_ACTIVE_MANAGERS):
        try:
            mgr.stop()
        except Exception:
            pass


atexit.register(_cleanup_all_managers)


def is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def make_valid_png_bytes(width: int = 64, height: int = 64, seed: int = 1) -> bytes:
    """Generate a valid RGB PNG whose compressed IDAT size varies with seed."""
    rows = []
    for y in range(height):
        row = bytearray([0])  # filter type 0
        for x in range(width):
            r = (x * 13 + y * 7 + seed * 37) & 0xFF
            g = (x * 5 + y * 19 + seed * 53) & 0xFF
            b = (x * 23 + y * 11 + seed * 71) & 0xFF
            row.extend((r, g, b))
        rows.append(bytes(row))
    raw_scanlines = b"".join(rows)
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat_data = zlib.compress(raw_scanlines, level=6)

    def _chunk(ctype: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(ctype + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + ctype + payload + struct.pack(">I", crc)

    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr_data) + _chunk(b"IDAT", idat_data) + _chunk(b"IEND", b"")


def make_valid_png_data_url(width: int = 64, height: int = 64, seed: int = 1) -> str:
    raw = make_valid_png_bytes(width=width, height=height, seed=seed)
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def generate_test_mp4(
    out_path: str,
    duration: float = 1.0,
    width: int = 320,
    height: int = 180,
    with_audio: bool = True,
    color: str = "blue",
) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s={width}x{height}:d={duration}:r=10",
    ]
    if with_audio:
        cmd.extend(["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"])
    cmd.extend(["-t", str(duration), "-c:v", "libx264", "-pix_fmt", "yuv420p"])
    if with_audio:
        cmd.extend(["-c:a", "aac", "-shortest"])
    else:
        cmd.append("-an")
    cmd.append(out_path)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=CREATE_NO_WINDOW,
        timeout=30,
    )
    if proc.returncode != 0 or not os.path.isfile(out_path):
        raise RuntimeError(f"ffmpeg failed generating {out_path}: {proc.stderr[-300:]}")
    return out_path


def generate_test_wav(out_path: str, duration: float = 1.0, freq: int = 440) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={freq}:duration={duration}",
        "-ar",
        "44100",
        "-ac",
        "1",
        out_path,
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=CREATE_NO_WINDOW,
        timeout=30,
    )
    if proc.returncode != 0 or not os.path.isfile(out_path):
        raise RuntimeError(f"ffmpeg failed generating wav {out_path}: {proc.stderr[-300:]}")
    return out_path


def ffprobe_inspect(media_path: str) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height",
        "-of",
        "json",
        media_path,
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=CREATE_NO_WINDOW,
        timeout=20,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {media_path}: {proc.stderr[-300:]}")
    return json.loads(proc.stdout)


def strip_html_comments(html_text: str) -> str:
    return re.sub(r"<!--.*?-->", "", html_text, flags=re.DOTALL)


class _IDParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.ids = []
        self._raw_depth = 0

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in ("script", "style"):
            self._raw_depth += 1
        if self._raw_depth <= (1 if t in ("script", "style") else 0):
            for k, v in attrs:
                if k and k.lower() == "id" and v is not None:
                    self.ids.append((t, v, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style") and self._raw_depth > 0:
            self._raw_depth -= 1


def extract_html_ids(html_text: str):
    parser = _IDParser()
    parser.feed(html_text)
    parser.close()
    return parser.ids


class _ScriptParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self._in_script = False
        self._is_external = False
        self._script_type = ""
        self._start_line = 0
        self._chunks = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            attr_map = {k.lower(): (v or "") for k, v in attrs if k}
            self._in_script = True
            self._is_external = "src" in attr_map and bool(attr_map["src"].strip())
            self._script_type = attr_map.get("type", "").strip().lower()
            self._start_line = self.getpos()[0]
            self._chunks = []

    def handle_data(self, data):
        if self._in_script and not self._is_external:
            self._chunks.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._in_script:
            if not self._is_external and self._script_type in ("", "text/javascript", "application/javascript", "module"):
                code = "".join(self._chunks)
                if code.strip():
                    self.scripts.append((self._start_line, self._script_type, code))
            self._in_script = False
            self._chunks = []


def extract_inline_scripts(html_text: str):
    parser = _ScriptParser()
    parser.feed(html_text)
    parser.close()
    return parser.scripts


def run_node_check(js_code: str, is_module: bool = False):
    suffix = ".mjs" if is_module else ".js"
    tf = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=suffix, delete=False)
    try:
        tf.write(js_code)
        tf.close()
        proc = subprocess.run(
            ["node", "--check", tf.name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATE_NO_WINDOW,
            timeout=20,
        )
        return proc.returncode, proc.stderr.strip()
    finally:
        try:
            os.unlink(tf.name)
        except OSError:
            pass


def ast_check_subprocesses(py_path: str):
    """Return list of subprocess call violations (missing creationflags / silent kwargs)."""
    with open(py_path, "r", encoding="utf-8") as fh:
        src = fh.read()
    tree = ast.parse(src, filename=py_path)
    has_create_no_window = ("CREATE_NO_WINDOW" in src) or ("0x08000000" in src)
    violations = []
    targets = {"Popen", "run", "call", "check_output", "check_call"}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_subproc = (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "subprocess"
            and func.attr in targets
        )
        if not is_subproc:
            continue
        has_kw = any(kw.arg == "creationflags" for kw in node.keywords)
        has_silent_unpack = any(
            kw.arg is None
            and isinstance(kw.value, ast.Call)
            and isinstance(kw.value.func, ast.Name)
            and "silent" in kw.value.func.id.lower()
            for kw in node.keywords
        )
        has_silent_var = any(
            kw.arg is None
            and isinstance(kw.value, ast.Name)
            and "silent" in kw.value.id.lower()
            for kw in node.keywords
        )
        if not (has_kw or has_silent_unpack or has_silent_var):
            violations.append(f"{os.path.basename(py_path)}:{node.lineno} subprocess.{func.attr} lacks creationflags")
    if violations and not has_create_no_window:
        violations.append(f"{os.path.basename(py_path)}: missing CREATE_NO_WINDOW")
    elif not has_create_no_window:
        # Check if any subprocess calls exist at all
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr in targets
            ):
                violations.append(f"{os.path.basename(py_path)}: subprocess calls present without CREATE_NO_WINDOW")
                break
    return violations


class _QuietThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        import sys
        _, exc, _ = sys.exc_info()
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError)):
            return
        super().handle_error(request, client_address)


class MockExternalServer:
    """Ephemeral localhost mock server for Fal.ai, Gemini, and blocked external hosts."""

    def __init__(self, tmp_media_dir: str):
        self.tmp_media_dir = tmp_media_dir
        self._lock = threading.Lock()
        self._counter = 0
        self._req_endpoints = {}
        self.ledger = []
        self.config = {}
        self.reset_config()

        self._png_bytes = make_valid_png_bytes(64, 64, seed=7)
        self._mp4_path = os.path.join(tmp_media_dir, "mock_ext_sample.mp4")
        generate_test_mp4(self._mp4_path, duration=0.5, width=160, height=120, with_audio=True, color="navy")
        with open(self._mp4_path, "rb") as fh:
            self._mp4_bytes = fh.read()
        self._safetensors_bytes = b'{"__metadata__":{"e2e":"mock"}}\x00' + (b"\x00" * 512)
        self._glb_bytes = b"glTF\x02\x00\x00\x00" + (b"\x00" * 128)

        parent = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format, *args):
                return

            def _send(self, code: int, content_type: str, raw: bytes):
                self.send_response(code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _send_json(self, code: int, obj: dict):
                self._send(code, "application/json; charset=utf-8", json.dumps(obj).encode("utf-8"))

            def _read_body(self) -> bytes:
                cl = int(self.headers.get("Content-Length", "0") or "0")
                return self.rfile.read(cl) if cl > 0 else b""

            def _record(self, method: str, body: bytes):
                parsed_json = None
                if body:
                    try:
                        parsed_json = json.loads(body.decode("utf-8", errors="replace"))
                    except Exception:
                        parsed_json = None
                with parent._lock:
                    parent.ledger.append(
                        {
                            "method": method,
                            "path": self.path,
                            "host": self.headers.get("X-Mock-Host", ""),
                            "body_json": parsed_json,
                            "body_len": len(body),
                        }
                    )

            def do_PUT(self):
                body = self._read_body()
                self._record("PUT", body)
                self._send_json(200, {"ok": True})

            def do_GET(self):
                self._record("GET", b"")
                parsed = urllib.parse.urlparse(self.path)
                p = parsed.path
                base = parent.base_url

                if p == "/__mock__/fal.run/fal-ai/flux/schnell":
                    self._send_json(parent.config["fal_key_status"], {"ok": parent.config["fal_key_status"] == 200})
                    return

                if p == "/__mock__/rest.alpha.fal.ai/users/current":
                    self._send_json(200, {"balance": 42.50, "currency": "USD"})
                    return

                if p.startswith("/__mock__/api.fal.ai/v1/models/pricing"):
                    self._send_json(200, {"prices": [{"unit_price": 0.05, "unit": "second"}]})
                    return

                if p == "/__mock__/generativelanguage.googleapis.com/v1beta/models":
                    self._send_json(200, {"models": [{"name": "models/gemini-3.5-flash"}]})
                    return

                if p.startswith("/__mock__/queue.fal.run/status/"):
                    if parent.config["fal_queue_status"] == "FAILED":
                        self._send_json(200, {"status": "FAILED", "error": parent.config["fal_fail_error"]})
                    else:
                        self._send_json(
                            200,
                            {
                                "status": "COMPLETED",
                                "logs": [{"message": "Mock Fal training/gen step 100%"}],
                            },
                        )
                    return

                if p.startswith("/__mock__/queue.fal.run/result/"):
                    req_id = p.rsplit("/", 1)[-1]
                    ep = parent._req_endpoints.get(req_id, "").lower()
                    if "flux-lora-fast-training" in ep or "lora" in ep and "train" in ep:
                        self._send_json(
                            200,
                            {
                                "diffusers_lora_file": {
                                    "url": f"{base}/__mock__/v3b.fal.media/files/mock_lora.safetensors",
                                    "file_size": len(parent._safetensors_bytes),
                                }
                            },
                        )
                    elif "flux-lora" in ep:
                        self._send_json(
                            200,
                            {"images": [{"url": f"{base}/__mock__/v3b.fal.media/files/mock_lora_img.png"}]},
                        )
                    elif "image-to-3d" in ep or "tripo" in ep:
                        self._send_json(
                            200,
                            {"model_file": {"url": f"{base}/__mock__/v3b.fal.media/files/mock_actor.glb"}},
                        )
                    else:
                        self._send_json(
                            200,
                            {"video": {"url": f"{base}/__mock__/v3b.fal.media/files/mock_video.mp4"}},
                        )
                    return

                if p.startswith("/__mock__/v3b.fal.media/files/") or p.startswith("/__mock__/fal.media/files/"):
                    if p.endswith(".png"):
                        self._send(200, "image/png", parent._png_bytes)
                    elif p.endswith(".mp4"):
                        self._send(200, "video/mp4", parent._mp4_bytes)
                    elif p.endswith(".safetensors"):
                        self._send(200, "application/octet-stream", parent._safetensors_bytes)
                    elif p.endswith(".glb"):
                        self._send(200, "model/gltf-binary", parent._glb_bytes)
                    else:
                        self._send(200, "application/octet-stream", b"MOCK_BYTES")
                    return

                self._send_json(200, {"ok": True, "mock_path": p})

            def do_POST(self):
                body = self._read_body()
                self._record("POST", body)
                parsed = urllib.parse.urlparse(self.path)
                p = parsed.path
                base = parent.base_url

                if p.startswith("/__mock__/rest.alpha.fal.ai/storage/upload/initiate"):
                    with parent._lock:
                        parent._counter += 1
                        idx = parent._counter
                    self._send_json(
                        200,
                        {
                            "upload_url": f"{base}/__mock__/upload_bin/asset_{idx}",
                            "file_url": f"{base}/__mock__/v3b.fal.media/files/mock_asset_{idx}.bin",
                        },
                    )
                    return

                if p.startswith("/__mock__/queue.fal.run/"):
                    ep = p[len("/__mock__/queue.fal.run/") :]
                    with parent._lock:
                        parent._counter += 1
                        req_id = f"mock_req_{parent._counter}"
                        parent._req_endpoints[req_id] = ep
                    self._send_json(
                        200,
                        {
                            "request_id": req_id,
                            "status_url": f"{base}/__mock__/queue.fal.run/status/{req_id}",
                            "response_url": f"{base}/__mock__/queue.fal.run/result/{req_id}",
                        },
                    )
                    return

                if p.startswith("/__mock__/fal.run/"):
                    if "any-llm" in p:
                        self._send_json(200, {"output": "Cinematic wide shot, warm tungsten lighting."})
                    else:
                        self._send_json(
                            200,
                            {"images": [{"url": f"{base}/__mock__/v3b.fal.media/files/mock_img.png"}]},
                        )
                    return

                if p.startswith("/__mock__/generativelanguage.googleapis.com/"):
                    if parent.config["gemini_status"] != 200:
                        self._send_json(parent.config["gemini_status"], {"error": {"message": "Mock Gemini error"}})
                        return
                    try:
                        req_obj = json.loads(body.decode("utf-8", errors="replace"))
                    except Exception:
                        req_obj = {}
                    gen_cfg = req_obj.get("generationConfig") or {}
                    if gen_cfg.get("responseMimeType") == "application/json":
                        all_text = []
                        sys_parts = (req_obj.get("systemInstruction") or {}).get("parts") or []
                        for sp in sys_parts:
                            if sp.get("text"):
                                all_text.append(sp["text"])
                        for msg in req_obj.get("contents") or []:
                            for pt in msg.get("parts") or []:
                                if pt.get("text"):
                                    all_text.append(pt["text"])
                        joined = "\n".join(all_text)
                        # Preserve any established character lock description across turns
                        lock_desc = ""
                        for marker in (
                            "Karim, 32yo Egyptian man in a navy trench coat and silver signet ring",
                            "navy trench coat",
                            "green scarf",
                            "scarred cheek",
                        ):
                            if marker.lower() in joined.lower():
                                lock_desc = (
                                    "Karim, 32yo Egyptian man in a navy trench coat and silver signet ring"
                                    if "navy trench coat" in joined.lower()
                                    else marker
                                )
                                break
                        base_prompt = (
                            f"{lock_desc}, 35mm anamorphic film still, dramatic noir lighting"
                            if lock_desc
                            else "Egyptian film director on rainy Cairo street, 35mm lens, tungsten streetlamp"
                        )
                        cindy_json = {
                            "reply": "تمام يا أستاذنا المخرج، ثبتنا ملامح الشخصية وزاوية الكاميرا جاهزة للتنفيذ.",
                            "should_render_previs": True,
                            "previs_spec": {
                                "title": "Mock E2E Scene",
                                "duration_sec": 5.0,
                                "fps": 24,
                                "environment": {"type": "street", "has_lamp_post": True},
                                "actors": [
                                    {
                                        "id": "actor_1",
                                        "name": "Karim",
                                        "keyframes": [
                                            {"time_sec": 0.0, "pos": [0.0, -1.0, 0.0], "pose": "STAND"},
                                            {"time_sec": 5.0, "pos": [0.0, 0.5, 0.0], "pose": "WALK"},
                                        ],
                                    }
                                ],
                                "camera_beats": [
                                    {"time_sec": 0.0, "framing": "MEDIUM_TWO", "lens_mm": 35, "transition": "SMOOTH"},
                                    {"time_sec": 5.0, "framing": "FACE_CLOSE_UP", "lens_mm": 50, "transition": "SMOOTH"},
                                ],
                            },
                            "has_shot": True,
                            "shot": {
                                "title": "لقطة الشارع الممطر",
                                "notes": "قفل الشخصية محفوظ",
                                "prompt": base_prompt,
                                "suggested_model": "Modal LTX-2.5",
                                "mode": "video",
                            },
                            "voice_text": "ثبتنا الشخصية والكادر جاهز.",
                        }
                        if lock_desc:
                            cindy_json["character_locks"] = {"Karim": lock_desc}
                        payload_text = json.dumps(cindy_json, ensure_ascii=False)
                    else:
                        payload_text = "e2e_actor, photorealistic cinematic portrait, 35mm lens"

                    self._send_json(
                        200,
                        {"candidates": [{"content": {"parts": [{"text": payload_text}]}}]},
                    )
                    return

                self._send_json(200, {"ok": True})

        self.server = _QuietThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

    def reset_config(self):
        self.config = {
            "fal_key_status": 200,
            "fal_queue_status": "COMPLETED",
            "fal_fail_error": "Mocked Fal queue failure",
            "gemini_status": 200,
        }

    def clear_ledger(self):
        with self._lock:
            self.ledger.clear()

    def stop(self):
        try:
            self.server.shutdown()
            self.server.server_close()
        except Exception:
            pass


class MockFreeFieldServer:
    """Ephemeral localhost mock server mimicking tools/FreeField API."""

    def __init__(self, tmp_media_dir: str):
        self._lock = threading.Lock()
        self._counter = 0
        self.ledger = []
        self.packs_downloaded = []
        self.models_mode = "404"  # '404' | 'needs_pack' | 'ready'
        self.run_terminal_status = "succeeded"  # 'succeeded' | 'failed' | 'expired' | 'lost'
        self.run_error = "Mock FreeField failure"

        self._mp4_path = os.path.join(tmp_media_dir, "mock_ff_out.mp4")
        generate_test_mp4(self._mp4_path, duration=0.5, width=160, height=120, with_audio=True, color="green")
        with open(self._mp4_path, "rb") as fh:
            self._mp4_bytes = fh.read()

        parent = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format, *args):
                return

            def _send(self, code: int, ctype: str, raw: bytes):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _send_json(self, code: int, obj: dict):
                self._send(code, "application/json; charset=utf-8", json.dumps(obj).encode("utf-8"))

            def _read_body(self) -> bytes:
                cl = int(self.headers.get("Content-Length", "0") or "0")
                return self.rfile.read(cl) if cl > 0 else b""

            def do_GET(self):
                with parent._lock:
                    parent.ledger.append({"method": "GET", "path": self.path})
                if self.path == "/api/models":
                    if parent.models_mode == "404":
                        self._send_json(404, {"error": "this backend does not download its own models"})
                    elif parent.models_mode == "needs_pack":
                        self._send_json(
                            200,
                            {
                                "available": True,
                                "alwaysOn": True,
                                "packs": {"upscale": {"gb": 1.2, "missing": 1, "missing_gb": 1.2}},
                                "needs": {"upscale-video": {"kind": "pack", "pack": "upscale", "gb": 1.2}},
                                "pack_apps": {"upscale": ["upscale-video"]},
                            },
                        )
                    else:
                        self._send_json(200, {"available": True, "packs": {}, "needs": {}, "pack_apps": {}})
                    return

                if self.path.startswith("/api/history/") and "/files/" in self.path:
                    self._send(200, "video/mp4", parent._mp4_bytes)
                    return

                if self.path.startswith("/api/history/"):
                    run_id = self.path.rsplit("/", 1)[-1]
                    st = parent.run_terminal_status
                    if st == "succeeded":
                        self._send_json(
                            200,
                            {
                                "id": run_id,
                                "status": "succeeded",
                                "error": None,
                                "outputs": [
                                    {
                                        "id": "out1",
                                        "name": "out.mp4",
                                        "type": "video",
                                        "url": f"/api/history/{run_id}/files/out.mp4",
                                    }
                                ],
                            },
                        )
                    else:
                        self._send_json(
                            200,
                            {
                                "id": run_id,
                                "status": st,
                                "error": parent.run_error,
                                "outputs": [],
                            },
                        )
                    return

                self._send_json(404, {"error": "not found"})

            def do_POST(self):
                body = self._read_body()
                with parent._lock:
                    parent.ledger.append({"method": "POST", "path": self.path, "body_len": len(body)})
                if self.path == "/api/models/download":
                    try:
                        data = json.loads(body.decode("utf-8", errors="replace"))
                        parent.packs_downloaded.extend(data.get("packs") or [])
                    except Exception:
                        pass
                    parent.models_mode = "ready"
                    self._send_json(200, {"started": True})
                    return

                if self.path.startswith("/api/apps/") and self.path.endswith("/run"):
                    with parent._lock:
                        parent._counter += 1
                        run_id = f"mock_ff_run_{parent._counter}"
                    self._send_json(202, {"id": run_id, "status": "queued"})
                    return

                self._send_json(404, {"error": "not found"})

        self.server = _QuietThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

    def reset_config(self):
        self.models_mode = "404"
        self.run_terminal_status = "succeeded"
        self.run_error = "Mock FreeField failure"
        self.packs_downloaded.clear()

    def clear_ledger(self):
        with self._lock:
            self.ledger.clear()

    def stop(self):
        try:
            self.server.shutdown()
            self.server.server_close()
        except Exception:
            pass


_SITECUSTOMIZE_CODE = r'''
import builtins
import io
import os
import socket
import subprocess
import urllib.parse
import urllib.request

_STATE_DIR = os.environ["CINDY_TEST_STATE_DIR"]
_REPO_ROOT = os.environ["CINDY_TEST_REPO_ROOT"]
_MOCK_EXT = os.environ["CINDY_TEST_MOCK_EXTERNAL_URL"].rstrip("/")
_MOCK_FF = os.environ["CINDY_TEST_MOCK_FREEFIELD_URL"].rstrip("/")
_MOCK_FF_PORT = int(os.environ["CINDY_TEST_MOCK_FREEFIELD_PORT"])

_REDIRECT_MAP = {}
for _rel, _dst in [
    ("cindy_secrets.json", "cindy_secrets.json"),
    ("cindy_loras.json", "cindy_loras.json"),
    ("daily_pricing_cache.json", "daily_pricing_cache.json"),
    ("IP_MANIFEST_SHA256.json", "IP_MANIFEST_SHA256.json"),
    ("IP_TIMESTAMP_RECORD.txt", "IP_TIMESTAMP_RECORD.txt"),
    ("bridge_debug.jsonl", "bridge_debug.jsonl"),
    (os.path.join("outputs", "user_preferences.json"), "user_preferences.json"),
    (os.path.join("outputs", "scripts_storyboard.json"), "scripts_storyboard.json"),
    (os.path.join("outputs", "cinema_radar_cache.json"), "cinema_radar_cache.json"),
    (os.path.join("outputs", "character_locks.json"), "character_locks.json"),
    (os.path.join("outputs", "blender_guides", "current_previs_spec.json"), "current_previs_spec.json"),
]:
    _REDIRECT_MAP[os.path.normcase(os.path.abspath(os.path.join(_REPO_ROOT, _rel)))] = os.path.join(_STATE_DIR, _dst)


def _remap_path(p):
    if isinstance(p, (str, bytes, os.PathLike)):
        try:
            sp = os.fspath(p)
            if isinstance(sp, bytes):
                return p
            norm = os.path.normcase(os.path.abspath(sp))
            if norm in _REDIRECT_MAP:
                return _REDIRECT_MAP[norm]
        except Exception:
            pass
    return p


_orig_open = builtins.open
def _patched_open(file, *args, **kwargs):
    return _orig_open(_remap_path(file), *args, **kwargs)
builtins.open = _patched_open
io.open = _patched_open

_orig_exists = os.path.exists
def _patched_exists(path):
    return _orig_exists(_remap_path(path))
os.path.exists = _patched_exists

_orig_isfile = os.path.isfile
def _patched_isfile(path):
    return _orig_isfile(_remap_path(path))
os.path.isfile = _patched_isfile

_orig_remove = os.remove
def _patched_remove(path, *args, **kwargs):
    return _orig_remove(_remap_path(path), *args, **kwargs)
os.remove = _patched_remove

_orig_stat = os.stat
def _patched_stat(path, *args, **kwargs):
    return _orig_stat(_remap_path(path), *args, **kwargs)
os.stat = _patched_stat

_orig_sub_run = subprocess.run
def _patched_sub_run(cmd, *args, **kwargs):
    try:
        if isinstance(cmd, (list, tuple)) and cmd and str(cmd[0]).lower() == "icacls":
            return subprocess.CompletedProcess(cmd, 0, stdout=b"", stderr=b"")
    except Exception:
        pass
    return _orig_sub_run(cmd, *args, **kwargs)
subprocess.run = _patched_sub_run

_MOCK_HOSTS = {
    "fal.run",
    "queue.fal.run",
    "rest.alpha.fal.ai",
    "api.fal.ai",
    "v3b.fal.media",
    "fal.media",
    "generativelanguage.googleapis.com",
    "api.runpod.io",
    "api.tripo3d.ai",
    "openrouter.ai",
    "synon.co.jp",
    "api.github.com",
    "huggingface.co",
    "api.mymemory.translated.net",
}

def _rewrite_external_url(url):
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    if host in ("127.0.0.1", "localhost", "::1"):
        if parsed.port == 4173:
            q = f"?{parsed.query}" if parsed.query else ""
            return f"{_MOCK_FF}{parsed.path}{q}", None
        return url, None
    if host in _MOCK_HOSTS:
        q = f"?{parsed.query}" if parsed.query else ""
        return f"{_MOCK_EXT}/__mock__/{parsed.netloc}{parsed.path}{q}", parsed.netloc
    raise RuntimeError(f"E2E Network Firewall blocked outbound call to: {url}")

try:
    import requests
    _orig_req = requests.Session.request
    def _patched_req(self, method, url, *args, **kwargs):
        new_url, orig_host = _rewrite_external_url(str(url))
        if orig_host:
            hdrs = dict(kwargs.get("headers") or {})
            hdrs["X-Mock-Host"] = orig_host
            kwargs["headers"] = hdrs
        return _orig_req(self, method, new_url, *args, **kwargs)
    requests.Session.request = _patched_req
except ImportError:
    pass

_orig_urlopen = urllib.request.urlopen
def _patched_urlopen(url, *args, **kwargs):
    if isinstance(url, urllib.request.Request):
        new_url, orig_host = _rewrite_external_url(url.full_url)
        if new_url != url.full_url:
            hdrs = dict(url.header_items())
            if orig_host:
                hdrs["X-Mock-Host"] = orig_host
            url = urllib.request.Request(new_url, data=url.data, headers=hdrs, method=url.get_method())
    else:
        new_url, _ = _rewrite_external_url(str(url))
        url = new_url
    return _orig_urlopen(url, *args, **kwargs)
urllib.request.urlopen = _patched_urlopen

_orig_create_conn = socket.create_connection
def _patched_create_conn(address, *args, **kwargs):
    host, port = address[0], address[1]
    if str(host).lower() in ("127.0.0.1", "localhost") and int(port) == 4173:
        address = ("127.0.0.1", _MOCK_FF_PORT)
    return _orig_create_conn(address, *args, **kwargs)
socket.create_connection = _patched_create_conn
'''


class IsolatedServerManager:
    """Runs real cindy_server.py on 127.0.0.1:8765 in full isolation."""

    def __init__(self):
        self.tmp_root = tempfile.mkdtemp(prefix="cindy_e2e_")
        self.state_dir = os.path.join(self.tmp_root, "state")
        self.shim_dir = os.path.join(self.tmp_root, "shim")
        self.media_dir = os.path.join(self.tmp_root, "media")
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.shim_dir, exist_ok=True)
        os.makedirs(self.media_dir, exist_ok=True)

        self.mock_ext = MockExternalServer(self.media_dir)
        self.mock_ff = MockFreeFieldServer(self.media_dir)
        self.proc = None
        self._log_fh = None
        self._outputs_snapshot = set()
        self._started = False

    def _seed_state(self):
        self.write_secrets(DEFAULT_DUMMY_SECRETS)
        self.reset_loras()
        pricing_cache = {
            "timestamp": time.time(),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fal_models": [{"name": f"Mock Model {i}", "price": "$0.10"} for i in range(25)],
            "runpod_gpus": [],
        }
        with open(os.path.join(self.state_dir, "daily_pricing_cache.json"), "w", encoding="utf-8") as fh:
            json.dump(pricing_cache, fh)

    def write_secrets(self, secrets_dict: dict):
        with open(os.path.join(self.state_dir, "cindy_secrets.json"), "w", encoding="utf-8") as fh:
            json.dump(secrets_dict, fh)

    def reset_loras(self):
        with open(os.path.join(self.state_dir, "cindy_loras.json"), "w", encoding="utf-8") as fh:
            json.dump([], fh)

    def clear_previs_spec(self):
        sp = os.path.join(self.state_dir, "current_previs_spec.json")
        if os.path.isfile(sp):
            try:
                os.remove(sp)
            except OSError:
                pass

    def _snapshot_outputs(self) -> set:
        out_root = os.path.join(REPO_ROOT, "outputs")
        snap = set()
        if os.path.isdir(out_root):
            for root, _, files in os.walk(out_root):
                for fn in files:
                    rel = os.path.relpath(os.path.join(root, fn), out_root)
                    snap.add(rel)
        return snap

    def _clean_outputs_diff(self):
        if not self._started:
            return
        out_root = os.path.join(REPO_ROOT, "outputs")
        if not os.path.isdir(out_root):
            return
        for root, dirs, files in os.walk(out_root, topdown=False):
            for fn in files:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, out_root)
                if rel not in self._outputs_snapshot:
                    try:
                        os.remove(full)
                    except OSError:
                        pass

    def start(self, timeout_sec: float = 15.0):
        if is_port_open(SERVER_PORT, SERVER_HOST, timeout=0.5):
            raise RuntimeError(
                f"Port {SERVER_HOST}:{SERVER_PORT} is already occupied before E2E startup. "
                "Stop existing server on 8765 before running E2E tests."
            )
        self._seed_state()
        self._outputs_snapshot = self._snapshot_outputs()

        with open(os.path.join(self.shim_dir, "sitecustomize.py"), "w", encoding="utf-8") as fh:
            fh.write(_SITECUSTOMIZE_CODE)

        env = os.environ.copy()
        prev_pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = self.shim_dir + (os.pathsep + prev_pp if prev_pp else "")
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["CINDY_TEST_STATE_DIR"] = self.state_dir
        env["CINDY_TEST_REPO_ROOT"] = REPO_ROOT
        env["CINDY_TEST_MOCK_EXTERNAL_URL"] = self.mock_ext.base_url
        env["CINDY_TEST_MOCK_FREEFIELD_URL"] = self.mock_ff.base_url
        env["CINDY_TEST_MOCK_FREEFIELD_PORT"] = str(self.mock_ff.port)

        log_path = os.path.join(self.tmp_root, "server.log")
        self._log_fh = open(log_path, "w", encoding="utf-8", errors="replace")
        self._started = True
        _ACTIVE_MANAGERS.add(self)

        import sys
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(REPO_ROOT, "cindy_server.py")],
            cwd=REPO_ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=self._log_fh,
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW,
        )

        deadline = time.time() + timeout_sec
        last_err = None
        while time.time() < deadline:
            if self.proc.poll() is not None:
                self._log_fh.flush()
                with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
                    log_tail = lf.read()[-1000:]
                raise RuntimeError(f"cindy_server.py exited early (rc={self.proc.returncode}):\n{log_tail}")
            try:
                status, _, body = self.http_raw("GET", "/api/status", timeout=2.0)
                if status == 200:
                    data = json.loads(body.decode("utf-8", errors="replace"))
                    if data.get("status") == "online":
                        return
            except Exception as exc:
                last_err = exc
            time.sleep(0.2)
        raise RuntimeError(f"Timed out waiting for {SERVER_URL}/api/status: {last_err}")

    def read_server_log(self) -> str:
        log_path = os.path.join(self.tmp_root, "server.log")
        if os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
                return fh.read()
        return ""

    def stop(self):
        _ACTIVE_MANAGERS.discard(self)
        if self.proc is not None:
            if self.proc.poll() is None:
                try:
                    self.proc.terminate()
                    self.proc.wait(timeout=5)
                except Exception:
                    try:
                        if os.name == "nt":
                            subprocess.run(
                                ["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                                capture_output=True,
                                creationflags=CREATE_NO_WINDOW,
                                timeout=5,
                            )
                        else:
                            self.proc.kill()
                        self.proc.wait(timeout=3)
                    except Exception:
                        pass
            self.proc = None

        deadline = time.time() + 5.0
        while time.time() < deadline and is_port_open(SERVER_PORT, SERVER_HOST, timeout=0.2):
            time.sleep(0.1)

        if self._log_fh is not None:
            try:
                self._log_fh.close()
            except Exception:
                pass
            self._log_fh = None

        self.mock_ext.stop()
        self.mock_ff.stop()
        self._clean_outputs_diff()
        shutil.rmtree(self.tmp_root, ignore_errors=True)

    def http_raw(self, method: str, path: str, body: bytes = b"", headers: dict = None, timeout: float = 30.0):
        url = f"{SERVER_URL}{path}"
        hdrs = dict(headers or {})
        req = urllib.request.Request(url, data=body if method != "GET" else None, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as err:
            return err.code, dict(err.headers or {}), err.read()

    def http_get_json(self, path: str, headers: dict = None, timeout: float = 15.0):
        st, hdrs, raw = self.http_raw("GET", path, headers=headers, timeout=timeout)
        try:
            return st, json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            return st, {"_raw": raw.decode("utf-8", errors="replace")}

    def http_post_json(self, path: str, payload: dict, headers: dict = None, timeout: float = 30.0):
        hdrs = {"Content-Type": "application/json"}
        if headers:
            hdrs.update(headers)
        raw_req = json.dumps(payload).encode("utf-8")
        st, _, raw_resp = self.http_raw("POST", path, body=raw_req, headers=hdrs, timeout=timeout)
        try:
            return st, json.loads(raw_resp.decode("utf-8", errors="replace"))
        except Exception:
            return st, {"_raw": raw_resp.decode("utf-8", errors="replace")}

    def seed_output_file(self, filename: str, content_bytes: bytes) -> str:
        out_dir = os.path.join(REPO_ROOT, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        dest = os.path.join(out_dir, os.path.basename(filename))
        with open(dest, "wb") as fh:
            fh.write(content_bytes)
        return dest


def find_headless_browser() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    raise RuntimeError("Neither Chrome nor Edge headless browser executable was found.")


class StdlibWS:
    """Minimal pure-Python RFC6455 WebSocket client for Chrome DevTools Protocol."""

    def __init__(self, ws_url: str, timeout: float = 15.0):
        parsed = urllib.parse.urlparse(ws_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 80
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)

        key = base64.b64encode(os.urandom(16)).decode("ascii")
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        self.sock.sendall(handshake)

        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("WebSocket handshake closed unexpectedly")
            buf += chunk
        header_end = buf.index(b"\r\n\r\n") + 4
        hdr = buf[:header_end].decode("latin1")
        if "101" not in hdr.splitlines()[0]:
            raise RuntimeError(f"WebSocket upgrade rejected: {hdr.splitlines()[0]}")
        self._rx_buf = buf[header_end:]

    def _recv_exact(self, n: int) -> bytes:
        while len(self._rx_buf) < n:
            chunk = self.sock.recv(max(4096, n - len(self._rx_buf)))
            if not chunk:
                raise RuntimeError("WebSocket connection closed while reading")
            self._rx_buf += chunk
        out = self._rx_buf[:n]
        self._rx_buf = self._rx_buf[n:]
        return out

    def _send_frame(self, opcode: int, payload: bytes):
        mask = os.urandom(4)
        length = len(payload)
        hdr = bytearray([0x80 | opcode])
        if length < 126:
            hdr.append(0x80 | length)
        elif length < 65536:
            hdr.append(0x80 | 126)
            hdr.extend(struct.pack("!H", length))
        else:
            hdr.append(0x80 | 127)
            hdr.extend(struct.pack("!Q", length))
        hdr.extend(mask)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(hdr) + masked)

    def send_text(self, text: str):
        self._send_frame(0x1, text.encode("utf-8"))

    def recv_text(self) -> str:
        fragments = []
        while True:
            b1, b2 = self._recv_exact(2)
            fin = (b1 & 0x80) != 0
            opcode = b1 & 0x0F
            masked = (b2 & 0x80) != 0
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8))[0]
            mask_key = self._recv_exact(4) if masked else b""
            payload = self._recv_exact(length)
            if masked:
                payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))

            if opcode == 0x8:  # Close
                raise RuntimeError("WebSocket closed by browser")
            if opcode == 0x9:  # Ping
                self._send_frame(0xA, payload)
                continue
            if opcode == 0xA:  # Pong
                continue
            fragments.append(payload)
            if fin:
                return b"".join(fragments).decode("utf-8", errors="replace")

    def close(self):
        try:
            self._send_frame(0x8, b"")
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass


class HeadlessBrowser:
    """Silent Chrome/Edge headless CDP controller with https://* interception and clean teardown."""

    def __init__(self, stub_https: bool = True):
        self.exe = find_headless_browser()
        self.udd = tempfile.mkdtemp(prefix="cindy_cdp_")
        self.stub_https = stub_https
        self.proc = None
        self.ws = None
        self._msg_id = 0
        self.console_errors = []
        self.console_messages = []
        self.page_exceptions = []
        self.external_requests = []
        self._load_fired = False

    def start(self, timeout: float = 15.0):
        self.proc = subprocess.Popen(
            [
                self.exe,
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-background-networking",
                "--remote-debugging-port=0",
                f"--user-data-dir={self.udd}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
        )

        port_file = os.path.join(self.udd, "DevToolsActivePort")
        dbg_port = None
        deadline = time.time() + timeout
        while time.time() < deadline:
            if os.path.isfile(port_file):
                try:
                    with open(port_file, "r", encoding="utf-8") as fh:
                        lines = [ln.strip() for ln in fh.read().splitlines() if ln.strip()]
                    if lines and lines[0].isdigit():
                        dbg_port = int(lines[0])
                        break
                except OSError:
                    pass
            time.sleep(0.05)
        if not dbg_port:
            raise RuntimeError("Headless browser failed to write DevToolsActivePort")

        ws_url = None
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{dbg_port}/json/list", timeout=2.0) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))
                page = next((t for t in targets if t.get("type") == "page" and t.get("webSocketDebuggerUrl")), None)
                if page:
                    ws_url = page["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.05)
        if not ws_url:
            raise RuntimeError("No CDP page target found")

        self.ws = StdlibWS(ws_url, timeout=15.0)
        self.call("Runtime.enable")
        self.call("Page.enable")
        if self.stub_https:
            self.call("Fetch.enable", {"patterns": [{"urlPattern": "https://*"}]})
        return self

    def _handle_event(self, evt: dict):
        method = evt.get("method", "")
        params = evt.get("params") or {}

        if method == "Fetch.requestPaused":
            req_id = params.get("requestId")
            url = (params.get("request") or {}).get("url", "")
            self.external_requests.append(url)
            if "cdn.tailwindcss.com" in url:
                body_str = "window.tailwind = window.tailwind || { config: {} };"
                ctype = "application/javascript"
            elif url.endswith(".css") or "fonts.googleapis.com" in url:
                body_str = "/* stub */"
                ctype = "text/css"
            elif url.endswith(".js") or url.endswith(".mjs"):
                body_str = "/* stub */"
                ctype = "application/javascript"
            else:
                body_str = ""
                ctype = "text/plain"
            self._send_raw(
                "Fetch.fulfillRequest",
                {
                    "requestId": req_id,
                    "responseCode": 200,
                    "responseHeaders": [{"name": "Content-Type", "value": ctype}],
                    "body": base64.b64encode(body_str.encode("utf-8")).decode("ascii"),
                },
            )
        elif method == "Page.javascriptDialogOpening":
            self._send_raw("Page.handleJavaScriptDialog", {"accept": True})
        elif method == "Page.loadEventFired":
            self._load_fired = True
        elif method == "Runtime.consoleAPICalled":
            ctype = params.get("type", "")
            args = params.get("args") or []
            msg = " ".join(str(a.get("value", a.get("description", ""))) for a in args)
            self.console_messages.append((ctype, msg))
            if ctype == "error":
                self.console_errors.append(msg)
        elif method == "Runtime.exceptionThrown":
            det = params.get("exceptionDetails") or {}
            exc_obj = det.get("exception") or {}
            text = exc_obj.get("description") or det.get("text") or str(det)
            self.page_exceptions.append(text)

    def _send_raw(self, method: str, params: dict = None) -> int:
        self._msg_id += 1
        mid = self._msg_id
        self.ws.send_text(json.dumps({"id": mid, "method": method, "params": params or {}}))
        return mid

    def call(self, method: str, params: dict = None, timeout: float = 15.0):
        target_id = self._send_raw(method, params)
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = self.ws.recv_text()
            msg = json.loads(raw)
            if "id" in msg:
                # Ignore fire-and-forget internal replies (Fetch.fulfillRequest etc.) until target_id arrives
                if msg["id"] == target_id:
                    if "error" in msg:
                        raise RuntimeError(f"CDP error for {method}: {msg['error']}")
                    return msg.get("result") or {}
            else:
                self._handle_event(msg)
        raise TimeoutError(f"CDP call {method} timed out after {timeout}s")

    def pump(self, duration_sec: float = 0.5):
        deadline = time.time() + duration_sec
        orig_timeout = self.ws.sock.gettimeout()
        try:
            while time.time() < deadline:
                rem = max(0.05, deadline - time.time())
                self.ws.sock.settimeout(min(0.15, rem))
                try:
                    raw = self.ws.recv_text()
                except socket.timeout:
                    continue
                msg = json.loads(raw)
                if "method" in msg:
                    self._handle_event(msg)
        finally:
            self.ws.sock.settimeout(orig_timeout)

    def navigate(self, url: str, settle_sec: float = 1.0, timeout: float = 15.0):
        self._load_fired = False
        self.console_errors.clear()
        self.page_exceptions.clear()
        self.call("Page.navigate", {"url": url}, timeout=timeout)
        deadline = time.time() + timeout
        while not self._load_fired and time.time() < deadline:
            self.pump(0.15)
        self.pump(settle_sec)

    def eval_js(self, expression: str, await_promise: bool = True, timeout: float = 15.0):
        res = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
            },
            timeout=timeout,
        )
        if "exceptionDetails" in res:
            det = res["exceptionDetails"]
            desc = (det.get("exception") or {}).get("description") or det.get("text") or str(det)
            raise RuntimeError(f"JS exception during eval: {desc}")
        return (res.get("result") or {}).get("value")

    def close(self):
        if self.ws is not None:
            self.ws.close()
            self.ws = None
        if self.proc is not None:
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                        capture_output=True,
                        creationflags=CREATE_NO_WINDOW,
                        timeout=5,
                    )
                else:
                    self.proc.kill()
                self.proc.wait(timeout=3)
            except Exception:
                pass
            self.proc = None
        shutil.rmtree(self.udd, ignore_errors=True)
