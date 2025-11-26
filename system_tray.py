import pystray
import PIL.Image
import threading
import os
import sys
from logger import logger

class SystemTray:
    """System tray interface for JARVIS"""
    
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.icon = None
        self.is_running = False
        self._create_icon()
    
    def _create_icon(self):
        """Create system tray icon"""
        try:
            from config import Config
            
            # Try to load custom icon, fall back to default if not found
            try:
                image = PIL.Image.open(Config.ICON_PATH)
            except:
                # Create a simple default icon
                image = self._create_default_icon()
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("JARVIS Assistant", self._show_status, default=True),
                pystray.MenuItem("Status", self._show_status),
                pystray.MenuItem("View Logs", self._open_logs),
                pystray.MenuItem("Configure Email", self._configure_email),
                pystray.MenuItem("---", None),
                pystray.MenuItem("Exit", self._quit_application)
            )
            
            self.icon = pystray.Icon("JARVIS", image, "JARVIS Assistant", menu)
            
        except Exception as e:
            logger.log_error("Error creating system tray icon", e)
    
    def _create_default_icon(self):
        """Create a default icon if custom icon is not available"""
        # Create a simple 64x64 icon with "J" text
        image = PIL.Image.new('RGBA', (64, 64), (0, 100, 200, 255))
        
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            
            # Try to use a system font
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            # Draw "J" in the center
            bbox = draw.textbbox((0, 0), "J", font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (64 - text_width) // 2
            y = (64 - text_height) // 2
            
            draw.text((x, y), "J", fill=(255, 255, 255, 255), font=font)
            
        except Exception:
            # If text drawing fails, just use solid color
            pass
        
        return image
    
    def start(self):
        """Start the system tray"""
        if self.icon and not self.is_running:
            self.is_running = True
            # Run in separate thread to avoid blocking
            tray_thread = threading.Thread(target=self.icon.run, daemon=True)
            tray_thread.start()
            logger.log_activity("System tray started")
    
    def update_status(self, status):
        """Update the tray icon tooltip with current status"""
        if self.icon:
            status_messages = {
                "listening": "JARVIS - Listening for 'Hey Jarvis'",
                "processing": "JARVIS - Processing command...",
                "speaking": "JARVIS - Speaking response",
                "ready": "JARVIS - Ready for commands"
            }
            tooltip = status_messages.get(status, f"JARVIS - {status}")
            self.icon.title = tooltip
    
    def stop(self):
        """Stop the system tray"""
        if self.icon and self.is_running:
            self.icon.stop()
            self.is_running = False
            logger.log_activity("System tray stopped")
    
    def _show_status(self, icon=None, item=None):
        """Show JARVIS status"""
        try:
            status = self.jarvis.get_status()
            
            # For now, just log the status. In a full implementation,
            # you might want to show a small popup or notification
            logger.log_activity(f"Status requested: {status}")
            
            # Could implement a simple message box here
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                messagebox.showinfo("JARVIS Status", status)
                root.destroy()
                
            except Exception:
                # Fallback if tkinter is not available
                pass
                
        except Exception as e:
            logger.log_error("Error showing status", e)
    
    def _open_logs(self, icon=None, item=None):
        """Open logs directory"""
        try:
            from config import Config
            import subprocess
            
            # Open logs directory in file explorer
            subprocess.Popen(f'explorer "{Config.LOGS_DIR}"')
            logger.log_activity("Logs directory opened")
            
        except Exception as e:
            logger.log_error("Error opening logs", e)
    
    def _configure_email(self, icon=None, item=None):
        """Open email configuration dialog"""
        try:
            # Simple email configuration using tkinter
            import tkinter as tk
            from tkinter import simpledialog, messagebox
            from config import Config
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Get email configuration
            sender_email = simpledialog.askstring(
                "Email Configuration", 
                "Enter sender email address:",
                initialvalue=Config.EMAIL_CONFIG.get("sender_email", "")
            )
            
            if sender_email:
                sender_password = simpledialog.askstring(
                    "Email Configuration", 
                    "Enter email password (for app-specific password):",
                    show='*'
                )
                
                if sender_password:
                    recipient_email = simpledialog.askstring(
                        "Email Configuration", 
                        "Enter recipient email address:",
                        initialvalue=Config.EMAIL_CONFIG.get("recipient_email", "")
                    )
                    
                    if recipient_email:
                        # Save configuration
                        email_config = {
                            "smtp_server": "smtp.gmail.com",
                            "smtp_port": 587,
                            "sender_email": sender_email,
                            "sender_password": sender_password,
                            "recipient_email": recipient_email
                        }
                        
                        Config.save_email_config(email_config)
                        messagebox.showinfo("Success", "Email configuration saved!")
                        logger.log_activity("Email configuration updated")
            
            root.destroy()
            
        except Exception as e:
            logger.log_error("Error configuring email", e)
    
    def _quit_application(self, icon=None, item=None):
        """Quit the application"""
        try:
            logger.log_activity("Quit requested from system tray")
            self.jarvis.stop()
            
        except Exception as e:
            logger.log_error("Error quitting application", e)
    
    def update_icon_tooltip(self, status):
        """Update the icon tooltip with current status"""
        if self.icon:
            self.icon.title = f"JARVIS Assistant - {status}"
