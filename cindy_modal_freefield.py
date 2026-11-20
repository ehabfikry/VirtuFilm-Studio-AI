import os
import time
import json
import shutil
import socket
import subprocess
import urllib.request
import urllib.error
import mimetypes
import uuid


FREEFIELD_BASE = "http://127.0.0.1:4173"
FREEFIELD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "FreeField")


def _silent_subprocess_kwargs():
    if os.name == "nt":
        return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    return {}


def _is_port_open(port=4173):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.0):
            return True
    except Exception:
        return False


def ensure_freefield_running(timeout_sec=20):
    """Starts FreeField local bridge silently (no console window) if not already running."""
    if _is_port_open(4173):
        return True
    if not os.path.isdir(FREEFIELD_DIR):
        raise RuntimeError("مجلد FreeField غير موجود في tools/FreeField")

    env = os.environ.copy()
    env["CI"] = "1"
    env["PORT"] = "4173"
    env["FREEFIELD_HOST"] = "127.0.0.1"

    node_exe = shutil.which("node")
    server_ts = os.path.join(FREEFIELD_DIR, "server", "server.ts")
    if node_exe and os.path.isfile(server_ts):
        cmd = [
            node_exe,
            "--env-file-if-exists=.env",
            "--experimental-strip-types",
            "--disable-warning=ExperimentalWarning",
            "server/server.ts",
        ]
    else:
        cmd = ["npm.cmd", "run", "serve"]

    proc = subprocess.Popen(
        cmd,
        cwd=FREEFIELD_DIR,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **_silent_subprocess_kwargs(),
    )
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if _is_port_open(4173):
            return True
        if proc.poll() is not None:
            raise RuntimeError(f"تعذر تشغيل جسر Modal (FreeField) — انتهى الخادم مبكراً (رمز {proc.returncode})")
        time.sleep(0.5)
    raise RuntimeError("تعذر تشغيل جسر Modal (FreeField) على المنفذ 4173")


