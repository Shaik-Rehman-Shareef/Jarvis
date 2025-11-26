#!/usr/bin/env python3
"""
Direct Vosk speech recognition test
"""

import pyaudio
import vosk
import json
import os

def test_vosk_recognition():
    print("Testing Vosk speech recognition directly...")
    print("Say 'Hey Jarvis' clearly into your microphone")
    
    # Use same model as JARVIS
    model_path = "models/vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return
    
    # Initialize Vosk
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)
    
    # Initialize audio
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=4,  # Use same device as JARVIS
            frames_per_buffer=4096
        )
        
        print("Listening for 15 seconds...")
        print("Results will appear below:")
        print("-" * 50)
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < 15:
            data = stream.read(4096, exception_on_overflow=False)
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get('text', '').strip()
                if text:
                    print(f"Recognized: '{text}'")
                    
                    # Check for hotword
                    if 'jarvis' in text.lower():
                        print("🎉 HOTWORD DETECTED! 🎉")
            else:
                # Partial result
                partial_result = json.loads(recognizer.PartialResult())
                partial_text = partial_result.get('partial', '').strip()
                if partial_text:
                    print(f"Partial: '{partial_text}'", end='\r')
        
        # Final result
        final_result = json.loads(recognizer.FinalResult())
        final_text = final_result.get('text', '').strip()
        if final_text:
            print(f"\nFinal: '{final_text}'")
        
        stream.stop_stream()
        stream.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        p.terminate()
        print("\nTest complete")

if __name__ == "__main__":
    test_vosk_recognition()
