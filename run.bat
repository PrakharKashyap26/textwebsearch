@echo off
title TexBrowse Terminal Browser

echo Starting TexBrowse...
echo.

REM Change to script directory
cd /d %~dp0

REM Run the app
python main.py

echo.
echo Application closed.
pause