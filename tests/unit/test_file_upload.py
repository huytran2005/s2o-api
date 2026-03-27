from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

import utils.file_upload as file_upload


def test_save_restaurant_image_stores_file(monkeypatch, tmp_path):
    monkeypatch.setattr(file_upload, "RESTAURANT_DIR", tmp_path / "restaurants")
    file_upload.RESTAURANT_DIR.mkdir(parents=True, exist_ok=True)

    upload = UploadFile(filename="preview.png", file=BytesIO(b"image-bytes"))

    saved_path = file_upload.save_restaurant_image(upload)

    assert saved_path.startswith("/media/restaurants/")
    saved_name = Path(saved_path).name
    assert (file_upload.RESTAURANT_DIR / saved_name).read_bytes() == b"image-bytes"


def test_save_menu_image_stores_file(monkeypatch, tmp_path):
    monkeypatch.setattr(file_upload, "MENU_DIR", tmp_path / "menus")
    file_upload.MENU_DIR.mkdir(parents=True, exist_ok=True)

    upload = UploadFile(filename="menu.jpg", file=BytesIO(b"menu-bytes"))

    saved_path = file_upload.save_menu_image(upload)

    assert saved_path.startswith("/media/menus/")
    saved_name = Path(saved_path).name
    assert (file_upload.MENU_DIR / saved_name).read_bytes() == b"menu-bytes"
