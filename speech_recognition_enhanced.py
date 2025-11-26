"""
Enhanced Speech Recognition for JARVIS
Supports multiple speech recognition engines for improved accuracy:
1. Vosk (offline, small/large models)
2. Google Speech Recognition (online, requires internet)
3. OpenAI Whisper (offline, excellent accuracy)
"""
import os
import json
import threading
import time
import io
import wave
from collections import deque
from logger import logger
from tts import tts

# Try to import dependencies
try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import speech_recognition as sr
    GOOGLE_SR_AVAILABLE = True
except ImportError:
    GOOGLE_SR_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

class EnhancedSpeechRecognition:
    """Enhanced Speech Recognition with multiple engines"""
    
    def __init__(self, preferred_engine="google"):
        self.preferred_engine = preferred_engine
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
        
        # Speech recognition engines
        self.sr_recognizer = None
        self.whisper_model = None
        
        # Initialize available engines
        self._initialize_engines()
        
        if PYAUDIO_AVAILABLE:
            self._initialize_microphone()
        else:
            logger.log_error("PyAudio not available - speech recognition disabled")
    
    def _initialize_engines(self):
        """Initialize available speech recognition engines"""
        engines_initialized = []
        
        # Initialize Google Speech Recognition
        if GOOGLE_SR_AVAILABLE:
            try:
                self.sr_recognizer = sr.Recognizer()
                engines_initialized.append("Google Speech Recognition")
            except Exception as e:
                logger.log_error("Failed to initialize Google Speech Recognition", e)
        
        # Initialize Whisper
        if WHISPER_AVAILABLE:
            try:
                # Use the smallest model for faster loading
                self.whisper_model = whisper.load_model("base")
                engines_initialized.append("OpenAI Whisper")
            except Exception as e:
                logger.log_error("Failed to initialize Whisper", e)
        
        # Initialize Vosk
        if VOSK_AVAILABLE:
            self._initialize_vosk()
            if self.model:
                engines_initialized.append("Vosk")
        
        logger.log_activity(f"Speech recognition engines initialized: {', '.join(engines_initialized)}")
        
        if not engines_initialized:
            logger.log_error("No speech recognition engines available!")
    
    def _initialize_vosk(self):
        """Initialize Vosk speech recognition model"""
        try:
            from config import Config
            
            # Check available models
            model_paths = [
                "models/vosk-model-en-us-0.22",  # Large model
                "models/vosk-model-small-en-us-0.15",  # Small model
                Config.VOSK_MODEL_PATH if hasattr(Config, 'VOSK_MODEL_PATH') else None
            ]
            
            model_path = None
            for path in model_paths:
                if path and os.path.exists(path):
                    model_path = path
                    break
            
            if not model_path:
                logger.log_error("No Vosk model found. Skipping Vosk initialization.")
                return
            
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, Config.SAMPLE_RATE)
            logger.log_activity(f"Vosk initialized with model: {model_path}")
            
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
    
    def _get_best_available_engine(self):
        """Get the best available speech recognition engine"""
        # Priority order: Whisper > Google > Vosk
        if WHISPER_AVAILABLE and self.whisper_model:
            return "whisper"
        elif GOOGLE_SR_AVAILABLE and self.sr_recognizer:
            return "google"
        elif VOSK_AVAILABLE and self.model:
            return "vosk"
        else:
            return None
    
    def _recognize_with_google(self, audio_data):
        """Recognize speech using Google Speech Recognition"""
        try:
            # Convert audio data to wav format for Google SR
            audio_wav = sr.AudioData(audio_data, 16000, 2)
            text = self.sr_recognizer.recognize_google(audio_wav, language='en-US')
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            logger.log_error(f"Google Speech Recognition error: {e}")
            return ""
    
    def _recognize_with_whisper(self, audio_data):
        """Recognize speech using OpenAI Whisper"""
        try:
            # Save audio data to temporary file for Whisper
            import tempfile
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
                os.unlink(temp_file.name)
                
                return result['text'].lower().strip()
        except Exception as e:
            logger.log_error(f"Whisper recognition error: {e}")
            return ""
    
    def _recognize_with_vosk(self, audio_data):
        """Recognize speech using Vosk"""
        try:
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                return result.get('text', '').lower()
            else:
                partial = json.loads(self.recognizer.PartialResult())
                return partial.get('partial', '').lower()
        except Exception as e:
            logger.log_error(f"Vosk recognition error: {e}")
            return ""
    
    def recognize_speech(self, audio_data, engine=None):
        """Recognize speech using the specified or best available engine"""
        if not engine:
            engine = self._get_best_available_engine()
        
        if not engine:
            logger.log_error("No speech recognition engine available")
            return ""
        
        try:
            if engine == "whisper" and WHISPER_AVAILABLE and self.whisper_model:
                return self._recognize_with_whisper(audio_data)
            elif engine == "google" and GOOGLE_SR_AVAILABLE and self.sr_recognizer:
                return self._recognize_with_google(audio_data)
            elif engine == "vosk" and VOSK_AVAILABLE and self.model:
                return self._recognize_with_vosk(audio_data)
            else:
                logger.log_error(f"Engine {engine} not available")
                return ""
        except Exception as e:
            logger.log_error(f"Speech recognition error with {engine}", e)
            return ""
    
    def _contains_hotword(self, text):
        """Check if text contains hotword"""
        if not text:
            return False
        
        # Simplified hotword detection
        hotwords = ['hey', 'jarvis', 'hey jarvis']
        text = text.lower().strip()
        
        for hotword in hotwords:
            if hotword in text:
                logger.log_activity(f"Hotword detected: '{hotword}' in '{text}'")
                return True
        return False
    
    def _listen_loop(self):
        """Continuous listening loop"""
        try:
            while self.is_listening:
                if not self.microphone:
                    time.sleep(0.1)
                    continue
                
                try:
                    # Read audio chunk
                    from config import Config
                    data = self.microphone.read(Config.CHUNK_SIZE, exception_on_overflow=False)
                    
                    # Simple volume detection to ignore silence
                    import audioop
                    rms = audioop.rms(data, 2)
                    
                    if rms > 500:  # Noise threshold
                        self.audio_queue.append(data)
                        
                        # Keep reasonable queue size
                        if len(self.audio_queue) > 50:
                            self.audio_queue.popleft()
                    
                except Exception as e:
                    logger.log_error("Error reading audio data", e)
                    time.sleep(0.1)
        
        except Exception as e:
            logger.log_error("Error in listen loop", e)
    
    def _process_audio(self):
        """Process audio queue for speech recognition"""
        try:
            while self.is_listening:
                if len(self.audio_queue) >= 15:  # Process when we have enough audio
                    # Combine audio chunks
                    audio_data = b''.join(list(self.audio_queue))
                    self.audio_queue.clear()
                    
                    if len(audio_data) > 1000:  # Ensure we have meaningful audio
                        # Try speech recognition with fallback engines
                        text = ""
                        
                        # Try preferred engine first
                        if self.preferred_engine == "whisper":
                            text = self.recognize_speech(audio_data, "whisper")
                        elif self.preferred_engine == "google":
                            text = self.recognize_speech(audio_data, "google")
                        else:
                            text = self.recognize_speech(audio_data, "vosk")
                        
                        # Fallback to other engines if needed
                        if not text:
                            for engine in ["whisper", "google", "vosk"]:
                                if engine != self.preferred_engine:
                                    text = self.recognize_speech(audio_data, engine)
                                    if text:
                                        break
                        
                        if text:
                            logger.log_activity(f"Recognized: {text}")
                            
                            # Check for hotword
                            if self._contains_hotword(text):
                                self.hotword_detected = True
                                tts.speak("Yes, I'm listening")
                                logger.log_activity("Hotword detected - JARVIS activated")
                                
                                # Clear the queue and wait for command
                                self.audio_queue.clear()
                                time.sleep(1)  # Brief pause
                                
                                # Listen for actual command
                                command_audio = []
                                start_time = time.time()
                                
                                while time.time() - start_time < 5:  # 5 second timeout
                                    if len(self.audio_queue) > 0:
                                        command_audio.extend(self.audio_queue)
                                        self.audio_queue.clear()
                                    time.sleep(0.1)
                                
                                if command_audio:
                                    command_data = b''.join(command_audio)
                                    command_text = self.recognize_speech(command_data)
                                    
                                    if command_text:
                                        logger.log_activity(f"Command recognized: {command_text}")
                                        # Here you would process the command
                                        tts.speak(f"You said: {command_text}")
                                    else:
                                        tts.speak("Sorry, I didn't catch that")
                                
                                self.hotword_detected = False
                
                time.sleep(0.1)
        
        except Exception as e:
            logger.log_error("Error in audio processing", e)
    
    def start_listening(self):
        """Start listening for speech"""
        if not self.audio_available:
            logger.log_error("Audio not available - cannot start listening")
            return False
        
        if self.is_listening:
            logger.log_activity("Already listening")
            return True
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.process_thread = threading.Thread(target=self._process_audio, daemon=True)
        
        self.listen_thread.start()
        self.process_thread.start()
        
        logger.log_activity("Speech recognition started")
        return True
    
    def stop_listening(self):
        """Stop listening for speech"""
        self.is_listening = False
        
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        if self.process_thread:
            self.process_thread.join(timeout=1)
        
        logger.log_activity("Speech recognition stopped")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_listening()
        
        if self.microphone:
            self.microphone.stop_stream()
            self.microphone.close()
        
        if hasattr(self, 'audio'):
            self.audio.terminate()
        
        logger.log_activity("Speech recognition cleaned up")

# Create instance
enhanced_speech_recognition = EnhancedSpeechRecognition(preferred_engine="google")
