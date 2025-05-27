import cv2
import numpy as np
from pyzbar.pyzbar import decode
from datetime import datetime, timedelta
from app.qrcode_db import SessionLocal, get_qr_code
from app.access_logs import add_log






# Function to handle unknown QR codes
def unknown_qrcode():
    add_log("Unknown", "qr_code", "not_successful")
    # print("Unknown QR code. Not authorized!")

# Function to scan a QR code and check in the database
def scan_qr_code(session):
    # Initialize the camera
    cap = cv2.VideoCapture(0)
    
    # Track last scanned QR codes and their timestamps
    last_scanned = {}
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Decode the QR codes in the frame
        detected_qrcodes = decode(frame)
        
        for qr in detected_qrcodes:
            qr_data = qr.data.decode('utf-8')
            current_time = datetime.now()
            
            # Check if QR code was recently scanned
            if qr_data in last_scanned:
                time_since_last_scan = current_time - last_scanned[qr_data]
                if time_since_last_scan < timedelta(minutes=1):
                    # print(f"QR code {qr_data} already scanned recently. Ignoring...")
                    continue
            
            # Update last scanned time
            last_scanned[qr_data] = current_time
            
            print(f"Scanned QR Code: {qr_data}")
            
            # Check if the QR code exists in the database
            qr_entry = get_qr_code(session, qr_data)
            if qr_entry:
                add_log(qr_entry.user_name, "qr_code", "successful")
                # print(f"Authorized: {qr_entry.user_name} - {qr_entry.type.value}")
            else:
                unknown_qrcode()
        
        # Display the frame with detected QR codes
        for qr in detected_qrcodes:
            pts = qr.polygon
            if len(pts) == 4:
                pts = [tuple(pt) for pt in pts]
                cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (0, 0, 255), 2)
            else:
                center = qr.rect[:2]
                cv2.circle(frame, center, 5, (0, 0, 255), 2)
        
        # Show the video feed
        cv2.imshow("QR Code Scanner", frame)
        
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    session = SessionLocal()

    print("\nStarting QR Code Scanner:")
    scan_qr_code(session)