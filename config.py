import json
import os
from datetime import datetime

class Config:
    """Configuration settings for JARVIS assistant"""
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    
    # Voice settings
    HOTWORD = "jarvis"
    VOICE_RATE = 150      # Working rate from test
    VOICE_VOLUME = 0.5    # Working volume from test

    # ElevenLabs (cloud TTS) integration
    # Set environment variable ELEVENLABS_API_KEY with your key to enable.
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
    # Default public voice IDs can be replaced by user preference.
    # Example voices (as of documentation): Rachel: 21m00Tcm4TlvDq8ikWAM, Adam: pNInz6obpgDQGcFmaJgB
    ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    ELEVENLABS_MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_monolingual_v1")
    # Engine priority order: 'elevenlabs', then fallback 'pyttsx3'
    TTS_ENGINE_ORDER = ["elevenlabs", "pyttsx3"]
    
    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 8192
    
    # Vosk model (download if not exists)
    VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    VOSK_MODEL_PATH = os.path.join(MODELS_DIR, "vosk-model-en-us-0.22")
    
    # System tray icon
    ICON_PATH = os.path.join(ASSETS_DIR, "jarvis_icon.ico")
    
    # Activity monitoring
    ACTIVITY_LOG_FILE = os.path.join(LOGS_DIR, f"jarvis_activity_{datetime.now().strftime('%Y%m%d')}.txt")
    ERROR_LOG_FILE = os.path.join(LOGS_DIR, f"jarvis_errors_{datetime.now().strftime('%Y%m%d')}.txt")
    
    # Email settings (can be configured by user)
    EMAIL_CONFIG = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "",
        "sender_password": "",
        "recipient_email": ""
    }
    
    # Common applications
    APPS = {
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "file explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe"
    }
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.LOGS_DIR, cls.ASSETS_DIR, cls.MODELS_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def load_email_config(cls):
        """Load email configuration from file if exists"""
        config_file = os.path.join(cls.BASE_DIR, "email_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    cls.EMAIL_CONFIG.update(json.load(f))
            except Exception:
                pass
    
    @classmethod
    def save_email_config(cls, config):
        """Save email configuration to file"""
        config_file = os.path.join(cls.BASE_DIR, "email_config.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            cls.EMAIL_CONFIG.update(config)
        except Exception:
            pass
