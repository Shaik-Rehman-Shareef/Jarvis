# Quick Setup Script for JARVIS
# Run this script to set up your JARVIS environment

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing JARVIS requirements...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_icon():
    """Create default icon"""
    try:
        subprocess.check_call([sys.executable, "create_icon.py"])
        print("✅ Icon created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create icon: {e}")
        return False

def main():
    print("JARVIS Quick Setup")
    print("=" * 30)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create icon
    create_icon()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Download Vosk model: https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
    print("2. Extract to: models/vosk-model-en-us-0.22/")
    print("3. Run: python test_system.py (to test everything)")
    print("4. Run: python main.py (to start JARVIS)")

if __name__ == "__main__":
    main()
