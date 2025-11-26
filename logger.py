import logging
import os
from datetime import datetime
from config import Config

class Logger:
    """Centralized logging system for JARVIS"""
    
    def __init__(self):
        # Ensure logs directory exists
        Config.ensure_directories()
        
        # Setup activity logger
        self.activity_logger = logging.getLogger('jarvis_activity')
        self.activity_logger.setLevel(logging.INFO)
        
        activity_handler = logging.FileHandler(Config.ACTIVITY_LOG_FILE, encoding='utf-8')
        activity_formatter = logging.Formatter('%(asctime)s - %(message)s')
        activity_handler.setFormatter(activity_formatter)
        self.activity_logger.addHandler(activity_handler)
        
        # Setup error logger
        self.error_logger = logging.getLogger('jarvis_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(Config.ERROR_LOG_FILE, encoding='utf-8')
        error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Console logger for debugging
        self.console_logger = logging.getLogger('jarvis_console')
        self.console_logger.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.console_logger.addHandler(console_handler)
    
    def log_activity(self, message):
        """Log user activity"""
        self.activity_logger.info(message)
        self.console_logger.info(f"ACTIVITY: {message}")
    
    def log_error(self, message, exception=None):
        """Log errors"""
        if exception:
            message = f"{message}: {str(exception)}"
        self.error_logger.error(message)
        self.console_logger.error(f"ERROR: {message}")
    
    def log_command(self, command, success=True):
        """Log voice commands"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Voice command executed - '{command}' - {status}"
        self.log_activity(message)
    
    def log_system_event(self, event_type, details):
        """Log system events like app launches, web browsing, etc."""
        message = f"System Event: {event_type} - {details}"
        self.log_activity(message)
    
    def log_startup(self):
        """Log JARVIS startup"""
        self.log_activity("JARVIS Assistant started")
    
    def log_shutdown(self):
        """Log JARVIS shutdown"""
        self.log_activity("JARVIS Assistant stopped")

# Global logger instance
logger = Logger()
