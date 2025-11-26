import threading
import os
import io
import json
import time
from logger import logger

try:
    import pyttsx3  # Local engine fallback
except Exception:
    pyttsx3 = None

try:
    import requests  # For ElevenLabs HTTP API
except Exception:
    requests = None

class TextToSpeech:
    """Hybrid TTS: ElevenLabs (if API key present) with pyttsx3 fallback."""

    def __init__(self):
        from config import Config
        self.config = Config
        self.primary_engine = None        # 'elevenlabs' or 'pyttsx3'
        self.local_engine = None          # pyttsx3 instance
        self.is_speaking = False
        self.lock = threading.Lock()
        self.session = None               # requests session
        self._init_engines()
    
    def _init_engines(self):
        """Initialize preferred engine order."""
        order = self.config.TTS_ENGINE_ORDER
        api_key = self.config.ELEVENLABS_API_KEY.strip()
        for engine in order:
            if engine == "elevenlabs":
                if api_key and requests:
                    self.primary_engine = "elevenlabs"
                    self.session = requests.Session()
                    logger.log_activity("ElevenLabs TTS enabled")
                    return
            if engine == "pyttsx3":
                if pyttsx3:
                    try:
                        self.local_engine = pyttsx3.init()
                        self._configure_pyttsx3()
                        self.primary_engine = self.primary_engine or "pyttsx3"
                        return
                    except Exception as e:
                        logger.log_error("Failed initializing pyttsx3", e)
        logger.log_error("No TTS engine available (missing API key and pyttsx3)")

    def _configure_pyttsx3(self):
        """Configure local pyttsx3 engine."""
        if not self.local_engine:
            return
        self.local_engine.setProperty('rate', self.config.VOICE_RATE)
        self.local_engine.setProperty('volume', self.config.VOICE_VOLUME)
        try:
            voices = self.local_engine.getProperty('voices')
            chosen = None
            for pref in ("david", "zira"):
                for v in voices:
                    if pref in v.name.lower():
                        self.local_engine.setProperty('voice', v.id)
                        chosen = v.name
                        break
                if chosen:
                    break
            if not chosen and voices:
                self.local_engine.setProperty('voice', voices[0].id)
                chosen = voices[0].name
            logger.log_activity(f"pyttsx3 voice: {chosen}")
        except Exception:
            pass
        logger.log_activity("Local pyttsx3 TTS ready")

    # ---------------- ElevenLabs Handling ---------------- #
    def _speak_elevenlabs(self, text: str):
        from config import Config
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{Config.ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": Config.ELEVENLABS_API_KEY,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": Config.ELEVENLABS_MODEL_ID,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        r = self.session.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"ElevenLabs API error {r.status_code}: {r.text[:120]}")
        audio_bytes = r.content
        self._play_audio_bytes(audio_bytes)

    def _play_audio_bytes(self, data: bytes):
        """Play MP3/decoded audio bytes using simpletempfile + playsound fallback."""
        # Minimal dependency playback to avoid adding heavy libs: use temp file + winsound (wav only) OR playsound.
        import tempfile, os
        # ElevenLabs returns MP3. Try playsound if available; else attempt pydub conversion if installed.
        try:
            from playsound import playsound  # type: ignore
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                f.write(data)
                temp_path = f.name
            playsound(temp_path)
        except Exception as e:
            logger.log_error("Playback failure for ElevenLabs audio", e)
        finally:
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
    
    def speak(self, text, blocking=False):
        """Speak text via preferred engine with fallback."""
        if not text:
            return

        def _do_speak():
            with self.lock:
                self.is_speaking = True
                try:
                    engine_used = None
                    if self.primary_engine == "elevenlabs":
                        try:
                            logger.log_activity(f"Speaking (ElevenLabs): {text}")
                            self._speak_elevenlabs(text)
                            engine_used = "elevenlabs"
                        except Exception as e:
                            logger.log_error("ElevenLabs failed, falling back", e)
                    if engine_used is None:
                        if self.local_engine:
                            logger.log_activity(f"Speaking (pyttsx3): {text}")
                            self.local_engine.say(text)
                            self.local_engine.runAndWait()
                        else:
                            logger.log_error("No TTS engine available to speak", None)
                finally:
                    self.is_speaking = False

        if blocking:
            _do_speak()
        else:
            threading.Thread(target=_do_speak, daemon=True).start()
    
    def stop(self):
        """Attempt to stop local engine speech."""
        try:
            if self.local_engine and self.is_speaking:
                self.local_engine.stop()
                self.is_speaking = False
        except Exception as e:
            logger.log_error("Error stopping speech", e)
    
    def is_busy(self):
        return self.is_speaking

# Global TTS instance
tts = TextToSpeech()
