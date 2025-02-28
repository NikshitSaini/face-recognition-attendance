# Face Recognition Attendance System

A web-based attendance system using face recognition technology.

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
