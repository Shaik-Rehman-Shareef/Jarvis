import psutil
import time
import threading
from datetime import datetime
from logger import logger

class ActivityMonitor:
    """Monitor user activity and system events"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_active_window = None
        self.active_processes = set()
        self.monitoring_interval = 30  # seconds
    
    def start_monitoring(self):
        """Start activity monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.log_activity("Activity monitoring started")
    
    def stop_monitoring(self):
        """Stop activity monitoring"""
        self.is_monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        logger.log_activity("Activity monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                self._check_running_processes()
                self._log_system_status()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.log_error("Error in activity monitoring", e)
                time.sleep(self.monitoring_interval)
    
    def _check_running_processes(self):
        """Check for new or closed processes"""
        try:
            current_processes = set()
            
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name']
                    current_processes.add(proc_name)
                    
                    # Check for newly started processes
                    if proc_name not in self.active_processes:
                        # Only log significant applications (not system processes)
                        if self._is_significant_process(proc_name):
                            logger.log_system_event("PROCESS_STARTED", proc_name)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for closed processes
            closed_processes = self.active_processes - current_processes
            for proc_name in closed_processes:
                if self._is_significant_process(proc_name):
                    logger.log_system_event("PROCESS_CLOSED", proc_name)
            
            self.active_processes = current_processes
            
        except Exception as e:
            logger.log_error("Error checking processes", e)
    
    def _is_significant_process(self, process_name):
        """Determine if a process is significant enough to log"""
        # List of significant applications to monitor
        significant_apps = [
            'chrome.exe', 'firefox.exe', 'edge.exe', 'opera.exe',
            'notepad.exe', 'notepad++.exe', 'code.exe', 'devenv.exe',
            'winword.exe', 'excel.exe', 'powerpnt.exe',
            'vlc.exe', 'spotify.exe', 'steam.exe',
            'discord.exe', 'skype.exe', 'zoom.exe',
            'photoshop.exe', 'illustrator.exe',
            'cmd.exe', 'powershell.exe',
            'calculator.exe', 'mspaint.exe'
        ]
        
        return process_name.lower() in [app.lower() for app in significant_apps]
    
    def _log_system_status(self):
        """Log periodic system status"""
        try:
            # CPU and Memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('C:')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network activity
            network = psutil.net_io_counters()
            
            status_message = (
                f"System Status - CPU: {cpu_percent}%, "
                f"Memory: {memory.percent}%, "
                f"Disk: {disk_percent:.1f}%, "
                f"Network: {self._bytes_to_mb(network.bytes_sent)}MB sent, "
                f"{self._bytes_to_mb(network.bytes_recv)}MB received"
            )
            
            logger.log_system_event("SYSTEM_STATUS", status_message)
            
        except Exception as e:
            logger.log_error("Error logging system status", e)
    
    def _bytes_to_mb(self, bytes_value):
        """Convert bytes to megabytes"""
        return round(bytes_value / (1024 * 1024), 2)
    
    def log_web_activity(self, url, title=""):
        """Log web browsing activity"""
        activity = f"Web Activity - URL: {url}"
        if title:
            activity += f", Title: {title}"
        logger.log_system_event("WEB_ACTIVITY", activity)
    
    def log_file_activity(self, action, filepath):
        """Log file operations"""
        logger.log_system_event("FILE_ACTIVITY", f"{action}: {filepath}")
    
    def log_app_usage(self, app_name, action):
        """Log application usage"""
        logger.log_system_event("APP_USAGE", f"{app_name} - {action}")

# Global activity monitor instance
activity_monitor = ActivityMonitor()
