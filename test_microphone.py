#!/usr/bin/env python3
"""
Microphone diagnostic script for JARVIS
Tests microphone access and audio levels
"""

import pyaudio
import wave
import threading
import time
import struct

def list_audio_devices():
    """List all available audio devices"""
    print("Available audio devices:")
    p = pyaudio.PyAudio()
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"Device {i}: {info['name']}")
        print(f"  Channels: {info['maxInputChannels']} input, {info['maxOutputChannels']} output")
        print(f"  Sample Rate: {info['defaultSampleRate']}")
        print()
    
    p.terminate()

def test_microphone_levels(device_index=None, duration=10):
    """Test microphone input levels"""
    print(f"Testing microphone for {duration} seconds...")
    print("Speak into your microphone to see audio levels")
    print("Press Ctrl+C to stop early")
    
    # Audio parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        
        print("Listening...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Convert to audio data and calculate RMS (volume level)
                audio_data = struct.unpack(f'{CHUNK}h', data)
                rms = (sum(x**2 for x in audio_data) / len(audio_data)) ** 0.5
                
                # Create visual level indicator
                level = int(rms / 1000)  # Scale down for display
                level = min(level, 50)   # Cap at 50 characters
                
                bar = "█" * level + "░" * (50 - level)
                print(f"\rLevel: [{bar}] {rms:6.0f}", end="", flush=True)
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nError reading audio: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        
    except Exception as e:
        print(f"Error opening microphone: {e}")
    finally:
        p.terminate()
        print("\nMicrophone test complete")

def record_test_audio(filename="test_recording.wav", duration=5, device_index=None):
    """Record a test audio file"""
    print(f"Recording {duration} seconds to {filename}...")
    print("Speak clearly into your microphone")
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
            
            # Show progress
            progress = (i + 1) / (RATE / CHUNK * duration)
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"\rRecording: [{bar}] {progress*100:.0f}%", end="", flush=True)
        
        print("\nSaving...")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recording
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"Recording saved to {filename}")
        
    except Exception as e:
        print(f"Error recording: {e}")

def main():
    """Main diagnostic function"""
    print("JARVIS Microphone Diagnostic Tool")
    print("=" * 40)
    
    try:
        print("\n1. Listing audio devices:")
        list_audio_devices()
        
        print("\n2. Testing default microphone levels:")
        test_microphone_levels(duration=5)
        
        print("\n\n3. Recording test audio:")
        record_test_audio(duration=3)
        
        print("\n\nDiagnostic complete!")
        print("If you saw audio levels and the recording was created, your microphone is working.")
        print("If not, try:")
        print("- Check Windows microphone permissions")
        print("- Test with a different microphone")
        print("- Check microphone privacy settings")
        
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted by user")
    except Exception as e:
        print(f"Diagnostic error: {e}")

if __name__ == "__main__":
    main()
