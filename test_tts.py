#!/usr/bin/env python3
"""
Simple TTS test for JARVIS
"""

def test_tts():
    print("Testing JARVIS Text-to-Speech...")
    
    try:
        from tts import tts
        
        print("1. Testing basic TTS...")
        tts.speak("Hello, this is a TTS test. Can you hear me?", blocking=True)
        
        print("2. Testing JARVIS acknowledgment...")
        tts.speak("Yes sir? I'm listening.", blocking=True)
        
        print("3. Testing different voice...")
        tts.speak("JARVIS assistant is now active and ready for commands", blocking=True)
        
        print("TTS test complete!")
        print("Did you hear all three messages?")
        
    except Exception as e:
        print(f"Error testing TTS: {e}")

if __name__ == "__main__":
    test_tts()
