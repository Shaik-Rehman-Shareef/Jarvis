#!/usr/bin/env python3
"""
Simple Vosk Model Downloader for JARVIS
Downloads the small English model directly
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
from pathlib import Path
import ssl

def download_small_vosk_model():
    """Download and extract small Vosk model for speech recognition"""
    print("🔊 JARVIS Vosk Model Setup (Small Model)")
    print("=" * 50)
    
    # Use smaller model URL - this is the correct 50MB model
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_dir = Path("models")
    model_zip = model_dir / "vosk-model-small-en-us-0.15.zip"
    model_extracted = model_dir / "vosk-model-small-en-us-0.15"
    
    # Create models directory
    model_dir.mkdir(exist_ok=True)
    
    # Skip if already exists
    if model_extracted.exists():
        print(f"✅ Model already exists: {model_extracted}")
        return True
    
    print(f"📥 Downloading small Vosk model from: {model_url}")
    print("⚠️  This is about 40MB and should download quickly...")
    
    try:
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create custom opener with SSL context
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
        urllib.request.install_opener(opener)
        
        # Download with progress
        def progress_hook(count, block_size, total_size):
            if total_size > 0 and total_size < 100000000:  # Only show progress for files < 100MB
                percent = min(100, int(count * block_size * 100 / total_size))
                mb_downloaded = count * block_size / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r📥 Progress: {percent}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)", end="", flush=True)
            else:
                mb_downloaded = count * block_size / (1024 * 1024)
                print(f"\r📥 Downloaded: {mb_downloaded:.1f}MB", end="", flush=True)
        
        urllib.request.urlretrieve(model_url, model_zip, progress_hook)
        print()  # New line after progress
        
        # Verify file was downloaded and has reasonable content
        if not model_zip.exists() or model_zip.stat().st_size < 10000000:  # Less than 10MB indicates failure
            print(f"❌ Download failed: File too small ({model_zip.stat().st_size / (1024*1024):.1f}MB)")
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
    
    # Test model exists (check for small model)
    model_path = Path("models/vosk-model-small-en-us-0.15")
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
    print("JARVIS Speech Recognition Setup (Small Model)")
    print("=" * 60)
    
    success = True
    
    # Step 1: Download small Vosk model
    if not download_small_vosk_model():
        success = False
    
    # Step 2: Test components
    if success:
        if test_components():
            print("\n🚀 Setup complete!")
            print("Run 'python main.py' to start JARVIS")
            print("Note: Using small model for faster performance")
        else:
            print("\n⚠️  Setup completed with issues")
            print("Check error messages above")
    else:
        print("\n❌ Setup failed")
        print("Check error messages above")

if __name__ == "__main__":
    main()
