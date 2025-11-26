#!/usr/bin/env python3
"""
Enhanced speech recognition setup for JARVIS
Downloads and configures better speech recognition models
"""

import os
import requests
import zipfile
import sys
from pathlib import Path

def download_file(url, local_filename):
    """Download a file with progress bar"""
    print(f"Downloading {local_filename}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        downloaded = 0
        
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)", end="", flush=True)
    print("\nDownload complete!")

def extract_zip(zip_path, extract_to):
    """Extract zip file"""
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete!")

def setup_better_vosk_model():
    """Download and setup better Vosk model"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Better Vosk models (choose based on size/accuracy trade-off)
    models = {
        "medium": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
            "name": "vosk-model-en-us-0.22",
            "size": "1.8GB",
            "description": "Large model - Best accuracy"
        },
        "small_improved": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", 
            "name": "vosk-model-small-en-us-0.15",
            "size": "40MB",
            "description": "Small model - Fast but limited"
        }
    }
    
    print("Available Vosk Models:")
    for key, model in models.items():
        print(f"{key}: {model['description']} ({model['size']})")
    
    choice = input("\nWhich model do you want? (medium/small_improved): ").strip().lower()
    
    if choice not in models:
        print("Invalid choice, using medium model")
        choice = "medium"
    
    selected_model = models[choice]
    model_path = models_dir / selected_model["name"]
    zip_path = models_dir / f"{selected_model['name']}.zip"
    
    # Check if model already exists
    if model_path.exists():
        print(f"Model {selected_model['name']} already exists!")
        return str(model_path)
    
    try:
        # Download model
        download_file(selected_model["url"], zip_path)
        
        # Extract model
        extract_zip(zip_path, models_dir)
        
        # Clean up zip file
        zip_path.unlink()
        
        print(f"✅ Successfully installed {selected_model['name']}")
        return str(model_path)
        
    except Exception as e:
        print(f"❌ Error setting up model: {e}")
        return None

def install_whisper():
    """Install OpenAI Whisper for better speech recognition"""
    try:
        print("Installing OpenAI Whisper...")
        os.system("pip install openai-whisper")
        print("✅ Whisper installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error installing Whisper: {e}")
        return False

def install_speech_recognition():
    """Install SpeechRecognition library"""
    try:
        print("Installing SpeechRecognition library...")
        os.system("pip install SpeechRecognition")
        print("✅ SpeechRecognition installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error installing SpeechRecognition: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 JARVIS Speech Recognition Enhancement Setup")
    print("=" * 50)
    
    print("\n1. Setting up better Vosk model...")
    vosk_model = setup_better_vosk_model()
    
    print("\n2. Installing additional speech recognition libraries...")
    
    install_whisper()
    install_speech_recognition()
    
    print("\n✅ Setup complete!")
    print("\nAvailable speech recognition options:")
    print("1. Enhanced Vosk (offline, good accuracy)")
    print("2. OpenAI Whisper (offline, excellent accuracy)")
    print("3. Google Speech Recognition (online, very good accuracy)")
    
    if vosk_model:
        print(f"\n🎯 Recommended: Use the enhanced Vosk model at: {vosk_model}")

if __name__ == "__main__":
    main()
