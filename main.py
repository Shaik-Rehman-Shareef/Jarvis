#!/usr/bin/env python3
"""
JARVIS Desktop Assistant
A Windows-based background desktop assistant that behaves like a personal JARVIS.

Features:
- System tray operation (hidden from screen sharing)
- Offline voice recognition using Vosk
- Natural language voice commands
- System-level actions (opening apps, websites, etc.)
- Activity monitoring and logging
- Webcam photo capture
- Email sending capabilities
- Automatic startup with Windows

Author: JARVIS Assistant
Version: 1.0.0
"""

import sys
import os
import signal
import time
import threading
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from logger import logger
from tts import tts
from speech_recognition_safe import speech_recognition
from activity_monitor import activity_monitor
from system_tray import SystemTray
from startup_manager import startup_manager

class JarvisAssistant:
    """Main JARVIS Assistant class"""
    
    def __init__(self):
        self.is_running = False
        self.system_tray = None
        self.setup_signal_handlers()
        
        # Initialize configuration
        Config.ensure_directories()
        Config.load_email_config()
        
        logger.log_startup()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.log_activity(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start JARVIS assistant"""
        if self.is_running:
            return
        
        try:
            self.is_running = True
            
            # Start components
            logger.log_activity("Starting JARVIS components...")
            
            # Start activity monitoring
            activity_monitor.start_monitoring()
            
            # Start speech recognition
            speech_recognition.start_listening()
            
            # Start system tray
            self.system_tray = SystemTray(self)
            self.system_tray.start()
            
            # Try to add to startup if not already there (optional feature)
            try:
                if not startup_manager.is_in_startup():
                    success = startup_manager.add_to_startup()
                    if not success:
                        logger.log_activity("Startup registration failed (non-critical)")
            except Exception as e:
                logger.log_activity(f"Startup registration skipped: {str(e)}")
            
            # Initial greeting
            tts.speak("JARVIS assistant is now active and ready for commands")
            
            logger.log_activity("JARVIS Assistant fully started")
            
            # Keep the main thread alive
            self._main_loop()
            
        except Exception as e:
            logger.log_error("Error starting JARVIS", e)
            self.stop()
    
    def stop(self):
        """Stop JARVIS assistant"""
        if not self.is_running:
            return
        
        try:
            logger.log_activity("Stopping JARVIS components...")
            self.is_running = False
            
            # Stop components
            if hasattr(speech_recognition, 'cleanup'):
                speech_recognition.cleanup()
            
            activity_monitor.stop_monitoring()
            
            if self.system_tray:
                self.system_tray.stop()
            
            logger.log_shutdown()
            
            # Give time for cleanup
            time.sleep(1)
            
            # Exit the application
            sys.exit(0)
            
        except Exception as e:
            logger.log_error("Error stopping JARVIS", e)
            sys.exit(1)
    
    def _main_loop(self):
        """Main application loop"""
        try:
            while self.is_running:
                time.sleep(1)
                
                # Update system tray status periodically
                if self.system_tray:
                    status = self.get_status()
                    self.system_tray.update_icon_tooltip(status)
                
        except KeyboardInterrupt:
            logger.log_activity("Keyboard interrupt received")
            self.stop()
        except Exception as e:
            logger.log_error("Error in main loop", e)
            self.stop()
    
    def get_status(self):
        """Get current status of JARVIS"""
        components_status = []
        
        if speech_recognition.is_listening:
            if speech_recognition.hotword_detected:
                components_status.append("Listening for command")
            else:
                components_status.append("Listening for hotword")
        else:
            components_status.append("Speech recognition offline")
        
        if activity_monitor.is_monitoring:
            components_status.append("Monitoring active")
        else:
            components_status.append("Monitoring offline")
        
        if tts.is_busy():
            components_status.append("Speaking")
        
        return " | ".join(components_status) if components_status else "Ready"
    
    def restart(self):
        """Restart JARVIS assistant"""
        logger.log_activity("Restarting JARVIS...")
        self.stop()
        time.sleep(2)
        self.start()

def main():
    """Main entry point"""
    try:
        # Check if another instance is already running
        import psutil
        current_pid = os.getpid()
        script_name = os.path.basename(__file__)
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] != current_pid:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any(script_name in arg for arg in cmdline):
                        print("JARVIS is already running!")
                        logger.log_activity("Attempted to start second instance - exiting")
                        sys.exit(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Create and start JARVIS
        jarvis = JarvisAssistant()
        jarvis.start()
        
    except Exception as e:
        logger.log_error("Critical error in main", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
