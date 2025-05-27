from fastapi import APIRouter, UploadFile, File, Form
from typing import List
import shutil
import os
try:
    from register_face import register_from_folder
except:
    from app.register_face import register_from_folder

try:
    from Face_db import Database
except:
    from app.Face_db import Database

router = APIRouter()

UPLOAD_DIR = "app/faces"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-images/")
async def upload_images(
    username: str = Form(...),
    images: List[UploadFile] = File(...)
):
    print(f"Received images for user: {username}")
    if len(images) < 10:
        print("Error: Exactly 10 images are required.")
        return {"error": "Exactly 10 images are required."}

    user_dir = os.path.join(UPLOAD_DIR)
    os.makedirs(user_dir, exist_ok=True)
    print(f"Directory created")

    saved_files = []
    for idx, image in enumerate(images):
        file_path = os.path.join(user_dir, f"{idx+1}_{image.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        saved_files.append(file_path)
    
    print(f"Saved images")

    register_from_folder(username)
    return {"message": "Images uploaded successfully.", "files": saved_files}

@router.get("/get_all_users/")
async def get_all_users():
    db = Database()
    faces = db.list_users()
    return [
            {
                "index": i,
                "user_name": face.username
                
            }
            for i, face in enumerate(faces)
        ]


