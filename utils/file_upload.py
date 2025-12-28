import os
import uuid
from fastapi import UploadFile

RESTAURANT_DIR = "media/restaurants"
MENU_DIR = "media/menus"

os.makedirs(RESTAURANT_DIR, exist_ok=True)
os.makedirs(MENU_DIR, exist_ok=True)


def save_restaurant_image(file: UploadFile) -> str:
    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(RESTAURANT_DIR, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path


def save_menu_image(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(MENU_DIR, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path
