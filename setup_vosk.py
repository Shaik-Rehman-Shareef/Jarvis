#!/usr/bin/env python3
"""
Vosk Model Downloader for JARVIS
This script downloads and sets up the Vosk speech recognition model
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

def download_vosk_model():
    """Download and extract the Vosk model"""
    
    print("🔊 JARVIS Vosk Model Setup")
    print("=" * 40)
    
    # Model information
    model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    model_name = "vosk-model-en-us-0.22"
    models_dir = Path("models")
    model_path = models_dir / model_name
    zip_path = models_dir / f"{model_name}.zip"
    
    # Create models directory
    models_dir.mkdir(exist_ok=True)
    
    # Check if model already exists
    if model_path.exists():
        print(f"✅ Model already exists at: {model_path}")
        return True
    
    print(f"📥 Downloading Vosk model from: {model_url}")
    print("⚠️  This is about 50MB and may take a few minutes...")
    
    try:
        # Download the model
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r📥 Progress: {progress:.1f}% ({downloaded // 1024 // 1024}MB)", end='')
        
        print(f"\n✅ Download complete: {zip_path}")
        
        # Extract the model
        print("📂 Extracting model...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)
        
        print(f"✅ Model extracted to: {model_path}")
        
        # Clean up zip file
        zip_path.unlink()
        print("🗑️  Cleaned up zip file")
        
        # Verify extraction
        if model_path.exists() and (model_path / "am").exists():
            print("✅ Model verification successful!")
            return True
        else:
            print("❌ Model verification failed!")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Download failed: {e}")
        return False
    except zipfile.BadZipFile as e:
        print(f"❌ Extraction failed: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def install_pyaudio():
    """Try to install PyAudio using different methods"""
    
    print("\n🎤 Installing PyAudio...")
    
    import subprocess
    
    # Method 1: Try pip install
    try:
        print("📦 Trying pip install...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyAudio installed successfully!")
            return True
    except Exception as e:
        print(f"❌ Pip install failed: {e}")
    
    # Method 2: Try PyAudio-binaries
    try:
        print("📦 Trying PyAudio-binaries...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "PyAudio-binaries"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyAudio-binaries installed successfully!")
            return True
    except Exception as e:
        print(f"❌ PyAudio-binaries install failed: {e}")
    
    # Method 3: Manual instructions
    print("❌ Automatic PyAudio installation failed.")
    print("\n📋 Manual Installation Instructions:")
    print("1. Download Microsoft C++ Build Tools from:")
    print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print("2. Install the build tools")
    print("3. Run: pip install pyaudio")
    print("\nOR download a pre-compiled wheel from:")
    print("https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    
    return False

def test_installation():
    """Test if everything is working"""
    
    print("\n🧪 Testing Installation...")
    
    # Test Vosk
    try:
        import vosk
        model_path = Path("models/vosk-model-en-us-0.22")
        if model_path.exists():
            model = vosk.Model(str(model_path))
            print("✅ Vosk model loaded successfully!")
        else:
            print("❌ Vosk model not found!")
            return False
    except Exception as e:
        print(f"❌ Vosk test failed: {e}")
        return False
    
    # Test PyAudio
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        audio.terminate()
        print(f"✅ PyAudio working! Found {device_count} audio devices.")
    except Exception as e:
        print(f"❌ PyAudio test failed: {e}")
        return False
    
    # Test TTS
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ Text-to-speech working!")
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False
    
    print("\n🎉 All components working! JARVIS is ready!")
    return True

def main():
    """Main setup function"""
    
    print("JARVIS Speech Recognition Setup")
    print("=" * 50)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    success = True
    
    # Download Vosk model
    if not download_vosk_model():
        success = False
    
    # Install PyAudio
    if not install_pyaudio():
        success = False
    
    # Test everything
    if success:
        test_installation()
    
    print("\n🚀 Setup complete!")
    print("Run 'python main.py' to start JARVIS")

if __name__ == "__main__":
    main()
