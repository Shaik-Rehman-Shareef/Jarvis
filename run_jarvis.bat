@echo off
title JARVIS Desktop Assistant
echo Starting JARVIS Desktop Assistant...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo main.py not found in current directory
    echo Please run this from the JARVIS project folder
    pause
    exit /b 1
)

REM Start JARVIS
echo JARVIS is starting...
echo Look for the JARVIS icon in your system tray
echo Say "Jarvis" followed by your command
echo.
echo Press Ctrl+C to stop JARVIS
echo.

python main.py

echo.
echo JARVIS has stopped
pause
