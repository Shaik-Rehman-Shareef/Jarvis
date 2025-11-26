#!/usr/bin/env python3
"""
Simple keyboard test with visual feedback
"""

import time

def test_keyboard_visual():
    print("JARVIS Keyboard Test with Visual Feedback")
    print("=" * 50)
    print("Press 'h' to trigger JARVIS hotword")
    print("You should see immediate feedback here")
    print("Press 'q' to quit")
    print()
    
    try:
        import keyboard
        
        while True:
            if keyboard.is_pressed('h'):
                print("🎯 HOTKEY DETECTED! Triggering JARVIS...")
                
                # Import and trigger directly
                try:
                    from tts import tts
                    import random
                    
                    responses = ["Yes sir?", "I'm listening.", "How can I help you?"]
                    response = random.choice(responses)
                    
                    print(f"📢 JARVIS Speaking: '{response}'")
                    tts.speak(response, blocking=True)
                    print("✅ TTS command completed")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Wait for key release
                while keyboard.is_pressed('h'):
                    time.sleep(0.1)
                print("🔄 Ready for next trigger...\n")
                    
            elif keyboard.is_pressed('q'):
                print("👋 Goodbye!")
                break
                
            time.sleep(0.1)
            
    except ImportError:
        print("❌ Keyboard module not available")
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")

if __name__ == "__main__":
    test_keyboard_visual()
