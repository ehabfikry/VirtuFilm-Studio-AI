"""Opaque-box 4-tier E2E test suite for VirtuFilm AI (http://127.0.0.1:8765)."""

import os

E2E_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(E2E_DIR))
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
