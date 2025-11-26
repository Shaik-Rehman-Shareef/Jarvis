#!/usr/bin/env python3
"""
Windows audio device checker and fixer
"""

import pyttsx3

def check_audio_devices():
    print("Checking Windows audio output devices...")
    
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Get available voices and audio devices
        voices = engine.getProperty('voices')
        print(f"Found {len(voices)} voice(s):")
        
        for i, voice in enumerate(voices):
            print(f"  Voice {i}: {voice.name}")
            print(f"    ID: {voice.id}")
            print(f"    Languages: {voice.languages}")
            print()
        
        # Check current settings
        rate = engine.getProperty('rate')
        volume = engine.getProperty('volume')
        voice = engine.getProperty('voice')
        
        print(f"Current TTS Settings:")
        print(f"  Rate: {rate}")
        print(f"  Volume: {volume}")
        print(f"  Voice: {voice}")
        print()
        
        # Try to increase volume and test
        print("Setting maximum volume and testing...")
        engine.setProperty('volume', 1.0)  # Maximum volume
        engine.setProperty('rate', 150)    # Clear speech rate
        
        print("Testing with maximum volume...")
        engine.say("This is a maximum volume test. Can you hear me now?")
        engine.runAndWait()
        
        print("Audio test complete!")
        
    except Exception as e:
        print(f"Error checking audio: {e}")

def check_windows_audio():
    print("\nWindows Audio Troubleshooting:")
    print("1. Check Windows volume mixer (right-click speaker icon)")
    print("2. Make sure Python.exe isn't muted in volume mixer")
    print("3. Check default playback device in Windows Sound settings")
    print("4. Try different headphones/speakers")
    print("5. Check Windows Sound settings > App volume and device preferences")

if __name__ == "__main__":
    check_audio_devices()
    check_windows_audio()
