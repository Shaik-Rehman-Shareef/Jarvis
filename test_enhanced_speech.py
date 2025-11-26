"""
Test Enhanced Speech Recognition
Quick test to see if the enhanced speech recognition is working
"""
from speech_recognition_enhanced import enhanced_speech_recognition
from logger import logger
import time

def test_enhanced_speech():
    print("🎤 Testing Enhanced Speech Recognition")
    print("=" * 50)
    
    # Check available engines
    engines = []
    if enhanced_speech_recognition.sr_recognizer:
        engines.append("Google Speech Recognition")
    if enhanced_speech_recognition.whisper_model:
        engines.append("OpenAI Whisper")
    if enhanced_speech_recognition.model:
        engines.append("Vosk")
    
    print(f"Available engines: {', '.join(engines)}")
    print(f"Audio available: {enhanced_speech_recognition.audio_available}")
    
    if not enhanced_speech_recognition.audio_available:
        print("❌ Audio not available - cannot test")
        return
    
    print("\n🚀 Starting enhanced speech recognition...")
    print("Say 'hey' to activate JARVIS")
    print("Press Ctrl+C to stop")
    
    try:
        success = enhanced_speech_recognition.start_listening()
        if success:
            print("✅ Enhanced speech recognition started successfully!")
            print("Listening for 'hey' hotword...")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
        else:
            print("❌ Failed to start enhanced speech recognition")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping enhanced speech recognition...")
        enhanced_speech_recognition.stop_listening()
        enhanced_speech_recognition.cleanup()
        print("✅ Enhanced speech recognition stopped")

if __name__ == "__main__":
    test_enhanced_speech()
