#!/usr/bin/env python3
"""
Simple keyboard bypass for JARVIS testing
"""

import time
import keyboard

def test_jarvis_response():
    """Test JARVIS TTS and command processing directly"""
    print("JARVIS Keyboard Test")
    print("Press 'h' to trigger hotword detection")
    print("Press 'q' to quit")
    
    try:
        from tts import tts
        from speech_recognition_safe import SpeechRecognition
        
        # Get the JARVIS instance
        import sys
        sys.path.append('.')
        
        while True:
            if keyboard.is_pressed('h'):
                print("Manual hotword trigger!")
                
                # Directly trigger the acknowledgment
                import random
                acknowledgments = [
                    "Yes sir?",
                    "I'm listening.",
                    "How can I help you?",
                    "At your service.",
                    "Yes?",
                    "Ready for your command.",
                    "I'm here."
                ]
                
                response = random.choice(acknowledgments)
                print(f"Speaking: {response}")
                tts.speak(response, blocking=True)
                
                # Wait for key release
                while keyboard.is_pressed('h'):
                    time.sleep(0.1)
                    
            elif keyboard.is_pressed('q'):
                break
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    
    print("Test complete")

if __name__ == "__main__":
    test_jarvis_response()
