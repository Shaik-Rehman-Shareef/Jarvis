#!/usr/bin/env python3
"""
Quick audio output test for JARVIS TTS troubleshooting
"""

import pyttsx3
import time

def test_audio_output():
    """Test audio output with different settings"""
    print("Testing JARVIS Audio Output...")
    print("=" * 40)
    
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices)}")
        for i, voice in enumerate(voices):
            print(f"  Voice {i}: {voice.name} - {voice.id}")
        
        # Test different volume levels
        volumes = [0.5, 0.8, 1.0]
        rates = [150, 200, 250]
        
        for volume in volumes:
            for rate in rates:
                print(f"\nTesting Volume: {volume}, Rate: {rate}")
                engine.setProperty('volume', volume)
                engine.setProperty('rate', rate)
                
                # Use the clearest voice
                if voices:
                    for voice in voices:
                        if 'zira' in voice.name.lower() or 'david' in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            print(f"Using voice: {voice.name}")
                            break
                
                # Test speech
                test_text = f"Testing audio output at volume {volume} and rate {rate}"
                print(f"Speaking: {test_text}")
                engine.say(test_text)
                engine.runAndWait()
                
                # Pause between tests
                time.sleep(1)
                
                response = input("Did you hear that? (y/n/q to quit): ").lower()
                if response == 'y':
                    print(f"✅ SUCCESS! Volume: {volume}, Rate: {rate}")
                    return volume, rate
                elif response == 'q':
                    return None, None
        
        print("❌ No successful audio output detected")
        return None, None
        
    except Exception as e:
        print(f"Error testing audio: {e}")
        return None, None

if __name__ == "__main__":
    result = test_audio_output()
    if result[0] is not None:
        print(f"\n🎉 Recommended settings: Volume: {result[0]}, Rate: {result[1]}")
    else:
        print("\n❌ Audio output test failed")
        print("Try checking:")
        print("- Windows sound settings")
        print("- Default playback device")
        print("- Volume mixer for Python.exe")
        print("- Headphone/speaker connections")
