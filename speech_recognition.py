import os
import json
import vosk
import pyaudio
import threading
import time
from collections import deque
from logger import logger
from tts import tts

class SpeechRecognition:
    """Speech recognition using Vosk for offline processing"""
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.microphone = None
        self.audio_queue = deque()
        self.is_listening = False
        self.is_recording = False
        self.hotword_detected = False
        self.listen_thread = None
        self.process_thread = None
        
        self._initialize_vosk()
        self._initialize_microphone()
    
    def _initialize_vosk(self):
        """Initialize Vosk speech recognition model"""
        try:
            from config import Config
            
            # Check if model exists, if not, user needs to download it
            if not os.path.exists(Config.VOSK_MODEL_PATH):
                logger.log_error(f"Vosk model not found at {Config.VOSK_MODEL_PATH}")
                logger.log_error("Please download the Vosk model manually from: https://alphacephei.com/vosk/models/")
                return
            
            self.model = vosk.Model(Config.VOSK_MODEL_PATH)
            self.recognizer = vosk.KaldiRecognizer(self.model, Config.SAMPLE_RATE)
            logger.log_activity("Vosk speech recognition initialized")
            
        except Exception as e:
            logger.log_error("Failed to initialize Vosk", e)
    
    def _initialize_microphone(self):
        """Initialize microphone using PyAudio"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find default input device
            default_device = self.audio.get_default_input_device_info()
            logger.log_activity(f"Using microphone: {default_device['name']}")
            
            from config import Config
            self.microphone = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=Config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=Config.CHUNK_SIZE
            )
            
            logger.log_activity("Microphone initialized")
            
        except Exception as e:
            logger.log_error("Failed to initialize microphone", e)
    
    def start_listening(self):
        """Start listening for hotword and commands"""
        if not self.model or not self.microphone:
            logger.log_error("Speech recognition not properly initialized")
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.process_thread = threading.Thread(target=self._process_audio, daemon=True)
        
        self.listen_thread.start()
        self.process_thread.start()
        
        logger.log_activity("Started listening for hotword")
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.is_recording = False
        
        if self.listen_thread:
            self.listen_thread.join(timeout=1.0)
        if self.process_thread:
            self.process_thread.join(timeout=1.0)
        
        logger.log_activity("Stopped listening")
    
    def _listen_loop(self):
        """Continuous audio capture loop"""
        while self.is_listening:
            try:
                if self.microphone:
                    data = self.microphone.read(4096, exception_on_overflow=False)
                    self.audio_queue.append(data)
                time.sleep(0.01)  # Small delay to prevent high CPU usage
            except Exception as e:
                logger.log_error("Error in listen loop", e)
                break
    
    def _process_audio(self):
        """Process audio data for speech recognition"""
        while self.is_listening:
            try:
                if self.audio_queue and self.recognizer:
                    audio_data = self.audio_queue.popleft()
                    
                    if self.recognizer.AcceptWaveform(audio_data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip().lower()
                        
                        if text:
                            if not self.hotword_detected:
                                # Listen for hotword
                                if self._contains_hotword(text):
                                    self.hotword_detected = True
                                    self._on_hotword_detected()
                            else:
                                # Process command
                                if text and text != "":
                                    self._on_command_detected(text)
                                    self.hotword_detected = False
                
                time.sleep(0.01)
                
            except Exception as e:
                logger.log_error("Error processing audio", e)
                continue
    
    def _contains_hotword(self, text):
        """Check if text contains the hotword"""
        from config import Config
        return Config.HOTWORD in text
    
    def _on_hotword_detected(self):
        """Handle hotword detection"""
        logger.log_activity("Hotword detected")
        tts.speak("Yes?")
        
        # Set a timeout for command listening
        threading.Timer(10.0, self._reset_hotword_detection).start()
    
    def _on_command_detected(self, command):
        """Handle command detection"""
        logger.log_activity(f"Command detected: {command}")
        
        # Import here to avoid circular imports
        from command_processor import process_command
        
        # Process command in separate thread
        thread = threading.Thread(
            target=process_command, 
            args=(command,), 
            daemon=True
        )
        thread.start()
    
    def _reset_hotword_detection(self):
        """Reset hotword detection after timeout"""
        if self.hotword_detected:
            self.hotword_detected = False
            logger.log_activity("Command timeout - returning to hotword listening")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        
        if self.microphone:
            self.microphone.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        
        logger.log_activity("Speech recognition cleaned up")

# Global speech recognition instance
speech_recognition = SpeechRecognition()
