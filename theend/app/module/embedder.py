import numpy as np
import cv2

try:
    import tensorflow.lite as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    try:
        import tensorflow as tf
        tflite = tf.lite
        TFLITE_AVAILABLE = True
    except ImportError:
        TFLITE_AVAILABLE = False


class MobileFaceNetEmbedder:
    def __init__(self, model_path='mobilefacenet.tflite'):
        if not TFLITE_AVAILABLE:
            raise ImportError("Neither tflite nor tensorflow.lite is available.")

        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def preprocess(self, face):
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = cv2.resize(face, (112, 112))  # Assuming 112x112 model input
        face = face.astype(np.float32) / 127.5 - 1.0
        return np.expand_dims(face, axis=0)

    def get_embedding(self, face):
        input_data = self.preprocess(face)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        embedding = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        return embedding / np.linalg.norm(embedding)
