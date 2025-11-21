# School Gate Monitoring System

A comprehensive RFID-based school gate monitoring system with face detection, database logging, and email notifications.

## Features

- **RFID Tag Reading**: Automatically detects student entry/exit via RFID tags
- **Face Detection**: Verifies student presence using webcam
- **Database Logging**: Stores all events in SQLite database
- **Email Notifications**: Sends real-time alerts to parents/guardians
- **GUI Interface**: User-friendly Tkinter-based interface
- **Duplicate Prevention**: Ignores repeated scans within 5 seconds
- **Active Student Tracking**: Shows who's currently inside the school

## Requirements

### Hardware
- RFID reader (USB/Serial connection)
- Webcam (built-in or USB)
- Computer running Windows/Linux/Mac

### Software Dependencies

Install required Python packages:

```bash
pip install pyserial opencv-python
```

## Installation

1. **Clone or download the project files**

2. **Download Haar Cascade file**
   - The system will try to use OpenCV's built-in cascade if the file is missing
   - Or download manually from: https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml

3. **Configure the system**

   Edit `config.py` with your settings:

   ```python
   # Email settings (use Gmail App Password, not regular password)
   EMAIL_SENDER = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_16_char_app_password"
   
   # Map student RFID tags to parent emails
   EMAIL_RECIPIENTS = {
       "04A1B2C3": "parent1@example.com",
       "04B2C3D4": "parent2@example.com",
   }
   
   # Serial port (check your device manager)
   SERIAL_PORT = 'COM3'  # Windows
   # SERIAL_PORT = '/dev/ttyUSB0'  # Linux
   # SERIAL_PORT = '/dev/cu.usbserial-XXX'  # Mac
   ```

4. **Set up Gmail App Password**
   - Go to your Google Account settings
   - Enable 2-Step Verification
   - Generate an App Password for "Mail"
   - Use this 16-character password in config.py

## Usage

1. **Run the application**
   ```bash
   python main.py
   ```

2. **Operation**
   - The system starts in "Waiting for scan" mode
   - When an RFID tag is scanned:
     - System detects if the student is entering or exiting
     - Webcam captures image and checks for face
     - If face detected, logs the event and sends email
     - Updates the active students list
     - If no face, prompts to try again

3. **GUI Features**
   - **Activity Log**: Shows all scan events and system messages
   - **Active Students**: Lists students currently inside
   - **Clear Log Display**: Clears the activity log view
   - **Reset Active List**: Clears the active students list

## File Structure

```
PythonProject/
├── main.py              # Main application
├── config.py            # Configuration settings
├── rfid_handler.py      # RFID reader functions
├── face_detector.py     # Face detection functions
├── logger.py            # Database operations
├── email_sender.py      # Email notification functions
├── school_gate.db       # SQLite database (auto-created)
└── haarcascade_frontalface_default.xml  # Face detection model
```

## Troubleshooting

### RFID Reader Not Detected
- Check the serial port in Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac)
- Update `SERIAL_PORT` in config.py
- Verify baudrate matches your device (usually 9600)
- Check USB cable and connections

### Camera Not Working
- Ensure webcam is connected and not in use by another application
- Try changing camera index in face_detector.py from 0 to 1
- Grant camera permissions to Python/Terminal

### Email Not Sending
- Verify Gmail App Password is correct (not regular password)
- Check internet connection
- Ensure 2-Step Verification is enabled on Google Account
- Check if less secure app access is needed (older accounts)

### Face Detection Issues
- Ensure good lighting
- Position face clearly in front of camera
- Check if haarcascade file is in project directory
- System will work without face detection if needed (for testing)

## Database Schema

The system creates a SQLite database `school_gate.db` with the following structure:

```sql
CREATE TABLE gate_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    event TEXT NOT NULL,  -- 'entry' or 'exit'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Security Considerations

- **Never commit `config.py` with real credentials to version control**
- Add `config.py` to `.gitignore`
- Use App Passwords instead of regular passwords
- Restrict physical access to the monitoring computer
- Regularly backup the database file

## Future Enhancements

- Student name database instead of just IDs
- Photo capture on each scan
- Advanced reporting and analytics
- Mobile app for parents
- Multiple gate support
- Cloud database synchronization

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, check the console output for detailed error messages.