def _http_json(method, path, payload=None, timeout=30):
    url = f"{FREEFIELD_BASE}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _post_multipart(path, fields, files_map, timeout=180):
    """files_map: dict of {field_name: file_path}"""
    boundary = f"----CindyModalBoundary{uuid.uuid4().hex}"
    body_parts = []
    for k, v in (fields or {}).items():
        if v is None:
            continue
        body_parts.append(f"--{boundary}\r\n".encode("utf-8"))
        body_parts.append(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
        body_parts.append(f"{v}\r\n".encode("utf-8"))

    for file_field, file_path in (files_map or {}).items():
        if not file_path or not os.path.isfile(file_path):
            continue
        filename = os.path.basename(file_path)
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        body_parts.append(f"--{boundary}\r\n".encode("utf-8"))
        body_parts.append(
            f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode("utf-8")
        )
        body_parts.append(f"Content-Type: {mime}\r\n\r\n".encode("utf-8"))
        body_parts.append(file_bytes)
        body_parts.append(b"\r\n")

    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(body_parts)
    req = urllib.request.Request(
        f"{FREEFIELD_BASE}{path}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(raw)
        except Exception:
            err_json = {"error": raw}
        return e.code, err_json


def _extract_pack_needs(models_info, pack_name):
    needs = models_info.get("needs") or {}
    pack_apps = models_info.get("pack_apps") or {}
    app_ids = set(pack_apps.get(pack_name) or [])
    relevant = []
    for app_id, need in needs.items():
        if isinstance(need, dict) and (app_id in app_ids or need.get("pack") == pack_name):
            relevant.append(need)
    packs = models_info.get("packs") or {}
    pack_state = packs.get(pack_name) or {}
    raw_missing = pack_state.get("missing") if isinstance(pack_state, dict) else 0
    if isinstance(raw_missing, list):
        missing_count = len(raw_missing)
    else:
        try:
            missing_count = int(raw_missing or 0)
        except (TypeError, ValueError):
            missing_count = 0
    return relevant, missing_count


def _ensure_pack_downloaded(pack_name, wait_sec=300):
    """Checks if a Modal/FreeField model pack is ready; treats HTTP 404 as Modal-managed no-op."""
    try:
        models_info = _http_json("GET", "/api/models", timeout=20)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return
        return
    except Exception:
        return

    relevant, missing_count = _extract_pack_needs(models_info, pack_name)
    for need in relevant:
        kind = need.get("kind")
        if kind in ("token", "license", "failed"):
            detail = need.get("error") or ", ".join(need.get("repos") or []) or kind
            raise RuntimeError(f"تعذر تجهيز حزمة '{pack_name}' على FreeField ({kind}): {detail}")

    has_pack_need = any(n.get("kind") == "pack" for n in relevant)
    is_downloading = any(n.get("kind") == "downloading" for n in relevant)
    if not has_pack_need and not is_downloading and missing_count <= 0:
        return

    if has_pack_need or (missing_count > 0 and not is_downloading):
        print(f"[Cindy Modal] Pack '{pack_name}' missing {missing_count} file(s). Triggering download...")
        _http_json("POST", "/api/models/download", {"packs": [pack_name]}, timeout=30)

    deadline = time.time() + wait_sec
    while time.time() < deadline:
        time.sleep(3)
        try:
            st = _http_json("GET", "/api/models", timeout=20)
            rel_now, miss_now = _extract_pack_needs(st, pack_name)
            for need in rel_now:
                kind = need.get("kind")
                if kind in ("token", "license", "failed"):
                    detail = need.get("error") or ", ".join(need.get("repos") or []) or kind
                    raise RuntimeError(f"فشل تحميل حزمة '{pack_name}' ({kind}): {detail}")
            if not rel_now and miss_now <= 0:
                print(f"[Cindy Modal] Pack '{pack_name}' is ready on Modal Volume.")
                return
        except RuntimeError:
            raise
        except Exception:
            pass
    raise RuntimeError(f"جاري تحميل موديلات '{pack_name}' على سيرفر Modal لأول مرة — حاول مرة أخرى بعد دقيقتين.")


def run_modal_video_app(app_id, pack_name, input_video_path, output_video_path, extra_fields=None, extra_files=None, poll_timeout=600):
    """
    Runs a FreeField video app ('upscale-video', 'reframe', 'recast', 'relight', 'speak', etc.) on Modal L40S GPU
    and saves the resulting MP4 directly to output_video_path.
    """
    ensure_freefield_running()
    if pack_name:
        _ensure_pack_downloaded(pack_name)

    files_map = {}
    if input_video_path:
        files_map["clip"] = input_video_path
    if extra_files:
        files_map.update(extra_files)

    status, resp = _post_multipart(
        f"/api/apps/{app_id}/run",
        fields=extra_fields or {},
        files_map=files_map,
    )
    if status >= 400:
        err_msg = resp.get("error") or resp.get("message") or str(resp)
        raise RuntimeError(f"Modal ({app_id}) رفض الطلب ({status}): {err_msg}")

    run_id = resp.get("id") or resp.get("runId")
    if not run_id:
        raise RuntimeError(f"لم يرجع Modal معرف مهمة صالح: {resp}")

    deadline = time.time() + poll_timeout
    consecutive_errors = 0
    while time.time() < deadline:
        time.sleep(3)
        try:
            hist = _http_json("GET", f"/api/history/{run_id}", timeout=20)
            consecutive_errors = 0
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise RuntimeError(f"المهمة غير موجودة على Modal ({app_id}): {run_id}")
            consecutive_errors += 1
            if consecutive_errors >= 5:
                raise RuntimeError(f"تعذر متابعة حالة Modal ({app_id}): HTTP {e.code}")
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            consecutive_errors += 1
            if consecutive_errors >= 5:
                raise RuntimeError(f"انقطع الاتصال أثناء متابعة Modal ({app_id}): {e}")
            continue

        state = (hist.get("status") or hist.get("state") or "").lower()
        if state in ("done", "completed", "succeeded", "success"):
            outputs = hist.get("outputs") or []
            if not outputs:
                raise RuntimeError("انتهت المعالجة على Modal لكن لم يتم العثور على ملف فيديو ناتج.")
            out_item = outputs[0]
            out_url = out_item.get("url")
            if not out_url:
                fname = out_item.get("file") or out_item.get("name")
                out_url = f"/api/history/{run_id}/files/{fname}"
            if out_url.startswith("/"):
                out_url = f"{FREEFIELD_BASE}{out_url}"

            os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)
            with urllib.request.urlopen(out_url, timeout=180) as dl, open(output_video_path, "wb") as f_out:
                while True:
                    chunk = dl.read(1024 * 1024)
                    if not chunk:
                        break
                    f_out.write(chunk)
            return output_video_path

        if state in ("failed", "error", "cancelled", "canceled", "expired", "lost"):
            raw_err = hist.get("error")
            if isinstance(raw_err, dict):
                err = raw_err.get("message") or json.dumps(raw_err, ensure_ascii=False)
            elif raw_err:
                err = str(raw_err)
            else:
                err = f"انتهت المهمة بحالة ({state})"
            raise RuntimeError(f"فشل التشغيل على Modal ({app_id}): {err}")

    raise RuntimeError(f"انتهى وقت الانتظار للمعالجة على Modal ({app_id}).")
