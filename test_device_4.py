#!/usr/bin/env python3
"""
Quick microphone test for device 4
"""

import pyaudio
import time
import struct

def test_device_4():
    print("Testing Device 4 with real-time audio levels...")
    print("Say 'Hey Jarvis' loudly and clearly")
    
    CHUNK = 4096  # Same as JARVIS uses
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    DEVICE_ID = 4
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=DEVICE_ID,
            frames_per_buffer=CHUNK
        )
        
        print("Listening for 10 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            data = stream.read(CHUNK, exception_on_overflow=False)
            
            # Calculate audio level
            audio_data = struct.unpack(f'{CHUNK}h', data)
            rms = (sum(x**2 for x in audio_data) / len(audio_data)) ** 0.5
            
            # Show level bar
            level = int(rms / 500)  # Scale for display
            level = min(level, 40)   # Cap at 40 characters
            
            bar = "█" * level + "░" * (40 - level)
            print(f"\rLevel: [{bar}] {rms:6.0f}", end="", flush=True)
            
            # Alert if good audio detected
            if rms > 2000:
                print(f" <-- GOOD AUDIO DETECTED!")
            
            time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        p.terminate()
        print("\nTest complete")

if __name__ == "__main__":
    test_device_4()
