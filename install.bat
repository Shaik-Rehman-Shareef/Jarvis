@echo off
echo JARVIS Desktop Assistant Installer
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found, checking version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.8+ is required
    echo Please update Python from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python version is compatible
echo.

echo [INFO] Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo [OK] Packages installed successfully
echo.

echo [INFO] Creating directories...
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "assets" mkdir assets

echo [INFO] Creating default icon...
python create_icon.py

echo.
echo [IMPORTANT] Vosk Speech Model Setup
echo ===================================
echo JARVIS needs a speech recognition model to work offline.
echo.
echo Please follow these steps:
echo 1. Go to: https://alphacephei.com/vosk/models/
echo 2. Download: vosk-model-en-us-0.22.zip (about 50MB)
echo 3. Extract the ZIP file
echo 4. Copy the extracted folder to: models/vosk-model-en-us-0.22/
echo.
echo The final path should be: models/vosk-model-en-us-0.22/am/
echo.

set /p download_choice="Would you like to open the download page now? (y/n): "
if /i "%download_choice%"=="y" (
    start https://alphacephei.com/vosk/models/
)

echo.
echo [SUCCESS] Installation completed!
echo.
echo Next steps:
echo 1. Download and setup the Vosk model (see instructions above)
echo 2. Run: python main.py
echo 3. JARVIS will appear in your system tray
echo 4. Say "Jarvis" followed by your command
echo.
echo For email functionality, right-click the system tray icon
echo and select "Configure Email"
echo.
pause
