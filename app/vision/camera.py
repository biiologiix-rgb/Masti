import re
import base64
import pickle
from pathlib import Path
from io import BytesIO

import cv2
import numpy as np
from PIL import Image
import face_recognition


def capture_and_store_face(image_data: str, username: str, roll: int, upload_dir: str) -> str:
    """
    Saves the base64 image to <upload_dir>/<safe_filename>.jpg
    Returns the absolute path string (e.g., 'faces/Name_1.jpg').
    """
    if not image_data or not image_data.startswith("data:image"):
        raise ValueError("Invalid or empty base64 image received.")

    try:
        image_data_clean = re.sub(r'^data:image/.+;base64,', '', image_data)
        img_bytes = base64.b64decode(image_data_clean)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise ValueError(f"Image could not be decoded: {e}")

    safe_name = re.sub(r'[^A-Za-z0-9_-]+', '_', username.strip())
    filename = f"{safe_name}_{roll}.jpg"

    faces_folder = Path(upload_dir)
    faces_folder.mkdir(parents=True, exist_ok=True)
    file_path = faces_folder / filename

    cv2.imwrite(str(file_path), img_cv)
    return str(file_path)  # absolute path used by get_face_encodings


def get_face_encodings(image_path: Path):
    """
    Returns a list of face encodings from the given image.
    Can be multiple if multiple faces/angles are detected.
    """
    image = face_recognition.load_image_file(str(image_path))
    image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)

    encodings = face_recognition.face_encodings(image)
    if encodings:
        return encodings  # list of 128-d vectors
    return []
