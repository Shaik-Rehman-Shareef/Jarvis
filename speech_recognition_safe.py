import os
import json
import threading
import time
from collections import deque
from logger import logger
from tts import tts

# Try to import dependencies, but make them optional
try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.log_error("Vosk not available - speech recognition will be disabled")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.log_error("PyAudio not available - using alternative audio method")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.log_activity("Whisper not available - using Vosk only")

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
        self.audio_available = False
        
        # Whisper for better accuracy
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                logger.log_activity("Whisper model loaded successfully")
            except Exception as e:
                logger.log_error("Failed to initialize Whisper", e)
        
        if VOSK_AVAILABLE and PYAUDIO_AVAILABLE:
            self._initialize_vosk()
            self._initialize_microphone()
        else:
            logger.log_error("Speech recognition disabled due to missing dependencies")
    
    def _initialize_vosk(self):
        """Initialize Vosk speech recognition model"""
        try:
            from config import Config
            
            # Check if model exists, if not, user needs to download it
            model_path = Config.VOSK_MODEL_PATH
            if not os.path.exists(model_path):
                # Try small model as fallback
                small_model_path = "models/vosk-model-small-en-us-0.15"
                if os.path.exists(small_model_path):
                    model_path = small_model_path
                    logger.log_activity(f"Using small Vosk model: {model_path}")
                else:
                    logger.log_error(f"Vosk model not found at {Config.VOSK_MODEL_PATH}")
                    logger.log_error("Please download the Vosk model manually from: https://alphacephei.com/vosk/models/")
                    logger.log_error("Or run: python setup_vosk_small.py")
                    return
            
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, Config.SAMPLE_RATE)
            logger.log_activity("Vosk speech recognition initialized")
            
        except Exception as e:
            logger.log_error("Failed to initialize Vosk", e)
    
    def _initialize_microphone(self):
        """Initialize microphone using PyAudio"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Try to use the working microphone device if available
            device_index = None
            try:
                with open("working_microphone.txt", "r") as f:
                    device_index = int(f.read().strip())
                    device_info = self.audio.get_device_info_by_index(device_index)
                    logger.log_activity(f"Using working microphone device {device_index}: {device_info['name']}")
            except:
                # Fall back to default device
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
            logger.log_activity("Microphone initialized successfully")
            
        except Exception as e:
            logger.log_error("Failed to initialize microphone", e)
            self.audio_available = False
    
    def start_listening(self):
        """Start listening for hotword and commands"""
        if not self.audio_available:
            logger.log_error("Audio not available - starting in text-only mode")
            self._start_text_mode()
            return
        
        if not self.model or not self.microphone:
            logger.log_error("Speech recognition not properly initialized")
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.process_thread = threading.Thread(target=self._process_audio, daemon=True)
        self.keyboard_thread = threading.Thread(target=self._keyboard_override, daemon=True)
        
        self.listen_thread.start()
        self.process_thread.start()
        self.keyboard_thread.start()
        
        logger.log_activity("Started listening for hotword")
        logger.log_activity("Keyboard override: Press 'h' key to manually trigger hotword")
    
    def _keyboard_override(self):
        """Keyboard override for testing - press 'h' to trigger hotword"""
        try:
            import keyboard
            while self.is_listening:
                if keyboard.is_pressed('h'):
                    if not self.hotword_detected:
                        logger.log_activity("Manual hotword trigger via keyboard!")
                        self.hotword_detected = True
                        self._on_hotword_detected()
                        
                        # Wait for key release to avoid repeated triggers
                        while keyboard.is_pressed('h'):
                            time.sleep(0.1)
                time.sleep(0.1)
        except ImportError:
            logger.log_activity("Keyboard module not available - no keyboard override")
        except Exception as e:
            logger.log_error("Error in keyboard override", e)
    
    def _start_text_mode(self):
        """Start in text-only mode for testing without audio"""
        self.is_listening = True
        logger.log_activity("Started in text-only mode - audio input disabled")
        # Note: In real deployment, you might want to implement keyboard shortcuts
        # or other input methods when audio is not available
    
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
        """Continuous audio capture loop with noise filtering"""
        import struct
        
        logger.log_activity("Audio capture loop started with noise filtering")
        audio_chunks_processed = 0
        noise_threshold = 500  # Lowered threshold for better sensitivity
        
        while self.is_listening:
            try:
                if self.microphone:
                    data = self.microphone.read(4096, exception_on_overflow=False)
                    
                    # Calculate audio level to filter background noise
                    try:
                        audio_data = struct.unpack(f'{len(data)//2}h', data)
                        rms = (sum(x**2 for x in audio_data) / len(audio_data)) ** 0.5
                        
                        # Only process audio above threshold to reduce background noise
                        if rms > noise_threshold:
                            self.audio_queue.append(data)
                            audio_chunks_processed += 1
                            
                            # Log occasionally with volume level
                            if audio_chunks_processed % 50 == 0:  # More frequent logging
                                logger.log_activity(f"Processed {audio_chunks_processed} audio chunks (vol: {rms:.0f})")
                        
                    except struct.error:
                        # If we can't calculate volume, process anyway
                        self.audio_queue.append(data)
                        audio_chunks_processed += 1
                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
            except Exception as e:
                logger.log_error("Error in listen loop", e)
                break
    
    def _recognize_with_whisper(self, audio_data):
        """Use Whisper for better accuracy"""
        if not self.whisper_model:
            return ""
        
        try:
            import tempfile
            import wave
            
            # Save audio data to temporary file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Create wav file
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(16000)
                    wav_file.writeframes(audio_data)
                
                # Recognize with Whisper
                result = self.whisper_model.transcribe(temp_file.name)
                
                # Clean up
                import os
                os.unlink(temp_file.name)
                
                return result['text'].lower().strip()
        except Exception as e:
            logger.log_error(f"Error in Whisper recognition: {e}")
            return ""
    
    def _process_audio(self):
        """Process audio data for speech recognition"""
        logger.log_activity("Speech recognition processing started")
        processed_results = 0
        
        while self.is_listening:
            try:
                if self.audio_queue and self.recognizer:
                    audio_data = self.audio_queue.popleft()
                    
                    # Try both AcceptWaveform and PartialResult for better detection
                    if self.recognizer.AcceptWaveform(audio_data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip().lower()
                        processed_results += 1
                        
                        # Only log non-empty results to reduce noise
                        if text:
                            logger.log_activity(f"Speech result #{processed_results}: '{text}'")
                            
                            if not self.hotword_detected:
                                # Listen for hotword
                                logger.log_activity(f"Checking for hotword in: '{text}'")
                                if self._contains_hotword(text):
                                    self.hotword_detected = True
                                    self._on_hotword_detected()
                            else:
                                # Process command - be more flexible with what we accept
                                if text and len(text.strip()) > 0:
                                    logger.log_activity(f"Processing command: '{text}'")
                                    self._on_command_detected(text)
                                    self.hotword_detected = False
                    else:
                        # Check partial results too for faster response
                        partial_result = json.loads(self.recognizer.PartialResult())
                        partial_text = partial_result.get('partial', '').strip().lower()
                        
                        # Only process meaningful partial results and avoid noise
                        if partial_text and len(partial_text) >= 3:
                            # Filter out common noise patterns
                            noise_patterns = ['uh', 'um', 'ah', 'eh', 'mm', 'hmm']
                            if not any(pattern in partial_text for pattern in noise_patterns):
                                
                                if not self.hotword_detected:
                                    logger.log_activity(f"Partial result: '{partial_text}'")
                                    if self._contains_hotword(partial_text):
                                        self.hotword_detected = True
                                        self._on_hotword_detected()
                                else:
                                    # In command mode, also accept longer partial results as commands
                                    if len(partial_text) >= 6:  # Longer partial text might be a complete command
                                        logger.log_activity(f"Command from partial result: '{partial_text}'")
                                        self._on_command_detected(partial_text)
                                        self.hotword_detected = False
                
                time.sleep(0.01)
                
            except Exception as e:
                logger.log_error("Error processing audio", e)
                continue
    
    def _contains_hotword(self, text):
        """Check if text contains the hotword"""
        text_lower = text.lower().strip()
        
        # Skip very short or empty text
        if len(text_lower) < 2:
            return False
        
        # Primary hotword is now "hey"
        primary_keywords = [
            "hey",
            "hi",
            "hello"
        ]
        
        # Check for exact matches or keywords at start of text
        for keyword in primary_keywords:
            if text_lower == keyword or text_lower.startswith(keyword + " "):
                logger.log_activity(f"Hotword detected: '{keyword}' in '{text}'")
                return True
        
        # Secondary alternatives (less sensitive)
        alternatives = [
            "jarvis",
            "activate",
            "huh"  # What Vosk sometimes recognizes
        ]
        
        for alt in alternatives:
            if alt in text_lower:
                logger.log_activity(f"Alternative hotword detected: '{alt}' in '{text}'")
                return True
                
        return False
    
    def _on_hotword_detected(self):
        """Handle hotword detection"""
        logger.log_activity("Hotword detected")
        
        # Update system tray status
        try:
            from main import jarvis_instance
            if hasattr(jarvis_instance, 'system_tray') and jarvis_instance.system_tray:
                jarvis_instance.system_tray.update_status("processing")
        except:
            pass
        
        # Choose a personalized acknowledgment response
        from conversation_context import jarvis_personality, conversation_context
        response = jarvis_personality.get_acknowledgment(conversation_context)
        logger.log_activity(f"Responding with: {response}")
        
        # Speak acknowledgment with higher priority (blocking)
        tts.speak(response, blocking=True)
        
        # Brief pause to let user prepare to speak command
        import time
        time.sleep(0.5)  # Small pause after acknowledgment
        
        # Update status back to listening
        try:
            from main import jarvis_instance
            if hasattr(jarvis_instance, 'system_tray') and jarvis_instance.system_tray:
                jarvis_instance.system_tray.update_status("ready")
        except:
            pass
        
        # Set a timeout for command listening
        threading.Timer(15.0, self._reset_hotword_detection).start()
    
    def _on_command_detected(self, command):
        """Handle command detection with enhanced recognition"""
        logger.log_activity(f"Command detected (Vosk): {command}")
        
        # Try to get better transcription with Whisper if available
        enhanced_command = command
        if self.whisper_model and len(self.audio_queue) > 0:
            try:
                # Get recent audio data for Whisper
                recent_audio = b''.join(list(self.audio_queue)[-10:])  # Last 10 chunks
                if len(recent_audio) > 1000:  # Ensure meaningful audio
                    whisper_result = self._recognize_with_whisper(recent_audio)
                    if whisper_result and len(whisper_result) > len(command):
                        enhanced_command = whisper_result
                        logger.log_activity(f"Enhanced command (Whisper): {enhanced_command}")
            except Exception as e:
                logger.log_error("Error with Whisper enhancement", e)
        
        # Import here to avoid circular imports
        from command_processor import process_command
        
        # Process enhanced command in separate thread
        thread = threading.Thread(
            target=process_command, 
            args=(enhanced_command,), 
            daemon=True
        )
        thread.start()
    
    def _reset_hotword_detection(self):
        """Reset hotword detection after timeout"""
        if self.hotword_detected:
            self.hotword_detected = False
            logger.log_activity("Command timeout - returning to hotword listening")
    
    def simulate_command(self, command):
        """Simulate a voice command for testing when audio is not available"""
        logger.log_activity(f"Simulating command: {command}")
        self._on_command_detected(command)
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        
        if self.microphone:
            self.microphone.close()
        if hasattr(self, 'audio') and self.audio:
            self.audio.terminate()
        
        logger.log_activity("Speech recognition cleaned up")

# Global speech recognition instance
speech_recognition = SpeechRecognition()
