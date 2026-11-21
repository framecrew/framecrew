@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3.11 -c "import sys" >nul 2>nul
    if not errorlevel 1 goto use_launcher
)
python -c "import sys; sys.exit(not ((3,11) <= sys.version_info[:2] <= (3,12)))" >nul 2>nul
if not errorlevel 1 goto use_path
set "FRAMECREW_PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if exist "%FRAMECREW_PY%" goto use_installed
where winget >nul 2>nul
if errorlevel 1 (
    echo Install Microsoft App Installer to make WinGet available, then rerun setup.
    goto failed
)
winget install --id Python.Python.3.11 --exact --source winget --scope user
if errorlevel 1 goto failed
if not exist "%FRAMECREW_PY%" (
    echo Python installation returned but its executable was not found. Open this installer again.
    goto failed
)
:use_installed
"%FRAMECREW_PY%" "%~dp0scripts\install_framecrew.py" %*
goto result
:use_launcher
py -3.11 "%~dp0scripts\install_framecrew.py" %*
goto result
:use_path
python "%~dp0scripts\install_framecrew.py" %*
:result
if not errorlevel 1 goto success
:failed
echo FrameCrew setup did not complete.
if not defined FRAMECREW_NO_PAUSE pause
exit /b 1
:success
if not defined FRAMECREW_NO_PAUSE pause
exit /b 0
