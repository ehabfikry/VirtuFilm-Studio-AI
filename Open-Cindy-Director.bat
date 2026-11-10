@echo off
cd /d "%~dp0Cindy-AI-Director"
powershell -NoProfile -Command "if (-not (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue)) { Start-Process python -ArgumentList 'cindy_server.py' -WorkingDirectory '%CD%' -WindowStyle Minimized }"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/index.html"
exit
