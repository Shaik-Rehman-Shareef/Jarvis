#!/usr/bin/env python3
"""
Enhanced speech recognition for JARVIS with multiple model support
Supports Vosk, Whisper, and Google Speech Recognition
"""

import os
import json
import threading
import time
import tempfile
import wave
from collections import deque
from logger import logger
from tts import tts

# Try to import speech recognition libraries
try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.log_error("Vosk not available")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.log_error("Whisper not available")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.log_error("SpeechRecognition library not available")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.log_error("PyAudio not available")

class EnhancedSpeechRecognition:
    """Enhanced speech recognition with multiple model support"""
    
    def __init__(self, preferred_model="vosk"):
        self.preferred_model = preferred_model
        self.models = {}
        self.microphone = None
        self.audio_queue = deque()
        self.is_listening = False
        self.hotword_detected = False
        self.listen_thread = None
        self.process_thread = None
        self.audio_available = False
        
        # Initialize available models
        self._initialize_models()
        self._initialize_microphone()
    
    def _initialize_models(self):
        """Initialize available speech recognition models"""
        logger.log_activity("Initializing speech recognition models...")
        
        # Initialize Vosk
        if VOSK_AVAILABLE:
            self._initialize_vosk()
        
        # Initialize Whisper
        if WHISPER_AVAILABLE:
            self._initialize_whisper()
        
        # Initialize Google Speech Recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            self._initialize_google_sr()
    
    def _initialize_vosk(self):
        """Initialize Vosk model"""
        try:
            from config import Config
            
            # Try to find the best available Vosk model
            models_to_try = [
                "models/vosk-model-en-us-0.22",  # Large model
                "models/vosk-model-small-en-us-0.15",  # Small model
                Config.VOSK_MODEL_PATH  # Config model
            ]
            
            for model_path in models_to_try:
                if os.path.exists(model_path):
                    logger.log_activity(f"Loading Vosk model: {model_path}")
                    model = vosk.Model(model_path)
                    recognizer = vosk.KaldiRecognizer(model, Config.SAMPLE_RATE)
                    self.models["vosk"] = {
                        "model": model,
                        "recognizer": recognizer,
                        "accuracy": "good",
                        "speed": "fast"
                    }
                    logger.log_activity(f"✅ Vosk model loaded: {model_path}")
                    break
            else:
                logger.log_error("No Vosk model found")
                
        except Exception as e:
            logger.log_error("Failed to initialize Vosk", e)
    
    def _initialize_whisper(self):
        """Initialize Whisper model"""
        try:
            # Load a smaller Whisper model for faster processing
            model = whisper.load_model("base")  # base, small, medium, large
            self.models["whisper"] = {
                "model": model,
                "accuracy": "excellent",
                "speed": "medium"
            }
            logger.log_activity("✅ Whisper model loaded")
        except Exception as e:
            logger.log_error("Failed to initialize Whisper", e)
    
    def _initialize_google_sr(self):
        """Initialize Google Speech Recognition"""
        try:
            recognizer = sr.Recognizer()
            self.models["google"] = {
                "recognizer": recognizer,
                "accuracy": "very_good",
                "speed": "variable",
                "requires_internet": True
            }
            logger.log_activity("✅ Google Speech Recognition initialized")
        except Exception as e:
            logger.log_error("Failed to initialize Google SR", e)
    
    def _initialize_microphone(self):
        """Initialize microphone"""
        if not PYAUDIO_AVAILABLE:
            logger.log_error("PyAudio not available - microphone disabled")
            return
            
        try:
            self.audio = pyaudio.PyAudio()
            
            # Try to use the working microphone device
            device_index = None
            try:
                with open("working_microphone.txt", "r") as f:
                    device_index = int(f.read().strip())
                    device_info = self.audio.get_device_info_by_index(device_index)
                    logger.log_activity(f"Using microphone device {device_index}: {device_info['name']}")
            except:
                device_info = self.audio.get_default_input_device_info()
                logger.log_activity(f"Using default microphone: {device_info['name']}")
            
            from config import Config
            self.microphone = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=Config.SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=Config.CHUNK_SIZE
            )
            
            self.audio_available = True
            logger.log_activity("✅ Microphone initialized successfully")
            
        except Exception as e:
            logger.log_error("Failed to initialize microphone", e)
    
    def recognize_speech(self, audio_data, model_name=None):
        """Recognize speech using specified model or best available"""
        if not model_name:
            model_name = self._get_best_model()
        
        if model_name not in self.models:
            logger.log_error(f"Model {model_name} not available")
            return ""
        
        try:
            if model_name == "vosk":
                return self._recognize_vosk(audio_data)
            elif model_name == "whisper":
                return self._recognize_whisper(audio_data)
            elif model_name == "google":
                return self._recognize_google(audio_data)
        except Exception as e:
            logger.log_error(f"Error recognizing speech with {model_name}", e)
            
        return ""
    
    def _recognize_vosk(self, audio_data):
        """Recognize speech using Vosk"""
        recognizer = self.models["vosk"]["recognizer"]
        
        if recognizer.AcceptWaveform(audio_data):
            result = json.loads(recognizer.Result())
            return result.get('text', '').strip()
        else:
            partial = json.loads(recognizer.PartialResult())
            return partial.get('partial', '').strip()
    
    def _recognize_whisper(self, audio_data):
        """Recognize speech using Whisper"""
        # Save audio to temporary file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            # Convert raw audio to WAV format
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_data)
            
            # Recognize with Whisper
            model = self.models["whisper"]["model"]
            result = model.transcribe(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
            
            return result.get("text", "").strip()
    
    def _recognize_google(self, audio_data):
        """Recognize speech using Google Speech Recognition"""
        recognizer = self.models["google"]["recognizer"]
        
        # Convert audio data to AudioData object
        audio_file = sr.AudioData(audio_data, 16000, 2)
        
        try:
            # Use Google Speech Recognition
            result = recognizer.recognize_google(audio_file)
            return result.strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            logger.log_error(f"Google SR request error: {e}")
            return ""
    
    def _get_best_model(self):
        """Get the best available model based on accuracy and availability"""
        preference_order = ["whisper", "google", "vosk"]
        
        for model_name in preference_order:
            if model_name in self.models:
                # Check internet requirement for Google
                if model_name == "google":
                    # Simple internet check (you might want to implement a proper check)
                    pass
                return model_name
        
        logger.log_error("No speech recognition models available")
        return None
    
    def start_listening(self):
        """Start listening for speech"""
        if not self.audio_available:
            logger.log_error("Audio not available - cannot start listening")
            return
        
        self.is_listening = True
        
        # Start audio capture thread
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_audio, daemon=True)
        self.process_thread.start()
        
        # Start keyboard override thread
        keyboard_thread = threading.Thread(target=self._keyboard_override, daemon=True)
        keyboard_thread.start()
        
        logger.log_activity("✅ Enhanced speech recognition started")
        logger.log_activity(f"Available models: {list(self.models.keys())}")
        logger.log_activity("Press 'h' key to manually trigger hotword")
    
    def _listen_loop(self):
        """Audio capture loop"""
        logger.log_activity("Audio capture started")
        chunk_count = 0
        
        while self.is_listening:
            try:
                if self.microphone:
                    data = self.microphone.read(4096, exception_on_overflow=False)
                    self.audio_queue.append(data)
                    chunk_count += 1
                    
                    if chunk_count % 100 == 0:
                        logger.log_activity(f"Captured {chunk_count} audio chunks")
                
                time.sleep(0.01)
            except Exception as e:
                logger.log_error("Error in audio capture", e)
                break
    
    def _process_audio(self):
        """Process audio for speech recognition"""
        logger.log_activity("Audio processing started")
        
        while self.is_listening:
            try:
                if self.audio_queue:
                    # Collect some audio data
                    audio_chunks = []
                    for _ in range(min(10, len(self.audio_queue))):
                        if self.audio_queue:
                            audio_chunks.append(self.audio_queue.popleft())
                    
                    if audio_chunks:
                        audio_data = b''.join(audio_chunks)
                        
                        # Try recognition with best available model
                        text = self.recognize_speech(audio_data)
                        
                        if text:
                            logger.log_activity(f"Recognized: '{text}'")
                            
                            if not self.hotword_detected:
                                if self._contains_hotword(text):
                                    self.hotword_detected = True
                                    self._on_hotword_detected()
                            else:
                                if text and text.strip():
                                    self._on_command_detected(text)
                                    self.hotword_detected = False
                
                time.sleep(0.1)
            except Exception as e:
                logger.log_error("Error processing audio", e)
                continue
    
    def _contains_hotword(self, text):
        """Check if text contains hotword"""
        text_lower = text.lower().strip()
        
        hotwords = ["hey", "hi", "hello", "jarvis"]
        
        for hotword in hotwords:
            if hotword in text_lower:
                logger.log_activity(f"Hotword detected: '{hotword}' in '{text}'")
                return True
        
        return False
    
    def _on_hotword_detected(self):
        """Handle hotword detection"""
        logger.log_activity("🎯 Hotword detected!")
        
        responses = [
            "Yes sir?",
            "I'm listening.",
            "How can I help you?",
            "At your service.",
            "Yes?",
            "Ready for your command."
        ]
        
        import random
        response = random.choice(responses)
        logger.log_activity(f"Responding with: {response}")
        tts.speak(response, blocking=True)
        
        # Reset after timeout
        threading.Timer(15.0, self._reset_hotword).start()
    
    def _on_command_detected(self, command):
        """Handle command detection"""
        logger.log_activity(f"Command received: {command}")
        # Handle command here
        pass
    
    def _reset_hotword(self):
        """Reset hotword detection"""
        self.hotword_detected = False
        logger.log_activity("Hotword detection reset")
    
    def _keyboard_override(self):
        """Keyboard override for testing"""
        try:
            import keyboard
            
            while self.is_listening:
                try:
                    if keyboard.is_pressed('h'):
                        if not self.hotword_detected:
                            logger.log_activity("Manual hotword trigger via keyboard!")
                            self.hotword_detected = True
                            self._on_hotword_detected()
                        time.sleep(0.5)  # Prevent multiple triggers
                    time.sleep(0.1)
                except:
                    time.sleep(1)  # If keyboard module fails, just wait
        except ImportError:
            logger.log_error("Keyboard module not available")
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        if self.microphone:
            self.microphone.stop_stream()
            self.microphone.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        logger.log_activity("Speech recognition stopped")

# Global instance
enhanced_speech_recognition = None

def get_speech_recognition():
    """Get speech recognition instance"""
    global enhanced_speech_recognition
    if enhanced_speech_recognition is None:
        enhanced_speech_recognition = EnhancedSpeechRecognition()
    return enhanced_speech_recognition
