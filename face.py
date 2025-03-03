import face_recognition as fr
from threading import Thread
import numpy as np
import time
import os
import cv2
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import config
exclude_names = ['Unknown', 'HOD', 'Principal']

class VideoStream:
    def __init__(self, stream):
        self.video = cv2.VideoCapture(stream)
        
        # Try setting a lower resolution if camera supports it
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.video.set(cv2.CAP_PROP_FPS, 30)  # Lower FPS
        
        # Wait a bit for camera to initialize
        time.sleep(2)
        
        if not self.video.isOpened():
            raise RuntimeError(f"Failed to open camera at index {stream}")

        self.grabbed, self.frame = self.video.read()
        if not self.grabbed:
            raise RuntimeError("Failed to grab first frame")

        self.stopped = True
        self.thread = Thread(target=self.update)
        self.thread.daemon = True
    
    def start(self):
        self.stopped = False
        self.thread.start()

    def update(self):
        while True :
            if self.stopped is True :
                break
            self.grabbed , self.frame = self.video.read()

        self.video.release()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        # Add proper cleanup
        if hasattr(self, 'video') and self.video is not None:
            self.video.release()
        cv2.destroyAllWindows()  # Close any open windows

    def __del__(self):
        # Ensure cleanup when object is destroyed
        self.stop()

        
def encode_faces():
    encoded_data = {}
    image_path = "data/Images"  # Relative path
    
    for dirpath, dnames, fnames in os.walk(image_path):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png") or f.endswith(".jpeg"):
                face = fr.load_image_file(os.path.join(dirpath, f))
                encoding = fr.face_encodings(face)[0]
                encoded_data[f.split(".")[0]] = encoding
    return encoded_data

def Attendance(name, class_section):
    if not class_section:
        return
        
    today = time.strftime('%d_%m_%Y')
    record_dir = "data/Records"  # Relative path
    
    # Create class-specific filename
    record_file = os.path.join(record_dir, f'Record_{class_section}_{today}.csv')
    
    # Create directory if it doesn't exist
    os.makedirs(record_dir, exist_ok=True)
    
    # Create new file with headers if it doesn't exist
    if not os.path.exists(record_file):
        with open(record_file, 'w') as f:
            f.write(f"Attendance Record for {class_section} - {today}\n")
            f.write("Name,Time,Class\n")
    
    # Read existing entries
    names_today = set()
    try:
        with open(record_file, 'r') as f:
            next(f)  # Skip header row 1
            next(f)  # Skip header row 2
            for line in f:
                if line.strip():  # Skip empty lines
                    names_today.add(line.split(',')[0])
    except:
        pass  # File might be empty or not exist
    
    # Add new entry if not already present
    if name not in names_today and name not in exclude_names:
        with open(record_file, 'a') as f:
            current_time = time.strftime('%H:%M:%S')
            f.write(f"{name},{current_time},{class_section}\n")
        # Removed send_attendance_email call from here


def send_attendance_email(record_file,class_section):
    email_sender = config.email_sender
    password = config.password
    receiver_email = config.receiver_email  # Get receiver email from config
    if not password:
        print("Error: EMAIL_PASSWORD environment variable not set.")
        return
    subject=f"Attendance Record for {class_section}"
    
    # Construct the email
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['Subject'] = subject
    
    # Email body
    body = f"Please find attached the attendance record for {class_section}."
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach the CSV file
    try:
        with open(record_file, "rb") as attachment:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(record_file)}"')
            msg.attach(part)
    except FileNotFoundError:
        print(f"Error: Could not find attendance file: {record_file}")
        return
    except Exception as e:
        print(f"Error attaching file: {e}")
        return
    
    # Send the email
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(email_sender, password)
        text = msg.as_string()
        server.sendmail(email_sender, receiver_email, text)  # Send to receiver_email
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    has_gui = True
    try:
        cv2.namedWindow('frame')
    except:
        print("Warning: GUI not available. Running in headless mode.")
        has_gui = False

    faces = encode_faces()
    encoded_faces = list(faces.values())
    faces_name = list(faces.keys())
    video_frame = True

    
    video_stream = VideoStream(stream=0)
    video_stream.start()

    start_time = time.time()

    try:
        while True:
            if video_stream.stopped is True:
                break
            else :
                frame = video_stream.read()

                if video_frame:
                    face_locations = fr.face_locations(frame)
                    unknown_face_encodings = fr.face_encodings(frame, \
                    face_locations)

                    face_names = []
                    for face_encoding in unknown_face_encodings:
                        matches = fr.compare_faces(encoded_faces, \
                        face_encoding)
                        name = "Unknown"

                        face_distances = fr.face_distance(encoded_faces,\
                        face_encoding)
                        try:

                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = faces_name[best_match_index]

                            face_names.append(name)
                        except:
                            pass

                video_frame = not video_frame

                for (top, right, bottom, left), name in zip(face_locations,\
                face_names):
                    cv2.rectangle(frame, (left-20, top-20), (right+20, \
                    bottom+20), (0, 255, 0), 2)
                    
                    cv2.rectangle(frame, (left-20, bottom -15), \
                    (right+20, bottom+20), (0, 255, 0), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                
                    cv2.putText(frame, name, (left -20, bottom + 15), \
                    font, 0.85, (255, 255, 255), 2)
                    
                    
                    Attendance(name)

            
            delay = 0.04
            time.sleep(delay)

            if has_gui:
                try:
                    cv2.imshow('frame' , frame)
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        break
                except Exception as e:
                    print(f"Error displaying frame: {e}")
                    break
            else:
                if time.time() - start_time > 60:
                    break
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
    finally:
        if video_stream:
            video_stream.stop()
        cv2.destroyAllWindows()

    email_sender = config.email_sender
    password = config.password
    receiver_email = config.receiver_email # Get receiver email from config
    subject="Automate Attendence "
    today = time.strftime('%d_%m_%Y')
    record_file = f"data/Records/Record_{today}.csv"
    msg=MIMEMultipart()
    msg['From']=email_sender
    msg["To"]=receiver_email
    msg.attach(MIMEText("Attendance", "plain"))
    part=MIMEBase('application',"octect-stream")
    part.set_payload(open(record_file, "rb").read())
    encoders.encode_base64(part)
    part.add_header('content-Disposition', f'attachment ; filename="Record_{today}.csv"')
    msg.attach(part)
    text=msg.as_string()
    server=smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login(email_sender,password)
    server.sendmail(email_sender,receiver_email,text)
    server.quit()


