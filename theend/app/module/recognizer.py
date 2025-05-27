import cv2
import pickle
import time
from app.module.embedder import MobileFaceNetEmbedder
from app.module.detector import detect_face
from app.access_logs import add_log
embedder = MobileFaceNetEmbedder()

with open("knn_model.pkl", "rb") as f:
    knn = pickle.load(f)

cooldown = {}
COOLDOWN_TIME = 15  # seconds

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    face = detect_face(frame)
    if face is not None:
        embedding = embedder.get_embedding(face)
        name = knn.predict([embedding])[0]
        distance = knn.kneighbors([embedding], return_distance=True)[0][0][0]

        current_time = time.time()
        if name not in cooldown or current_time - cooldown[name] > COOLDOWN_TIME:
            if distance < 0.75:
                # Assuming the name is the username
                # Add a log entry for the recognized face
                add_log(name, "face_recognition", "successful")
                print(f"authorized face: {name}")
            else:
                # Log the unauthorized access attempt
                add_log("Unkown", "face_recognition", "not_successful")
                print("unauthorized face")
            cooldown[name] = current_time

    # cv2.imshow("Live Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
