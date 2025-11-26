#!/usr/bin/env python3
"""
Vosk Model Downloader for JARVIS - Fixed Version
This script downloads and sets up the Vosk speech recognition model
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
from pathlib import Path
import ssl

def download_vosk_model():
    """Download and extract Vosk model for speech recognition"""
    print("🔊 JARVIS Vosk Model Setup (Fixed)")
    print("=" * 50)
    
    # Model details
    model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    model_dir = Path("models")
    model_zip = model_dir / "vosk-model-en-us-0.22.zip"
    model_extracted = model_dir / "vosk-model-en-us-0.22"
    
    # Create models directory
    model_dir.mkdir(exist_ok=True)
    
    # Skip if already exists
    if model_extracted.exists():
        print(f"✅ Model already exists: {model_extracted}")
        return True
    
    print(f"📥 Downloading Vosk model from: {model_url}")
    print("⚠️  This is about 50MB and may take a few minutes...")
    
    try:
        # Create SSL context that doesn't verify certificates (for download issues)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create custom opener with SSL context
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
        urllib.request.install_opener(opener)
        
        # Download with progress
        def progress_hook(count, block_size, total_size):
            if total_size > 0:
                percent = min(100, int(count * block_size * 100 / total_size))
                mb_downloaded = count * block_size / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r📥 Progress: {percent}% ({mb_downloaded:.0f}MB / {mb_total:.0f}MB)", end="", flush=True)
            else:
                mb_downloaded = count * block_size / (1024 * 1024)
                print(f"\r📥 Downloaded: {mb_downloaded:.0f}MB", end="", flush=True)
        
        urllib.request.urlretrieve(model_url, model_zip, progress_hook)
        print()  # New line after progress
        
        # Verify file was downloaded and has content
        if not model_zip.exists() or model_zip.stat().st_size < 1000000:  # Less than 1MB indicates failure
            print(f"❌ Download failed: File too small or doesn't exist")
            return False
            
        print(f"✅ Download complete: {model_zip} ({model_zip.stat().st_size / (1024*1024):.1f}MB)")
        
        # Extract the model
        print("📂 Extracting model...")
        try:
            with zipfile.ZipFile(model_zip, 'r') as zip_ref:
                zip_ref.extractall(model_dir)
            
            print(f"✅ Model extracted to: {model_extracted}")
            
            # Cleanup zip file
            model_zip.unlink()
            print("🗑️  Cleaned up zip file")
            
            return True
            
        except zipfile.BadZipFile:
            print(f"❌ Extraction failed: Downloaded file is corrupted")
            # Remove bad file
            if model_zip.exists():
                model_zip.unlink()
            return False
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        # Remove partial download
        if model_zip.exists():
            model_zip.unlink()
        return False

def install_pyaudio():
    """Install PyAudio using multiple methods"""
    print("\n🎤 Installing PyAudio...")
    print("=" * 30)
    
    try:
        import pyaudio
        print("✅ PyAudio already installed!")
        return True
    except ImportError:
        pass
    
    # Method 1: Try regular pip install
    print("📦 Trying pip install...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyAudio installed successfully!")
            return True
        else:
            print(f"⚠️  Pip install failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Pip install failed: {e}")
    
    # Method 2: Try with precompiled wheel
    print("📦 Trying with precompiled wheel...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", 
                               "PyAudio==0.2.11"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyAudio installed with precompiled wheel!")
            return True
    except Exception as e:
        print(f"⚠️  Wheel install failed: {e}")
    
    # Method 3: Try pipwin (Windows package manager)
    print("📦 Trying pipwin method...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pipwin"], 
                      capture_output=True, text=True)
        result = subprocess.run([sys.executable, "-m", "pipwin", "install", "pyaudio"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyAudio installed with pipwin!")
            return True
    except Exception as e:
        print(f"⚠️  Pipwin install failed: {e}")
    
    print("❌ PyAudio installation failed with all methods")
    print("💡 Manual installation required:")
    print("   1. Install Microsoft Visual C++ Build Tools")
    print("   2. Or download precompiled wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    return False

def test_components():
    """Test if all components are working"""
    print("\n🧪 Testing Components...")
    print("=" * 30)
    
    # Test PyAudio
    try:
        import pyaudio
        print("✅ PyAudio: OK")
    except ImportError:
        print("❌ PyAudio: Failed")
        return False
    
    # Test Vosk
    try:
        import vosk
        print("✅ Vosk: OK")
    except ImportError:
        print("❌ Vosk: Failed")
        return False
    
    # Test model exists
    model_path = Path("models/vosk-model-en-us-0.22")
    if model_path.exists():
        print("✅ Vosk Model: OK")
    else:
        print("❌ Vosk Model: Missing")
        return False
    
    # Test model loading
    try:
        model = vosk.Model(str(model_path))
        print("✅ Model Loading: OK")
        return True
    except Exception as e:
        print(f"❌ Model Loading: Failed - {e}")
        return False

def main():
    """Main setup function"""
    print("JARVIS Speech Recognition Setup")
    print("=" * 50)
    
    success = True
    
    # Step 1: Download Vosk model
    if not download_vosk_model():
        success = False
    
    # Step 2: Install PyAudio
    if not install_pyaudio():
        success = False
    
    # Step 3: Test components
    if success:
        if test_components():
            print("\n🚀 Setup complete!")
            print("Run 'python main.py' to start JARVIS")
        else:
            print("\n⚠️  Setup completed with issues")
            print("Check error messages above")
    else:
        print("\n❌ Setup failed")
        print("Check error messages above")

if __name__ == "__main__":
    main()
