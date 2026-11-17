@echo off
chcp 65001 >nul
title Cindy-AI-Director (VirtuFilm Studio AI) - One-Click Setup
color 0B

echo ======================================================================
echo    🎬 CINDY-AI-DIRECTOR (VirtuFilm Studio AI)
echo    Directed by Ehab Fikry | Engineered with Antigravity (Google DeepMind)
echo ======================================================================
echo.
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH!
    echo Please install Python 3.10 or 3.11 from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)
echo Python environment verified.
echo.

echo [2/4] Installing / Verifying dependencies from requirements.txt...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some optional packages failed to install. Continuing with core studio...
)
echo Dependencies verified.
echo.

echo [3/4] Checking Local Blender 5.3 3D Previs Engine...
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 5.3\blender.exe
if exist "%BLENDER_PATH%" (
    echo [OK] Blender 5.3 LTS detected at: %BLENDER_PATH%
) else (
    echo [NOTE] Blender 5.3 not found in standard directory.
    echo 3D Previs will use fallback rendering or standard Blender installation.
)
echo.

echo [4/4] Launching Cindy-AI-Director Server on http://127.0.0.1:8765 ...
echo.
start "" http://127.0.0.1:8765
python cindy_server.py

pause
