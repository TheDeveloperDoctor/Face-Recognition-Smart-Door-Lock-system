from mtcnn.mtcnn import MTCNN
import cv2

detector = MTCNN()

def detect_face(image):
    result = detector.detect_faces(image)
    if result:
        x, y, w, h = result[0]['box']
        x, y = max(0, x), max(0, y)
        face = image[y:y + h, x:x + w]
        return cv2.resize(face, (112, 112))
    return None
