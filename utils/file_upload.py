import os
import uuid
from fastapi import UploadFile

BASE_DIR_Res = "media/restaurants"
os.makedirs(BASE_DIR_Res, exist_ok=True)


def save_restaurant_image(file: UploadFile) -> str:
    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(BASE_DIR_Res, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path



MENU_DIR_Menu = "media/menus"

def save_menu_image(file: UploadFile) -> str:
    os.makedirs(MENU_DIR_Menu, exist_ok=True)

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(MENU_DIR_Menu, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path