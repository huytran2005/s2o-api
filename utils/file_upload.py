import os
import uuid
from fastapi import UploadFile
from pathlib import Path

RESTAURANT_DIR = Path("media/restaurants")
MENU_DIR = Path("media/menus")

RESTAURANT_DIR.mkdir(parents=True, exist_ok=True)
MENU_DIR.mkdir(parents=True, exist_ok=True)


def save_restaurant_image(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    file_path = RESTAURANT_DIR / filename

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # 🔥 TRẢ VỀ URL PATH
    return f"/media/restaurants/{filename}"


def save_menu_image(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    file_path = MENU_DIR / filename

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # 🔥 TRẢ VỀ URL PATH (QUAN TRỌNG)
    return f"/media/menus/{filename}"
