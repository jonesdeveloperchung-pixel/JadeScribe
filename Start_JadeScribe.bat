@echo off
chcp 65001 > nul
title JadeScribe Launcher
cls

echo ========================================================
echo   JadeScribe - Intelligent Jade Cataloging
echo ========================================================
echo.

REM 1. Check for Internet & Updates
echo [1/3] Checking for updates...
git pull
if %errorlevel% neq 0 (
    echo    Warning: Update check failed. Using current version.
) else (
    echo    Application is up to date.
)
echo.

REM 2. Python Environment & Dependencies
echo [2/3] Checking system environment...

if exist ".venv\Scripts\activate.bat" (
    echo    Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo    No virtual environment found. Using system Python.
)

echo    Verifying dependencies...
pip install -r requirements.txt > nul 2>&1
if %errorlevel% neq 0 (
    echo    Error installing dependencies!
    echo    Please check your Python installation.
    pause
    exit /b
)
echo    Dependencies ready.
echo.

REM 3. Launch Application
echo [3/3] Launching JadeScribe...
echo.
echo    Target Ollama Host: http://192.168.16.120:11434
echo    (Close this window to stop the application)
echo.

set OLLAMA_HOST=http://192.168.16.120:11434

streamlit run src/app.py

if %errorlevel% neq 0 (
    echo.
    echo Application crashed or closed unexpectedly.
    pause
)
