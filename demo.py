#!/usr/bin/env python3
"""
JARVIS Test Demo - Test JARVIS functionality without full voice recognition
This script demonstrates the core functionality of JARVIS without requiring
the Vosk speech model to be downloaded.
"""

import sys
import os
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from logger import logger
from tts import tts
from command_processor import process_command
from activity_monitor import activity_monitor

def test_basic_functionality():
    """Test basic JARVIS components without voice recognition"""
    
    print("🤖 JARVIS Test Demo")
    print("=" * 50)
    print()
    
    # Initialize configuration
    Config.ensure_directories()
    logger.log_activity("JARVIS Test Demo started")
    
    # Test TTS
    print("1. Testing Text-to-Speech...")
    try:
        tts.speak("Hello! JARVIS text to speech is working!")
        print("   ✅ TTS working")
        time.sleep(2)
    except Exception as e:
        print(f"   ❌ TTS error: {e}")
    
    # Test activity monitoring
    print("\n2. Testing Activity Monitor...")
    try:
        activity_monitor.start_monitoring()
        print("   ✅ Activity monitoring started")
        time.sleep(1)
        activity_monitor.stop_monitoring()
        print("   ✅ Activity monitoring stopped")
    except Exception as e:
        print(f"   ❌ Activity monitor error: {e}")
    
    # Test command processing
    print("\n3. Testing Command Processing...")
    
    test_commands = [
        "what time is it",
        "check cpu usage",
        "take a screenshot",
        "open notepad",
        "open google"
    ]
    
    for command in test_commands:
        try:
            print(f"   Testing: '{command}'")
            process_command(command)
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ Command error for '{command}': {e}")
    
    print("\n4. Demo Complete!")
    print("Check the 'logs' folder for activity logs.")
    print("\nTo enable full voice recognition:")
    print("1. Download Vosk model from: https://alphacephei.com/vosk/models/")
    print("2. Extract to: models/vosk-model-en-us-0.22/")
    print("3. Install PyAudio: pip install PyAudio")
    print("4. Run: python main.py")

def interactive_demo():
    """Interactive demo where user can type commands"""
    
    print("\n🎤 Interactive Command Demo")
    print("=" * 50)
    print("Type commands as if you were speaking to JARVIS")
    print("Type 'quit' to exit")
    print()
    
    # Initialize
    Config.ensure_directories()
    logger.log_activity("Interactive demo started")
    
    tts.speak("Interactive demo ready. Type your commands!")
    
    while True:
        try:
            command = input("You: ").strip()
            
            if command.lower() in ['quit', 'exit', 'stop']:
                break
            
            if command:
                print(f"Processing: {command}")
                process_command(command)
                print()
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("Demo ended!")
    tts.speak("Goodbye!")

def main():
    """Main demo function"""
    
    print("JARVIS Desktop Assistant - Test Demo")
    print("====================================")
    print()
    print("Choose demo mode:")
    print("1. Basic functionality test")
    print("2. Interactive command demo")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        test_basic_functionality()
    
    if choice in ["2", "3"]:
        interactive_demo()
    
    print("\n🎉 Demo complete!")
    print("To run full JARVIS: python main.py")

if __name__ == "__main__":
    main()
