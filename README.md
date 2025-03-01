# Face Recognition Attendance System

A web-based attendance system using face recognition technology with automatic email notifications.

## Project Structure

```
├── app.py              # Flask application
├── face.py            # Face recognition logic
├── config.py          # Configuration (not in repo)
├── requirements.txt   # Python dependencies
├── templates/         # HTML templates
└── data/             # Data directories
    ├── Images/       # Student images
    └── Records/      # Attendance records
```

## Config File Data:

```python
import os
#Replace File data below
DEFAULT_EMAIL_SENDER = "SENDER_EMAIL_ADDRESS" #CHANGE ADDRESS
DEFAULT_PASSWORD = "aaaaaaaaaaaaaaaa"  # 16 characters Googlr App password without spaces
DEFAULT_RECEIVER = "RECEIVER_EMAIL_ADDRESS" #CHANGE ADDRESS

email_sender = DEFAULT_EMAIL_SENDER
password = DEFAULT_PASSWORD
receiver_email = DEFAULT_RECEIVER
if not all([email_sender, password, receiver_email]):
    raise ValueError("Missing email configuration!")
```

## Features
- Face detection and recognition
- Class-wise attendance tracking
- Separate attendance records for different sections (SE-A, SE-B, SE-C)
- Web interface for easy access
- Email notifications

## Setup
1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/face-recognition-attendance.git
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create required directories
```bash
mkdir -p "project pbl/Images"
mkdir -p "project pbl/Records"
```

4. Add face images to `project pbl/Images` directory
- Name format: `PersonName.jpg`
- Just use in-build image saving feature after running program

5. Run the application
```bash
python app.py
```

6. Access the web interface at `http://127.0.0.1:5000`

## Usage
1. Select class section (SE-A, SE-B, or SE-C)
2. Click "Mark Attendance"
3. Allow camera access
4. System will automatically recognize faces and mark attendance
5. Click "Done" when finished