from uuid import UUID
import os
from typing import Optional
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Response,
    Query, Form
)
from sqlalchemy.orm import Session
from models.category import Category
from db.database import get_db
from models.menu_item import MenuItem
from schemas.menu_schema import MenuCreate, MenuOut
from utils.dependencies import get_current_user
from utils.permissions import require_roles
from utils.file_upload import save_menu_image
from sqlalchemy  import or_,func
from utils.redis import redis_client
import json
CACHE_TTL = 5

router = APIRouter(
    prefix="/menus",
    tags=["Menu"]
)
@router.get("/search")
def search_menu_items_by_name(
    keyword: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    """
    Search menu items by name or description
    """
    return (
        db.query(MenuItem)
        .filter(
            or_(
                MenuItem.name.ilike(f"%{keyword}%"),
                MenuItem.description.ilike(f"%{keyword}%"),
            )
        )
        .all()
    )
@router.get("/by-price")
def filter_menu_items_by_price(
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    """
    Filter menu items by price range
    """
    query = db.query(MenuItem)

    if min_price is not None:
        query = query.filter(MenuItem.price >= min_price)

    if max_price is not None:
        query = query.filter(MenuItem.price <= max_price)

    return query.order_by(MenuItem.price.asc()).all()

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
async def list_menus_guest(
    restaurant_id: UUID,
    response: Response,
    category_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    cache_key = f"menu:guest:{restaurant_id}:{category_id or 'all'}"

    try:
        cached = await redis_client.get(cache_key)
        if cached:
            response.headers["X-Cache"] = "HIT"
            return json.loads(cached)
    except Exception as e:
        print("⚠️ Redis unavailable:", e)

    query = (
        db.query(MenuItem)
        .outerjoin(Category)
        .filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True
        )
    )

    if category_id:
        query = query.filter(MenuItem.category_id == category_id)

    menus = query.all()

    data = [
        MenuOut(
            id=m.id,
            name=m.name,
            description=m.description,
            price=m.price,
            image_url=m.image_url,
            is_available=m.is_available,
            category_id=m.category.id if m.category else None,
            category_name=m.category.name if m.category else None,
        ).model_dump()
        for m in menus
    ]

    try:
        await redis_client.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(data, default=str)
        )
        response.headers["X-Cache"] = "MISS"
    except Exception as e:
        print("⚠️ Redis set failed:", e)

    return data

@router.get("/{menu_id}", response_model=MenuOut)
def get_menu_detail(
    menu_id: UUID,
    db: Session = Depends(get_db),
):
    menu = (
        db.query(MenuItem)
        .outerjoin(Category)
        .filter(
            MenuItem.id == menu_id,
            MenuItem.is_available == True
        )
        .first()
    )

    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    return MenuOut(
        id=menu.id,
        name=menu.name,
        description=menu.description,
        price=menu.price,
        image_url=menu.image_url,
        is_available=menu.is_available,
        category_id=menu.category.id if menu.category else None,
        category_name=menu.category.name if menu.category else None,
    )
@router.post("/with-image", response_model=MenuOut)
def create_menu_with_image(
    restaurant_id: UUID = Query(...),

    name: str = Form(...),
    category_id: UUID = Form(...),
    price: Decimal = Form(...),
    description: str | None = Form(None),

    image: UploadFile = File(...),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    # 1️⃣ save image
    image_url = save_menu_image(image)

    # 2️⃣ create menu
    menu = MenuItem(
        restaurant_id=restaurant_id,
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        is_available=True
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)

    return MenuOut(
        id=menu.id,
        name=menu.name,
        description=menu.description,
        price=menu.price,
        image_url=menu.image_url,
        is_available=menu.is_available,
        category_id=menu.category_id,
        category_name=menu.category.name if menu.category else None,
    )
@router.delete("/{menu_id}", status_code=204)
def delete_menu(
    menu_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # ===== CHECK PERMISSION =====
    require_roles(current_user, ["staff", "owner"])

    # ===== FIND MENU =====
    menu = (
        db.query(MenuItem)
        .filter(MenuItem.id == menu_id)
        .first()
    )

    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    restaurant_id = menu.restaurant_id
    category_id = menu.category_id

    # ======================
    # DELETE IMAGE FILE
    # ======================
    if menu.image_url:
        try:
            image_path = menu.image_url.lstrip("/")  # media/menus/xxx.png
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"🗑 Deleted image: {image_path}")
        except Exception as e:
            print("⚠️ Failed to delete image:", e)

    # ======================
    # HARD DELETE MENU
    # ======================
    db.delete(menu)
    db.commit()

    # ======================
    # 🔥 CLEAR ALL RELATED CACHE
    # ======================
    try:
        # all menus
        redis_client.delete(f"menu:guest:{restaurant_id}:all")

        # menu theo category
        if category_id:
            redis_client.delete(f"menu:guest:{restaurant_id}:{category_id}")

    except Exception as e:
        print("⚠️ Redis clear failed:", e)

    return Response(status_code=204)

@router.put("/{menu_id}/image", response_model=MenuOut)
def update_menu_image(
    menu_id: UUID,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    menu = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == menu_id,
            MenuItem.is_available == True
        )
        .first()
    )

    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    # (optional) xóa ảnh cũ nếu cần
    if menu.image_url:
        try:
            old_path = menu.image_url.replace("/media/", "")
            if os.path.exists(old_path):
                os.remove(old_path)
        except Exception:
            pass

    # save ảnh mới
    image_url = save_menu_image(image)
    menu.image_url = image_url

    db.commit()
    db.refresh(menu)

    # clear cache
    try:
        redis_client.delete(f"menu:guest:{menu.restaurant_id}:all")
    except Exception:
        pass

    return MenuOut(
        id=menu.id,
        name=menu.name,
        description=menu.description,
        price=menu.price,
        image_url=menu.image_url,
        is_available=menu.is_available,
        category_id=menu.category_id,
        category_name=menu.category.name if menu.category else None,
    )
