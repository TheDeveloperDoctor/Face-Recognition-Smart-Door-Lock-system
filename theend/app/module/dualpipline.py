import cv2
import pickle
import time
import os
from datetime import datetime, timedelta
from pyzbar.pyzbar import decode

# App modules
from app.qrcode_db import SessionLocal, get_qr_code
from app.access_logs import add_log
from app.module.embedder import MobileFaceNetEmbedder
from app.module.detector import detect_face

# Initialize components
embedder = MobileFaceNetEmbedder()

# Global variable for KNN model
knn = None
last_model_load_time = 0
model_file_path = "knn_model.pkl"

def load_knn_model():
    global knn, last_model_load_time
    try:
        with open(model_file_path, "rb") as f:
            knn = pickle.load(f)
        last_model_load_time = os.path.getmtime(model_file_path)
        print("KNN model loaded successfully")
    except Exception as e:
        print(f"Error loading KNN model: {e}")

# Initial model load
load_knn_model()

# Configurations
face_cooldown = {}
qr_cooldown = {}
COOLDOWN_FACE = 15  # seconds
COOLDOWN_QR = timedelta(minutes=1)
MODEL_CHECK_INTERVAL = 5  # seconds - how often to check for model updates
last_model_check_time = time.time()

# Start session
session = SessionLocal()
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = datetime.now()
        timestamp = time.time()

        # Periodically check for model updates
        if timestamp - last_model_check_time > MODEL_CHECK_INTERVAL:
            try:
                current_mod_time = os.path.getmtime(model_file_path)
                if current_mod_time > last_model_load_time:
                    print("Detected model file change, reloading...")
                    load_knn_model()
            except Exception as e:
                print(f"Error checking model file: {e}")
            last_model_check_time = timestamp

        # === QR Code Processing ===
        detected_qrcodes = decode(frame)
        for qr in detected_qrcodes:
            qr_data = qr.data.decode('utf-8')

            if qr_data in qr_cooldown and (current_time - qr_cooldown[qr_data]) < COOLDOWN_QR:
                continue

            qr_cooldown[qr_data] = current_time
            print(f"Scanned QR Code: {qr_data}")

            qr_entry = get_qr_code(session, qr_data)
            if qr_entry:
                add_log(qr_entry.user_name, "qr_code", "successful")
                print(f"Authorized QR: {qr_entry.user_name} and {qr_entry}")
            else:
                add_log("Unknown", "qr_code", "not_successful")
                print(f"Unknown QR code {qr_entry}")


        # === Face Recognition Processing ===
        if knn is not None:  # Only proceed if model is loaded
            face = detect_face(frame)
            if face is not None:
                embedding = embedder.get_embedding(face)
                name = knn.predict([embedding])[0]
                distance = knn.kneighbors([embedding], return_distance=True)[0][0][0]

                if name not in face_cooldown or timestamp - face_cooldown[name] > COOLDOWN_FACE:
                    if distance < 0.75:
                        add_log(name, "face_recognition", "successful")
                        print(f"Authorized Face: {name}")
                    else:
                        add_log("Unknown", "face_recognition", "not_successful")
                        print("Unauthorized face")
                    face_cooldown[name] = timestamp

        # Display the frame
        # cv2.imshow("QR & Face Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()