print("Script started...")  # Debugging line

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

print("All libraries imported successfully!")
