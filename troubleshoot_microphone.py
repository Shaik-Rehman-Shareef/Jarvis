#!/usr/bin/env python3
"""
Enhanced microphone troubleshooting for JARVIS
"""

import pyaudio
import time

def check_microphone_permissions():
    """Check Windows microphone permissions and provide guidance"""
    print("🔍 Checking microphone permissions...")
    print()
    print("Common issues and solutions:")
    print("1. Windows Privacy Settings:")
    print("   - Go to Settings > Privacy > Microphone")
    print("   - Enable 'Allow apps to access your microphone'")
    print("   - Enable 'Allow desktop apps to access your microphone'")
    print()
    print("2. Microphone not working in any application:")
    print("   - Check Device Manager > Audio inputs and outputs")
    print("   - Update audio drivers")
    print("   - Try a different microphone")
    print()
    print("3. Antivirus blocking microphone:")
    print("   - Check your antivirus settings")
    print("   - Add Python.exe to exceptions")
    print()

def test_specific_device(device_index):
    """Test a specific audio device"""
    print(f"Testing device {device_index}...")
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    
    try:
        # Get device info
        device_info = p.get_device_info_by_index(device_index)
        print(f"Device: {device_info['name']}")
        print(f"Channels: {device_info['maxInputChannels']}")
        print(f"Sample Rate: {device_info['defaultSampleRate']}")
        
        if device_info['maxInputChannels'] == 0:
            print("❌ This device has no input channels")
            return False
        
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        
        print("✅ Device opened successfully")
        print("Testing audio for 3 seconds...")
        
        for i in range(30):  # 3 seconds at 0.1s intervals
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Simple level check
                audio_level = max(abs(int.from_bytes(data[i:i+2], 'little', signed=True)) for i in range(0, len(data), 2))
                
                if audio_level > 100:  # Some threshold for activity
                    print(f"✅ Audio detected! Level: {audio_level}")
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return True
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error reading audio: {e}")
                break
        
        print("❌ No audio detected on this device")
        stream.stop_stream()
        stream.close()
        
    except Exception as e:
        print(f"❌ Failed to open device: {e}")
        return False
    finally:
        p.terminate()
    
    return False

def find_working_microphone():
    """Find a working microphone device"""
    print("🔍 Searching for working microphone...")
    
    p = pyaudio.PyAudio()
    
    # Get all input devices
    input_devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_devices.append((i, device_info))
    
    p.terminate()
    
    print(f"Found {len(input_devices)} input devices:")
    for i, (device_index, device_info) in enumerate(input_devices):
        print(f"{i+1}. Device {device_index}: {device_info['name']}")
    
    print("\nTesting devices...")
    
    working_devices = []
    for device_index, device_info in input_devices:
        print(f"\n--- Testing Device {device_index}: {device_info['name']} ---")
        if test_specific_device(device_index):
            working_devices.append(device_index)
            print(f"✅ Device {device_index} is working!")
        else:
            print(f"❌ Device {device_index} not working")
    
    return working_devices

def main():
    """Main troubleshooting function"""
    print("JARVIS Microphone Troubleshooting")
    print("=" * 40)
    
    try:
        check_microphone_permissions()
        
        print("\n" + "=" * 40)
        working_devices = find_working_microphone()
        
        if working_devices:
            print(f"\n✅ Found {len(working_devices)} working microphone(s):")
            for device_id in working_devices:
                print(f"   Device {device_id}")
            
            print(f"\nRecommendation: Use device {working_devices[0]} in JARVIS")
            
            # Save the working device to config
            with open("working_microphone.txt", "w") as f:
                f.write(str(working_devices[0]))
            print(f"Saved working device ID to 'working_microphone.txt'")
            
        else:
            print("\n❌ No working microphones found!")
            print("\nTroubleshooting steps:")
            print("1. Check Windows microphone permissions")
            print("2. Test your microphone in other applications")
            print("3. Try a different microphone")
            print("4. Restart your computer")
            print("5. Update audio drivers")
        
    except Exception as e:
        print(f"Error during troubleshooting: {e}")

if __name__ == "__main__":
    main()
