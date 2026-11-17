@echo off
chcp 65001 >nul
title Cindy GitHub Community Desk - مكتب متابعة مجتمع سيندي
color 0B

echo ======================================================================
echo    CINDY GITHUB COMMUNITY DESK
echo    Director: Ehab Fikry ^| Engineered with Antigravity (Google DeepMind)
echo ======================================================================
echo.
echo جاري فتح المتصفح على مكتب المتابعة: http://127.0.0.1:8790 ...
echo.

cd /d "C:\Users\DELL\Desktop\Cindy-AI-Director"
start "" "http://127.0.0.1:8790"
python cindy_desk_server.py

pause
