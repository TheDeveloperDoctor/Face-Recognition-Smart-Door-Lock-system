import cv2
import os
try:
    from module.embedder import MobileFaceNetEmbedder
    from module.detector import detect_face
    from Face_db import Database
    from module.trainer import train_knn
except:
    from app.module.embedder import MobileFaceNetEmbedder
    from app.module.detector import detect_face
    from app.Face_db import Database
    from app.module.trainer import train_knn

db = Database()
embedder = MobileFaceNetEmbedder()

def register_from_folder(username, folder_path="faces"):
    folder_path="app/faces"
    db = Database()
    embedder = MobileFaceNetEmbedder()
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
    if not image_files:
        print(f"No images found in folder '{folder_path}'.")
        return

    print(f"Registering face for: {username}")
    for idx, image_file in enumerate(image_files):
        image_path = os.path.join(folder_path, image_file)
        frame = cv2.imread(image_path)
        
        if frame is None:
            print(f"Error reading image {image_file}")
            continue
        
        face = detect_face(frame)
        if face is not None:
            # Get the embedding for the detected face
            embedding = embedder.get_embedding(face)
            # Insert embedding directly into the database
            db.insert_embedding(username, embedding)
            print(f"Processed {idx + 1}/{len(image_files)}: {image_file}")
    
    print("Registration complete.")
    train_knn()
    
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        os.remove(image_path)
        print(f"Removed {image_file} from '{folder_path}'")


# if __name__ == '__main__':
#     # Dynamic input for username and folder path
#     username = input("Enter username: ")
#     # You can change the folder path as needed
#     folder_path = "faces"
#     register_from_folder(username, folder_path)
