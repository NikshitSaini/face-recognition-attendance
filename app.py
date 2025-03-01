from flask import Flask, render_template, Response, request, redirect, url_for
import face
import cv2
import sys
import os
import time  # Add this import
import base64
import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)
video_stream = None
selected_class = None

def get_available_camera():
    """Try different camera indices to find an available one"""
    for index in range(10):  # Try indices 0 to 9
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            cap.release()
            return index
    return None

# Initialize face encodings
try:
    faces = face.encode_faces()
    encoded_faces = list(faces.values())
    faces_names = list(faces.keys())
except Exception as e:
    print(f"Error loading face encodings: {e}")
    sys.exit(1)

def gen_frames():
    global video_stream, selected_class  # Add selected_class
    
    # Find available camera
    camera_index = get_available_camera()
    if (camera_index is None):
        print("No cameras found!")
        return
        
    try:
        video_stream = face.VideoStream(stream=camera_index)
        video_stream.start()
        
        while True:
            frame = video_stream.read()
            if frame is None:
                print("No frame received")
                continue
                
            # Process frame for face recognition
            face_locations = face.fr.face_locations(frame)
            unknown_face_encodings = face.fr.face_encodings(frame, face_locations)
            
            face_names = []
            for face_encoding in unknown_face_encodings:
                matches = face.fr.compare_faces(encoded_faces, face_encoding)
                name = "Unknown"
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = faces_names[first_match_index]
                    # Pass selected_class to Attendance function
                    face.Attendance(name, selected_class)
                face_names.append(name)
            
            # Draw rectangle around faces
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, bottom + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   
    except Exception as e:
        print(f"Error in video stream: {e}")
        if video_stream:
            video_stream.stop()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_class', methods=['POST'])
def select_class():
    global selected_class, video_stream
    
    # Stop any existing video stream
    if video_stream:
        video_stream.stop()
        video_stream = None
    
    selected_class = request.form['class']
    if not selected_class:
        return redirect(url_for('index'))
    return redirect(url_for('mark_attendance'))

@app.route('/mark_attendance')
def mark_attendance():
    global selected_class
    if not selected_class:
        return redirect(url_for('index'))
    return render_template('mark_attendance.html', class_name=selected_class)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/done')
def done():
    global video_stream, selected_class
    if video_stream:
        video_stream.stop()
        video_stream = None
    
    # Send attendance email if class was selected
    if selected_class:
        try:
            # Setup email
            email_sender = config.email_sender
            password = config.password
            receiver_email = config.receiver_email
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_sender
            msg['To'] = receiver_email
            msg['Subject'] = f"Attendance Record for {selected_class}"
            
            # Add body
            body = f"Please find attached the attendance record for {selected_class}."
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach attendance file
            today = time.strftime('%d_%m_%Y')
            record_file = f"data/Records/Record_{selected_class}_{today}.csv"
            
            if os.path.exists(record_file):
                with open(record_file, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(record_file)}"')
                    msg.attach(part)
                
                # Send email
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(email_sender, password)
                text = msg.as_string()
                server.sendmail(email_sender, receiver_email, text)
                server.quit()
                print("Attendance email sent successfully!")
            
        except Exception as e:
            print(f"Error sending attendance email: {e}")
    
    selected_class = None
    return redirect(url_for('index'))

@app.route('/add_student')
def add_student():
    return render_template('add_student.html')

@app.route('/save_student', methods=['POST'])
def save_student():
    try:
        student_name = request.form['student_name']
        photo_data = request.form['photo']
        
        # Convert base64 to image
        image_data = base64.b64decode(photo_data.split(',')[1])
        
        # Create images directory if it doesn't exist
        image_dir = "data/Images"  # Relative path
        try:
            os.makedirs(image_dir, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory: {e}")
            return "Error creating directory", 500
        
        # Save the image
        image_path = os.path.join(image_dir, f"{student_name}.jpg")
        try:
            with open(image_path, 'wb') as f:
                f.write(image_data)
        except IOError as e:
            print(f"Error writing image file: {e}")
            return "Error writing image file", 500
            
        # Reload face encodings
        global faces, encoded_faces, faces_names
        faces = face.encode_faces()
        encoded_faces = list(faces.values())
        faces_names = list(faces.keys())
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error saving student: {e}")
        return "Error saving student", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
