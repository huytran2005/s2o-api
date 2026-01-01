from uuid import UUID
import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session

from db.database import get_db
from models.menu_item import MenuItem
from schemas.menu_schema import MenuCreate, MenuOut
from utils.dependencies import get_current_user
from utils.permissions import require_roles
from utils.file_upload import save_menu_image

router = APIRouter(
    prefix="/menus",
    tags=["Menu"]
)

# ======================
# CREATE MENU
# ======================
@router.post("/", response_model=MenuOut)
def create_menu(
    restaurant_id: UUID,
    data: MenuCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    menu = MenuItem(
        restaurant_id=restaurant_id,
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        price=data.price,
        image_url=data.image_url,
        meta=data.meta
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


# ======================
# LIST MENU
# ======================
@router.get("/", response_model=list[MenuOut])
def list_menus(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    return (
        db.query(MenuItem)
        .filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True
        )
        .all()
    )


# ======================
# UPLOAD MENU IMAGE
# ======================
@router.put("/{menu_id}/image")
def upload_menu_image(
    menu_id: UUID,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    old_image = menu.image_url

    new_image = save_menu_image(image)
    menu.image_url = new_image
    db.commit()

    if old_image and os.path.exists(old_image):
        try:
            os.remove(old_image)
        except Exception:
            pass

    return {
        "image_url": new_image
    }
