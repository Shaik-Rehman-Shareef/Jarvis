# JARVIS Desktop Assistant

A Windows-based background desktop assistant that behaves like a personal JARVIS, built with Python and completely offline.(Still under dev)

## Features

 **System Tray Operation**: Runs hidden in system tray, invisible during screen sharing
 **Offline Voice Recognition**: Uses Vosk for local speech recognition
 **Hotword Detection**: Activates with "Jarvis" command
 **Natural Language Commands**: Accepts voice commands for various tasks
 **System Integration**: Opens apps, websites, takes photos, sends emails
 **Activity Monitoring**: Logs user activity and system events
 **Automatic Startup**: Launches with Windows
 **100% Free & Open Source**: No cloud dependencies

## Prerequisites

1. **Python 3.8+** installed on Windows
2. **Vosk Model**: Download the English model from [Vosk Models](https://alphacephei.com/vosk/models/)
   - Download `vosk-model-en-us-0.22.zip`
   - Extract to `models/vosk-model-en-us-0.22/` in the project directory

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd Jarvis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download Vosk Model**
   - Create a `models` directory in the project folder
   - Download and extract the Vosk model to `models/vosk-model-en-us-0.22/`

4. **Run JARVIS**
   ```bash
   python main.py
   ```

## Voice Commands

JARVIS responds to the hotword "Jarvis" followed by commands:

### Application Commands
- "Jarvis, open Chrome"
- "Jarvis, launch Notepad"
- "Jarvis, start Calculator"

### Web Commands
- "Jarvis, open Google"
- "Jarvis, search YouTube for music"
- "Jarvis, go to website example.com"

### System Commands
- "Jarvis, take a photo"
- "Jarvis, take a screenshot"
- "Jarvis, volume up"
- "Jarvis, lock computer"

### Information Commands
- "Jarvis, what time is it?"
- "Jarvis, what's the date?"
- "Jarvis, check CPU usage"
- "Jarvis, check memory usage"

### Email Commands
- "Jarvis, send email" (requires email configuration)

## Configuration

### Email Setup
Right-click the system tray icon → "Configure Email" to set up email functionality.

### Supported Applications
- Chrome, Firefox, Edge
- Notepad, Visual Studio Code
- Calculator, Paint
- File Explorer, Task Manager
- Command Prompt, PowerShell
- And many more...

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/jarvis_icon.ico main.py
```

## Project Structure

```
Jarvis/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── logger.py              # Logging system
├── tts.py                 # Text-to-speech
├── speech_recognition.py  # Voice recognition
├── command_processor.py   # Command processing
├── activity_monitor.py    # Activity monitoring
├── system_tray.py         # System tray interface
├── startup_manager.py     # Windows startup management
├── requirements.txt       # Python dependencies
├── logs/                  # Activity and error logs
├── models/                # Vosk speech models
└── assets/                # Icons and resources
```

## Logs

JARVIS logs all activities to:
- `logs/jarvis_activity_YYYYMMDD.txt` - User activities and system events
- `logs/jarvis_errors_YYYYMMDD.txt` - Error logs

## Privacy & Security

- **Completely Offline**: No data sent to external servers
- **Local Processing**: All speech recognition happens locally
- **Activity Logging**: Only logs to local files
- **Open Source**: Full source code available for audit

## Troubleshooting

### Common Issues

1. **"Vosk model not found"**
   - Download the Vosk model and place it in `models/vosk-model-en-us-0.22/`

2. **"Microphone not working"**
   - Check Windows microphone permissions
   - Ensure microphone is set as default input device

3. **"Speech not recognized"**
   - Speak clearly and close to microphone
   - Check background noise levels
   - Verify Vosk model is properly installed

4. **"Email not working"**
   - Configure email settings via system tray menu
   - Use app-specific passwords for Gmail

### Dependencies Issues
If you encounter import errors, install missing packages:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## System Requirements

- Windows 10 or later
- Python 3.8+
- Microphone (built-in, USB, or Bluetooth)
- Speakers or headphones
- 4GB RAM minimum
- 1GB free disk space

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Disclaimer

This software is provided as-is for educational and personal use. Users are responsible for complying with local laws and regulations regarding voice recording and system automation.
