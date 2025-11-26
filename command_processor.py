import os
import subprocess
import webbrowser
import smtplib
import cv2
import pyautogui
import psutil
import time
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from logger import logger
from tts import tts
from config import Config
from conversation_context import conversation_context, jarvis_personality
from advanced_nlp import advanced_nlp

class CommandProcessor:
    """Process voice commands and execute corresponding actions"""
    
    def __init__(self):
        self.last_screenshot_path = None
    
    def process_command(self, command):
        """Main command processing function with conversational intelligence"""
        command = command.lower().strip()
        logger.log_command(command)
        
        # Store original command for context
        original_command = command
        response = None
        
        try:
            # First, try advanced NLP for complex commands
            advanced_response = advanced_nlp.process_complex_command(original_command, self)
            if advanced_response:
                return advanced_response
            
            # Handle conversational commands first
            if self._is_conversational_command(command):
                response = self._handle_conversational_command(command)
            
            # App launching commands
            elif self._is_app_command(command):
                response = self._handle_app_command(command)
            
            # Web commands
            elif self._is_web_command(command):
                response = self._handle_web_command(command)
            
            # Camera commands
            elif self._is_camera_command(command):
                response = self._handle_camera_command(command)
            
            # Email commands
            elif self._is_email_command(command):
                response = self._handle_email_command(command)
            
            # System commands
            elif self._is_system_command(command):
                response = self._handle_system_command(command)
            
            # Screenshot commands
            elif self._is_screenshot_command(command):
                response = self._handle_screenshot_command(command)
            
            # Information commands
            elif self._is_info_command(command):
                response = self._handle_info_command(command)
            
            # Time/Date commands
            elif self._is_time_command(command):
                response = self._handle_time_command(command)
            
            else:
                response = self._handle_unknown_command(command)
                
        except Exception as e:
            logger.log_error(f"Error processing command '{command}'", e)
            response = jarvis_personality.get_error_response()
            tts.speak(response)
        
        # Add interaction to conversation context
        if response:
            conversation_context.add_interaction(original_command, response)
            
            # Offer proactive suggestions occasionally
            suggestion = jarvis_personality.get_proactive_suggestion(conversation_context)
            if suggestion and len(conversation_context.conversation_history) % 3 == 0:  # Every 3rd command
                tts.speak(suggestion)
    
    def _is_conversational_command(self, command):
        """Check if command is conversational"""
        conversational_keywords = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "thanks", "thank you", "bye", "goodbye",
            "who are you", "what can you do", "help", "what time", "what day"
        ]
        return any(keyword in command for keyword in conversational_keywords)
    
    def _handle_conversational_command(self, command):
        """Handle conversational commands with personality"""
        if any(greeting in command for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            response = jarvis_personality.get_greeting()
            tts.speak(response)
            return response
            
        elif any(phrase in command for phrase in ["how are you", "what's up"]):
            responses = [
                "I'm functioning perfectly, thank you for asking.",
                "All systems operational, sir.",
                "Running smoothly, ready to assist.",
                "Quite well, thank you. How may I help you?"
            ]
            import random
            response = random.choice(responses)
            tts.speak(response)
            return response
            
        elif any(phrase in command for phrase in ["thanks", "thank you"]):
            responses = [
                "You're welcome, sir.",
                "My pleasure.",
                "Always happy to help.",
                "At your service."
            ]
            import random
            response = random.choice(responses)
            tts.speak(response)
            return response
            
        elif any(phrase in command for phrase in ["bye", "goodbye"]):
            responses = [
                "Goodbye, sir. I'll be here when you need me.",
                "Until next time.",
                "Farewell. Have a great day.",
                "Goodbye. Standing by for your return."
            ]
            import random
            response = random.choice(responses)
            tts.speak(response)
            return response
            
        elif any(phrase in command for phrase in ["who are you", "what are you"]):
            response = "I'm JARVIS, your virtual assistant. I'm here to help you with various tasks and provide information."
            tts.speak(response)
            return response
            
        elif "what can you do" in command or "help" in command:
            response = "I can help you open applications, browse the web, take screenshots, check system information, tell you the time, and much more. Just ask me!"
            tts.speak(response)
            return response
            
        elif "what time" in command:
            return self._handle_time_command(command)
            
        elif "what day" in command:
            from datetime import datetime
            today = datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {today}"
            tts.speak(response)
            return response
        
        return None
    
    def _is_app_command(self, command):
        """Check if command is to open an application"""
        app_keywords = ["open", "launch", "start", "run"]
        return any(keyword in command for keyword in app_keywords) and \
               any(app in command for app in Config.APPS.keys())
    
    def _handle_app_command(self, command):
        """Handle application launch commands"""
        for app_name, app_executable in Config.APPS.items():
            if app_name in command:
                try:
                    subprocess.Popen(app_executable, shell=True)
                    tts.speak(f"Opening {app_name}")
                    logger.log_system_event("APP_LAUNCH", app_name)
                    return
                except Exception as e:
                    logger.log_error(f"Failed to open {app_name}", e)
                    tts.speak(f"Sorry, I couldn't open {app_name}")
                    return
        
        tts.speak("I couldn't find that application")
    
    def _is_web_command(self, command):
        """Check if command is web-related"""
        web_keywords = ["open", "browse", "go to", "search", "youtube", "google"]
        return any(keyword in command for keyword in web_keywords)
    
    def _handle_web_command(self, command):
        """Handle web browsing commands"""
        try:
            if "youtube" in command:
                if "search" in command or "for" in command:
                    # Extract search query
                    query = self._extract_search_query(command, ["youtube", "search", "for"])
                    if query:
                        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                        webbrowser.open(url)
                        tts.speak(f"Searching YouTube for {query}")
                        logger.log_system_event("WEB_BROWSE", f"YouTube search: {query}")
                else:
                    webbrowser.open("https://www.youtube.com")
                    tts.speak("Opening YouTube")
                    logger.log_system_event("WEB_BROWSE", "YouTube")
            
            elif "google" in command:
                if "search" in command or "for" in command:
                    query = self._extract_search_query(command, ["google", "search", "for"])
                    if query:
                        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                        webbrowser.open(url)
                        tts.speak(f"Searching Google for {query}")
                        logger.log_system_event("WEB_BROWSE", f"Google search: {query}")
                else:
                    webbrowser.open("https://www.google.com")
                    tts.speak("Opening Google")
                    logger.log_system_event("WEB_BROWSE", "Google")
            
            elif "open" in command and ("website" in command or "site" in command):
                # Extract website URL
                url = self._extract_url(command)
                if url:
                    webbrowser.open(url)
                    tts.speak(f"Opening {url}")
                    logger.log_system_event("WEB_BROWSE", url)
                else:
                    tts.speak("Please specify which website to open")
            
            else:
                tts.speak("I'm not sure what you want me to browse")
                
        except Exception as e:
            logger.log_error("Error handling web command", e)
            tts.speak("Sorry, I couldn't open that website")
    
    def _is_camera_command(self, command):
        """Check if command is camera-related"""
        camera_keywords = ["take", "photo", "picture", "capture", "camera", "selfie"]
        return any(keyword in command for keyword in camera_keywords)
    
    def _handle_camera_command(self, command):
        """Handle camera/photo commands"""
        try:
            tts.speak("Taking a photo")
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                tts.speak("Sorry, I couldn't access the camera")
                return
            
            # Give user time to pose
            time.sleep(2)
            
            # Capture frame
            ret, frame = cap.read()
            
            if ret:
                # Save photo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"jarvis_photo_{timestamp}.jpg"
                filepath = os.path.join(Config.LOGS_DIR, filename)
                
                cv2.imwrite(filepath, frame)
                self.last_screenshot_path = filepath
                
                tts.speak("Photo captured successfully")
                logger.log_system_event("PHOTO_CAPTURE", filepath)
            else:
                tts.speak("Failed to capture photo")
            
            cap.release()
            
        except Exception as e:
            logger.log_error("Error taking photo", e)
            tts.speak("Sorry, I couldn't take a photo")
    
    def _is_email_command(self, command):
        """Check if command is email-related"""
        email_keywords = ["send", "email", "mail", "message"]
        return any(keyword in command for keyword in email_keywords)
    
    def _handle_email_command(self, command):
        """Handle email commands"""
        try:
            if not Config.EMAIL_CONFIG.get("sender_email"):
                tts.speak("Email is not configured. Please set up email configuration first.")
                return
            
            if "photo" in command and self.last_screenshot_path:
                self._send_email_with_photo()
            else:
                tts.speak("What would you like the email to say?")
                # For now, send a simple test email
                self._send_simple_email("JARVIS Test Email", "This is a test email from your JARVIS assistant.")
                
        except Exception as e:
            logger.log_error("Error handling email command", e)
            tts.speak("Sorry, I couldn't send the email")
    
    def _send_simple_email(self, subject, body):
        """Send a simple email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_CONFIG["sender_email"]
            msg['To'] = Config.EMAIL_CONFIG["recipient_email"]
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(Config.EMAIL_CONFIG["smtp_server"], Config.EMAIL_CONFIG["smtp_port"])
            server.starttls()
            server.login(Config.EMAIL_CONFIG["sender_email"], Config.EMAIL_CONFIG["sender_password"])
            
            text = msg.as_string()
            server.sendmail(Config.EMAIL_CONFIG["sender_email"], Config.EMAIL_CONFIG["recipient_email"], text)
            server.quit()
            
            tts.speak("Email sent successfully")
            logger.log_system_event("EMAIL_SENT", subject)
            
        except Exception as e:
            logger.log_error("Failed to send email", e)
            tts.speak("Failed to send email")
    
    def _send_email_with_photo(self):
        """Send email with the last captured photo"""
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_CONFIG["sender_email"]
            msg['To'] = Config.EMAIL_CONFIG["recipient_email"]
            msg['Subject'] = "Photo from JARVIS"
            
            msg.attach(MIMEText("Here's a photo captured by JARVIS.", 'plain'))
            
            # Attach photo
            with open(self.last_screenshot_path, "rb") as f:
                img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(self.last_screenshot_path))
                msg.attach(image)
            
            server = smtplib.SMTP(Config.EMAIL_CONFIG["smtp_server"], Config.EMAIL_CONFIG["smtp_port"])
            server.starttls()
            server.login(Config.EMAIL_CONFIG["sender_email"], Config.EMAIL_CONFIG["sender_password"])
            
            text = msg.as_string()
            server.sendmail(Config.EMAIL_CONFIG["sender_email"], Config.EMAIL_CONFIG["recipient_email"], text)
            server.quit()
            
            tts.speak("Photo sent via email successfully")
            logger.log_system_event("EMAIL_SENT", "Photo attachment")
            
        except Exception as e:
            logger.log_error("Failed to send photo email", e)
            tts.speak("Failed to send photo via email")
    
    def _is_system_command(self, command):
        """Check if command is system-related"""
        system_keywords = ["shutdown", "restart", "sleep", "lock", "volume", "minimize", "close"]
        return any(keyword in command for keyword in system_keywords)
    
    def _handle_system_command(self, command):
        """Handle system commands"""
        try:
            if "volume up" in command:
                pyautogui.press('volumeup')
                tts.speak("Volume increased")
                
            elif "volume down" in command:
                pyautogui.press('volumedown')
                tts.speak("Volume decreased")
                
            elif "mute" in command:
                pyautogui.press('volumemute')
                tts.speak("Volume muted")
                
            elif "lock" in command:
                os.system("rundll32.exe user32.dll,LockWorkStation")
                tts.speak("Locking the computer")
                logger.log_system_event("SYSTEM_LOCK", "Computer locked")
                
            elif "sleep" in command:
                tts.speak("Putting computer to sleep")
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                logger.log_system_event("SYSTEM_SLEEP", "Computer sleep")
                
            else:
                tts.speak("I'm not sure about that system command")
                
        except Exception as e:
            logger.log_error("Error handling system command", e)
            tts.speak("Sorry, I couldn't execute that system command")
    
    def _is_screenshot_command(self, command):
        """Check if command is screenshot-related"""
        screenshot_keywords = ["screenshot", "screen capture", "capture screen"]
        return any(keyword in command for keyword in screenshot_keywords)
    
    def _handle_screenshot_command(self, command):
        """Handle screenshot commands"""
        try:
            tts.speak("Taking a screenshot")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jarvis_screenshot_{timestamp}.png"
            filepath = os.path.join(Config.LOGS_DIR, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            self.last_screenshot_path = filepath
            tts.speak("Screenshot saved")
            logger.log_system_event("SCREENSHOT", filepath)
            
        except Exception as e:
            logger.log_error("Error taking screenshot", e)
            tts.speak("Sorry, I couldn't take a screenshot")
    
    def _is_info_command(self, command):
        """Check if command is requesting information"""
        info_keywords = ["what is", "tell me", "system info", "cpu", "memory", "battery"]
        return any(keyword in command for keyword in info_keywords)
    
    def _handle_info_command(self, command):
        """Handle information requests"""
        try:
            if "cpu" in command:
                cpu_percent = psutil.cpu_percent(interval=1)
                tts.speak(f"CPU usage is {cpu_percent} percent")
                
            elif "memory" in command or "ram" in command:
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                tts.speak(f"Memory usage is {memory_percent} percent")
                
            elif "battery" in command:
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        tts.speak(f"Battery is at {battery.percent} percent")
                    else:
                        tts.speak("No battery information available")
                except:
                    tts.speak("No battery information available")
                    
            else:
                tts.speak("What information would you like?")
                
        except Exception as e:
            logger.log_error("Error getting system info", e)
            tts.speak("Sorry, I couldn't get that information")
    
    def _is_time_command(self, command):
        """Check if command is time/date related"""
        time_keywords = ["time", "date", "what time", "what day"]
        return any(keyword in command for keyword in time_keywords)
    
    def _handle_time_command(self, command):
        """Handle time/date commands"""
        try:
            now = datetime.now()
            
            if "time" in command:
                time_str = now.strftime("%I:%M %p")
                tts.speak(f"The time is {time_str}")
                
            elif "date" in command:
                date_str = now.strftime("%B %d, %Y")
                tts.speak(f"Today is {date_str}")
                
        except Exception as e:
            logger.log_error("Error getting time/date", e)
            tts.speak("Sorry, I couldn't get the time")
    
    def _handle_unknown_command(self, command):
        """Handle unrecognized commands with intelligent suggestions"""
        # Try to provide helpful suggestions
        suggestions = []
        
        # Check for similar commands
        if "open" in command:
            suggestions.append("I can open applications like Chrome, Notepad, or Calculator.")
        elif "search" in command:
            suggestions.append("I can search on Google or YouTube.")
        elif "screenshot" in command or "capture" in command:
            suggestions.append("I can take screenshots for you.")
        elif "time" in command or "date" in command:
            suggestions.append("I can tell you the current time or date.")
        elif "system" in command or "computer" in command:
            suggestions.append("I can check system information like CPU usage or battery status.")
        
        # Use personality-based clarification
        if suggestions:
            response = jarvis_personality.get_clarification_request(command)
            response += f" For example, {suggestions[0]}"
        else:
            response = jarvis_personality.get_clarification_request(command)
            response += " You can ask me to open apps, search the web, take screenshots, or get system information."
        
        tts.speak(response)
        logger.log_command(command, success=False)
        return response
    
    def _extract_search_query(self, command, keywords_to_remove):
        """Extract search query from command"""
        query = command
        for keyword in keywords_to_remove:
            query = query.replace(keyword, "")
        return query.strip()
    
    def _extract_url(self, command):
        """Extract URL from command"""
        # Simple URL extraction - could be improved
        url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[^\s]+\.(com|org|net|edu|gov))'
        matches = re.findall(url_pattern, command)
        if matches:
            url = matches[0] if isinstance(matches[0], str) else matches[0][0]
            if not url.startswith('http'):
                url = 'http://' + url
            return url
        return None

# Global command processor instance
command_processor = CommandProcessor()

def process_command(command):
    """Global function to process commands"""
    command_processor.process_command(command)
