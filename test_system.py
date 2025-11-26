# Test script to verify JARVIS components
import os
import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    
    required_packages = [
        ('vosk', 'Speech recognition'),
        ('pyttsx3', 'Text-to-speech'),
        ('pyaudio', 'Audio input'),
        ('psutil', 'System monitoring'),
        ('pyautogui', 'System automation'),
        ('cv2', 'Camera/OpenCV'),
        ('PIL', 'Image processing'),
        ('pystray', 'System tray'),
        ('winshell', 'Windows shell integration')
    ]
    
    print("Testing JARVIS Dependencies")
    print("=" * 40)
    
    all_passed = True
    
    for package, description in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package:12} - {description}")
        except ImportError as e:
            print(f"❌ {package:12} - {description} (ERROR: {e})")
            all_passed = False
    
    return all_passed

def test_directories():
    """Test if required directories exist"""
    
    print("\nTesting Directory Structure")
    print("=" * 40)
    
    required_dirs = ['models', 'logs', 'assets']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")
            os.makedirs(directory, exist_ok=True)
            print(f"   Created {directory}/ directory")

def test_vosk_model():
    """Test if Vosk model is available"""
    
    print("\nTesting Vosk Model")
    print("=" * 40)
    
    model_path = "models/vosk-model-en-us-0.22"
    
    if os.path.exists(model_path):
        if os.path.exists(os.path.join(model_path, "am")):
            print("✅ Vosk model found and appears complete")
            return True
        else:
            print("❌ Vosk model directory exists but appears incomplete")
            return False
    else:
        print("❌ Vosk model not found")
        print("   Please download from: https://alphacephei.com/vosk/models/")
        print("   Extract to: models/vosk-model-en-us-0.22/")
        return False

def test_audio():
    """Test audio system"""
    
    print("\nTesting Audio System")
    print("=" * 40)
    
    try:
        import pyaudio
        
        # Test microphone
        audio = pyaudio.PyAudio()
        devices = audio.get_device_count()
        
        print(f"Found {devices} audio devices")
        
        # Find default input device
        try:
            default_input = audio.get_default_input_device_info()
            print(f"✅ Default microphone: {default_input['name']}")
        except:
            print("❌ No default microphone found")
        
        # Find default output device
        try:
            default_output = audio.get_default_output_device_info()
            print(f"✅ Default speaker: {default_output['name']}")
        except:
            print("❌ No default speaker found")
        
        audio.terminate()
        
    except Exception as e:
        print(f"❌ Audio system error: {e}")

def test_tts():
    """Test text-to-speech"""
    
    print("\nTesting Text-to-Speech")
    print("=" * 40)
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"✅ TTS engine initialized with {len(voices)} voices")
        
        # Test speech (uncomment to actually hear it)
        # engine.say("JARVIS text to speech test")
        # engine.runAndWait()
        
        print("✅ TTS test completed (silent)")
        
    except Exception as e:
        print(f"❌ TTS error: {e}")

def main():
    """Run all tests"""
    
    print("JARVIS Assistant - System Test")
    print("=" * 50)
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test directories
    test_directories()
    
    # Test Vosk model
    model_ok = test_vosk_model()
    
    # Test audio (only if imports are OK)
    if imports_ok:
        test_audio()
        test_tts()
    
    print("\nTest Summary")
    print("=" * 40)
    
    if imports_ok and model_ok:
        print("✅ All tests passed! JARVIS should work correctly.")
        print("\nTo start JARVIS:")
        print("   python main.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        
        if not imports_ok:
            print("\nTo install missing packages:")
            print("   pip install -r requirements.txt")
        
        if not model_ok:
            print("\nTo install Vosk model:")
            print("   Download from: https://alphacephei.com/vosk/models/")
            print("   Extract to: models/vosk-model-en-us-0.22/")

if __name__ == "__main__":
    main()
