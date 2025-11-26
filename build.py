# Build script for JARVIS Desktop Assistant
# Creates a standalone executable using PyInstaller

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build JARVIS as a standalone executable"""
    
    print("Building JARVIS Desktop Assistant...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build command
    build_cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name", "JARVIS",            # Output name
        "--icon", "assets/jarvis_icon.ico",  # Icon (if exists)
        "--add-data", "models;models",  # Include models directory
        "--add-data", "assets;assets",  # Include assets directory
        "--hidden-import", "pyttsx3.drivers",
        "--hidden-import", "pyttsx3.drivers.sapi5",
        "--hidden-import", "pyttsx3.drivers.nsss",
        "--hidden-import", "pyttsx3.drivers.espeak",
        "--hidden-import", "PIL._tkinter_finder",
        "main.py"
    ]
    
    try:
        # Clean previous build
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("JARVIS.spec"):
            os.remove("JARVIS.spec")
        
        # Run PyInstaller
        subprocess.check_call(build_cmd)
        
        print("\n✅ Build completed successfully!")
        print(f"Executable created: {os.path.abspath('dist/JARVIS.exe')}")
        print("\nTo distribute JARVIS:")
        print("1. Copy the entire 'dist' folder contents")
        print("2. Ensure Vosk model is in 'models' folder")
        print("3. Run JARVIS.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def create_installer_script():
    """Create a batch script for easy installation"""
    
    installer_script = """@echo off
echo Installing JARVIS Desktop Assistant...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Download Vosk model...
echo Please download the English model from:
echo https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
echo.
echo Extract it to: models/vosk-model-en-us-0.22/
echo.

echo Setup complete! Run 'python main.py' to start JARVIS
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_script)
    
    print("Created install.bat script")

def main():
    """Main build function"""
    
    # Ensure we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: Please run this script from the JARVIS project directory")
        return
    
    # Create directories if they don't exist
    os.makedirs("assets", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create installer script
    create_installer_script()
    
    # Ask user what to do
    print("JARVIS Build Script")
    print("==================")
    print("1. Build executable (requires all dependencies)")
    print("2. Create installer script only")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        success = build_executable()
        if not success:
            return
    
    if choice in ["2", "3"]:
        print("✅ Installer script created!")
    
    print("\n🚀 JARVIS is ready!")

if __name__ == "__main__":
    main()
