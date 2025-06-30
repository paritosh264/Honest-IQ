from flask import Flask, render_template, request, jsonify
import threading
import cv2
import numpy as np
import base64
import time
import mediapipe as mp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

app = Flask(__name__)
regno = ''
name = ''
latest_frame = None
latest_alerts = []
last_email_time = None
last_face_email=None

@app.route('/')
def intro():
    return render_template('index.html')

@app.route('/start', methods=["POST"])
def log():
    global regno, name
    regno = request.form.get('regno')
    name = request.form.get("name")
    print(f"[INFO] Test started for {name} ({regno})")
    return render_template("introduction.html")

@app.route('/send_frame', methods=["POST"])
def receive_frame():
    global latest_frame
    data = request.get_json()
    data_url = data.get('frame')
    if ',' in data_url:
        data = base64.b64decode(data_url.split(',')[1])
        np_arr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        latest_frame = frame
    return '', 204

@app.route('/get_alerts')
def get_alerts():
    return jsonify({"alerts": latest_alerts})

def send_email(subject, body, to_email, attachment_path=None):
    from_email = "tripathiparitoshmotto@gmail.com"
    from_password = "uevm eowa zmet rtoh"  
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach file if exists
    if attachment_path and os.path.exists(attachment_path):
        part = MIMEBase('application', 'octet-stream')
        with open(attachment_path, 'rb') as attachment:
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(part)
    else:
        print(f"Attachment not found: {attachment_path}")

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {str(e)}")
        print("Check SMTP settings and credentials.")



def multi_face_screenshot(frame):
    global last_face_email
    try:
        pth = r"C:\\Users\\parit\\the_genius_coder\\my_webd_researches\\multi_face.png"
        subject = "Multiple Faces Detected!"
        body = f"More than one faces were detected in the frame.for user) {name} id {regno})"
        to_email = "tutkarsh190@gmail.com"
        print("Multiple faces detected, sending screenshot email.")

        now = datetime.now()
        global last_email_time
        if last_face_email is None or (now - last_face_email).seconds >= 10:
            cv2.imwrite(pth, frame)
            threading.Thread(target=send_email, args=(subject, body, to_email, pth), daemon=True).start()
            last_face_email = now
    except Exception as e:
        print(f"Error in multi_face_screenshot function: {str(e)}")


def hand_screenshot(frame):
    try:
        pth = "C:\\Users\\parit\\the_genius_coder\\my_webd_researches\\temp.png"
        subject = "Hand Detected!"
        body = f"A hand was detected in the frame. for user) {name} id {regno})"
        to_email = "tutkarsh190@gmail.com"
        print("Hand detected, sending screenshot email.")
        
        now = datetime.now()
        global last_email_time
        if last_email_time is None or (now - last_email_time).seconds >= 10:
            cv2.imwrite(pth, frame)  
            threading.Thread(target=send_email, args=(subject, body, to_email, pth), daemon=True).start()
            last_email_time = now
    except Exception as e:
        print(f"Error in screenshot function: {str(e)}")

def detect():
    global latest_frame, latest_alerts

    mp_face = mp.solutions.face_mesh
    mp_hands = mp.solutions.hands
    face = mp_face.FaceMesh(static_image_mode=False, max_num_faces=2)
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

    while True:
        if latest_frame is not None:
            frame = latest_frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = face.process(rgb)
            hand_results = hands.process(rgb)

            alerts = []

        
            if face_results.multi_face_landmarks:
                if len(face_results.multi_face_landmarks) > 1:
                    alerts.append("More than 1 face detected")
                    multi_face_screenshot(frame)
                for f in face_results.multi_face_landmarks:
                    h, w, _ = frame.shape
                    upper_lip = f.landmark[13]
                    lower_lip = f.landmark[14]
                    y_diff = abs(upper_lip.y - lower_lip.y) * h
                    if y_diff >= 4:
                        alerts.append("Lip movement detected")
            else:
                alerts.append("Face not visible")

            # Hand detection
            if hand_results.multi_hand_landmarks:
                alerts.append("Hand detected")
                hand_screenshot(frame) 

            latest_alerts = alerts

        time.sleep(0.5)

if __name__ == "__main__":
    
    threading.Thread(target=detect, daemon=True).start()
    app.run(port=8000, debug=True)
