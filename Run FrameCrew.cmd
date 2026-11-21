@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run Install FrameCrew.cmd first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "scripts\install_framecrew.py" --launch
if errorlevel 1 (
    pause
    exit /b 1
)
