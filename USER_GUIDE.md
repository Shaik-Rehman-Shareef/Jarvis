# JARVIS Desktop Assistant - User Guide

## Quick Start

### 1. Installation
```bash
# Option 1: Run installer (Windows)
install.bat

# Option 2: Manual setup
pip install -r requirements.txt
python setup.py
```

### 2. Download Speech Model
- Go to: https://alphacephei.com/vosk/models/
- Download: `vosk-model-en-us-0.22.zip` (about 50MB)
- Extract to: `models/vosk-model-en-us-0.22/`

### 3. Test Setup
```bash
python test_system.py
```

### 4. Start JARVIS
```bash
python main.py
```

## Voice Commands

### Basic Usage
1. Say "**Jarvis**" (hotword)
2. Wait for confirmation beep/response
3. Give your command
4. JARVIS will execute and respond

### Application Commands
- "Jarvis, open Chrome"
- "Jarvis, launch Notepad"
- "Jarvis, start Calculator"
- "Jarvis, open File Explorer"
- "Jarvis, run Task Manager"

### Web Commands
- "Jarvis, open Google"
- "Jarvis, search YouTube for cats"
- "Jarvis, go to website github.com"
- "Jarvis, browse Facebook"

### System Commands
- "Jarvis, what time is it?"
- "Jarvis, what's the date?"
- "Jarvis, check CPU usage"
- "Jarvis, check memory"
- "Jarvis, volume up"
- "Jarvis, volume down"
- "Jarvis, mute"
- "Jarvis, lock computer"

### Media Commands
- "Jarvis, take a photo"
- "Jarvis, take a screenshot"
- "Jarvis, capture screen"

### Email Commands (requires setup)
- "Jarvis, send email"
- "Jarvis, send photo" (sends last captured photo)

## Configuration

### Email Setup
1. Right-click JARVIS system tray icon
2. Select "Configure Email"
3. Enter your email credentials

**For Gmail:**
- Use App Password (not your regular password)
- Enable 2-factor authentication
- Generate App Password in Google Account settings

### Startup Configuration
JARVIS automatically adds itself to Windows startup on first run.

To manually control:
- Enable startup: The system tray has this option
- Disable startup: Remove from Windows Startup folder

## System Tray Options

Right-click the JARVIS icon in system tray:
- **Status**: View current JARVIS status
- **View Logs**: Open logs directory
- **Configure Email**: Setup email functionality
- **Exit**: Stop JARVIS

## Logs and Monitoring

JARVIS creates daily logs in the `logs/` directory:

### Activity Logs
`jarvis_activity_YYYYMMDD.txt`
- Voice commands executed
- Applications launched
- System events
- Web browsing activity

### Error Logs
`jarvis_errors_YYYYMMDD.txt`
- Error messages
- Failed commands
- System issues

## Troubleshooting

### "Hotword not detected"
- **Speak clearly** and close to microphone
- **Check background noise** - use in quiet environment
- **Verify microphone** is working and set as default
- **Check Vosk model** is properly installed

### "Commands not working"
- **Wait for confirmation** after saying "Jarvis"
- **Speak naturally** - don't rush
- **Check supported commands** in this guide
- **View error logs** for specific issues

### "Speech recognition not working"
- **Verify Vosk model** path: `models/vosk-model-en-us-0.22/`
- **Check microphone permissions** in Windows settings
- **Test with different microphone** if available
- **Restart JARVIS** (Exit and run again)

### "Email not sending"
- **Configure email** via system tray menu
- **Use App Password** for Gmail (not regular password)
- **Check internet connection**
- **Verify SMTP settings** are correct

### "High CPU usage"
- **Normal during speech recognition** when listening
- **Check activity logs** for errors causing loops
- **Restart JARVIS** if issues persist

### "Missing dependencies"
```bash
pip install -r requirements.txt --upgrade
```

### "Python errors"
- **Use Python 3.8+**
- **Install in virtual environment** if needed:
```bash
python -m venv jarvis_env
jarvis_env\Scripts\activate
pip install -r requirements.txt
```

## Performance Tips

### Optimal Environment
- **Quiet room** for better speech recognition
- **Clear speech** at normal pace
- **Quality microphone** for best results
- **Stable internet** for web commands

### Resource Usage
- JARVIS uses ~50-100MB RAM normally
- CPU spikes during speech processing (normal)
- Disk usage grows with logs over time

### Battery (Laptops)
- Speech recognition uses more battery
- Consider using when plugged in for extended use

## Security & Privacy

### Data Privacy
- **All processing is local** - no cloud services
- **No data sent externally** except for web commands
- **Activity logs stay on your computer**
- **No recording storage** - only real-time processing

### Email Security
- **Credentials stored locally** in encrypted form
- **Use App Passwords** rather than main passwords
- **Email config file** can be deleted anytime

### System Access
- JARVIS can control system functions (by design)
- **Only responds to authenticated voice commands**
- **No remote access** or external control

## Advanced Usage

### Custom Commands
Edit `command_processor.py` to add new voice commands.

### Building Executable
```bash
python build.py
```
Creates standalone `JARVIS.exe` in `dist/` folder.

### Running at Different Startups
- **User startup**: Default behavior
- **System startup**: Run as Administrator and move to System startup folder

### Multiple Users
Each Windows user account needs separate JARVIS installation.

## Support

### Getting Help
1. **Check error logs** first
2. **Run test script**: `python test_system.py`
3. **Review this guide** for common issues
4. **Check project documentation**

### Reporting Issues
Include:
- Error logs (`logs/jarvis_errors_*.txt`)
- System information (Windows version, Python version)
- Steps to reproduce the issue
- What you expected vs. what happened

## License & Credits

- **Open Source**: MIT License
- **Built with**: Python, Vosk, PyTTS3, and other open-source libraries
- **Free to use**: No subscriptions or cloud fees
