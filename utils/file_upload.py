import os
import uuid
from fastapi import UploadFile

BASE_DIR = "media/restaurants"
os.makedirs(BASE_DIR, exist_ok=True)


def save_restaurant_image(file: UploadFile) -> str:
    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(BASE_DIR, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path
