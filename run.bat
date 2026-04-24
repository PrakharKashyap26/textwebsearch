@echo off
title TexWebsearch Terminal Browser

echo Starting TexWebsearch...
echo.

REM Change to script directory
cd /d %~dp0

REM Run the app
python app.py

echo.
echo Application closed.
pause