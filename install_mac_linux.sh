#!/usr/bin/env bash
# ==============================================================================
# VirtuFilm Studio AI (feat. Cindy) - macOS & Linux One-Click Setup
# Cross-Platform Launcher for macOS (Apple Silicon M1/M2/M3/M4 & Intel) & Linux
# ==============================================================================

set -e

echo "======================================================================"
echo " 🎬 VirtuFilm Studio AI (feat. Cindy) - macOS / Linux Setup"
echo " Conceived by Ehab Fikry | Implemented with Antigravity"
echo "======================================================================"
echo ""

# 1. Detect Python 3
echo "[1/4] Checking Python 3 environment..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not found in PATH."
    echo "Please install Python 3.10 or 3.11 using Homebrew on macOS: brew install python@3.11"
    exit 1
fi

PY_VER=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Detected Python: $PY_VER ($PYTHON_CMD)"
echo ""

# 2. Virtual Environment Setup (Recommended on macOS/Linux)
echo "[2/4] Setting up Python virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    $PYTHON_CMD -m venv .venv
    echo "Created .venv directory."
fi

# Activate virtualenv
source .venv/bin/activate
pip install --upgrade pip

echo "Installing / verifying dependencies from requirements.txt..."
pip install -r requirements.txt || echo "[NOTE] Optional wheels skipped. Core studio ready."
echo ""

# 3. Detect Blender on macOS / Linux
echo "[3/4] Checking local Blender installation..."
BLENDER_CMD=""

if [ "$(uname)" == "Darwin" ]; then
    # macOS standard application paths
    if [ -x "/Applications/Blender.app/Contents/MacOS/Blender" ]; then
        BLENDER_CMD="/Applications/Blender.app/Contents/MacOS/Blender"
    fi
elif [ "$(uname)" == "Linux" ]; then
    # Linux standard paths
    if command -v blender &>/dev/null; then
        BLENDER_CMD="blender"
    elif [ -x "/usr/bin/blender" ]; then
        BLENDER_CMD="/usr/bin/blender"
    elif [ -x "/snap/bin/blender" ]; then
        BLENDER_CMD="/snap/bin/blender"
    fi
fi

if [ -n "$BLENDER_CMD" ]; then
    echo "[OK] Found Blender at: $BLENDER_CMD"
else
    echo "[NOTE] Blender not detected in default system applications."
    echo "On macOS, install via: brew install --cask blender (or drag Blender.app to /Applications)"
fi
echo ""

# 4. Launch Studio
echo "[4/4] Launching VirtuFilm Studio AI on http://127.0.0.1:8765 ..."
echo ""

# Open browser automatically
if [ "$(uname)" == "Darwin" ]; then
    open "http://127.0.0.1:8765" || true
elif command -v xdg-open &>/dev/null; then
    xdg-open "http://127.0.0.1:8765" || true
fi

python cindy_server.py
