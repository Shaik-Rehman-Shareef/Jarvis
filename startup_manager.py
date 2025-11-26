import winshell
import os
import sys
import winreg
from logger import logger

class StartupManager:
    """Manage application startup with Windows (robust version)
    Tries Startup folder shortcut first, then HKCU Run key as fallback.
    """
    
    def __init__(self):
        self.app_name = "JARVIS Assistant"
        try:
            self.startup_folder = winshell.startup()
        except Exception as e:
            logger.log_error("Failed to get Startup folder", e)
            self.startup_folder = None
        self.shortcut_path = os.path.join(self.startup_folder, f"{self.app_name}.lnk") if self.startup_folder else None
        self.run_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def _get_script_and_python(self):
        """Return (exe_path, arguments, working_dir, frozen) properly quoted."""
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            arguments = ''
            working_dir = os.path.dirname(sys.executable)
            return exe_path, arguments, working_dir, True
        # Running as script
        python_exe = sys.executable
        # Prefer pythonw.exe if available for silent startup
        python_dir = os.path.dirname(python_exe)
        pythonw_candidate = os.path.join(python_dir, 'pythonw.exe')
        if os.path.exists(pythonw_candidate):
            python_exe = pythonw_candidate
        main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        exe_path = python_exe
        arguments = f'"{main_script}"'
        working_dir = os.path.dirname(main_script)
        return exe_path, arguments, working_dir, False
    
    def _sanitize(self, path):
        return f'"{path}"' if ' ' in path and not path.startswith('"') else path
    
    def add_to_startup(self):
        """Add JARVIS to Windows startup using shortcut, fallback to Run key."""
        exe_path, arguments, working_dir, frozen = self._get_script_and_python()
        exe_path = self._sanitize(exe_path)
        try:
            if self.startup_folder and self.shortcut_path:
                logger.log_activity(f"Creating startup shortcut: {self.shortcut_path}")
                with winshell.shortcut(self.shortcut_path) as shortcut:
                    shortcut.path = exe_path.strip('"')  # winshell handles quoting
                    if arguments:
                        shortcut.arguments = arguments
                    shortcut.description = "JARVIS Desktop Assistant"
                    shortcut.working_directory = working_dir
                if os.path.exists(self.shortcut_path):
                    logger.log_activity("Added to Windows startup via shortcut")
                    return True
            else:
                logger.log_activity("Startup folder unavailable, skipping shortcut creation")
        except Exception as e:
            logger.log_error("Shortcut creation failed", e)
        # Fallback: registry Run key
        try:
            full_cmd = f"{exe_path} {arguments}".strip()
            logger.log_activity(f"Adding Run key value: {full_cmd}")
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.run_key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, full_cmd)
            logger.log_activity("Added to Windows startup via Run registry key")
            return True
        except Exception as e:
            logger.log_error("Failed to add to startup (all methods)", e)
            return False
    
    def remove_from_startup(self):
        """Remove JARVIS from Windows startup (both shortcut and registry)."""
        removed_any = False
        # Remove shortcut
        try:
            if self.shortcut_path and os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)
                logger.log_activity("Removed startup shortcut")
                removed_any = True
        except Exception as e:
            logger.log_error("Failed to remove startup shortcut", e)
        # Remove Run key value
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.run_key_path, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, self.app_name)
                    logger.log_activity("Removed Run key entry")
                    removed_any = True
                except FileNotFoundError:
                    pass
        except Exception as e:
            logger.log_error("Failed accessing Run key for removal", e)
        return removed_any
    
    def is_in_startup(self):
        """Check if present either as shortcut or registry Run entry."""
        shortcut_exists = self.shortcut_path and os.path.exists(self.shortcut_path)
        run_exists = False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.run_key_path, 0, winreg.KEY_READ) as key:
                try:
                    winreg.QueryValueEx(key, self.app_name)
                    run_exists = True
                except FileNotFoundError:
                    run_exists = False
        except Exception:
            pass
        return shortcut_exists or run_exists
    
    def toggle_startup(self):
        if self.is_in_startup():
            return self.remove_from_startup()
        return self.add_to_startup()

# Global startup manager instance
startup_manager = StartupManager()
