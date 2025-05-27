# app/camera/stream.py
import cv2
from io import BytesIO

def generate_video_stream():
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend

    
    if not cap.isOpened():
        raise RuntimeError("Could not start camera.")
    
    # Set desired resolution if needed (e.g., 640x480)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture image.")
            break
        
        # Convert frame to JPEG format
        _, encoded_frame = cv2.imencode('.jpg', frame)
        
        # If frame encoding fails, skip this frame
        if not _:
            continue
        
        # Convert encoded frame to byte stream
        byte_io = BytesIO(encoded_frame.tobytes())
        
        # Yield the image as multipart/x-mixed-replace
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_io.read() + b'\r\n')

    cap.release()
