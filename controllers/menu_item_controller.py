import os
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
)
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from db.database import get_db
from models.category import Category
from models.menu_item import MenuItem
from schemas.menu_schema import MenuCreate, MenuOut
from utils.file_upload import save_menu_image
from utils.redis import redis_client
from utils.dependencies import get_current_user
from utils.permissions import require_roles

CACHE_TTL = 5
MENU_NOT_FOUND_DETAIL = "Menu not found"

router = APIRouter(
    prefix="/menus",
    tags=["Menu"]
)
@router.get("/search")
def search_menu_items_by_name(
    keyword: str = Query(..., min_length=1),
    *,
    db: Annotated[Session, Depends(get_db)],
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
    *,
    db: Annotated[Session, Depends(get_db)],
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
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
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
    *,
    db: Annotated[Session, Depends(get_db)],
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

@router.get(
    "/{menu_id}",
    response_model=MenuOut,
    responses={404: {"description": MENU_NOT_FOUND_DETAIL}},
)
def get_menu_detail(
    menu_id: UUID,
    db: Annotated[Session, Depends(get_db)],
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
        raise HTTPException(status_code=404, detail=MENU_NOT_FOUND_DETAIL)

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
    restaurant_id: Annotated[UUID, Query(...)],
    name: Annotated[str, Form(...)],
    category_id: Annotated[UUID, Form(...)],
    price: Annotated[Decimal, Form(...)],
    image: Annotated[UploadFile, File(...)],
    description: Annotated[str | None, Form()] = None,
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
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
@router.delete(
    "/{menu_id}",
    status_code=204,
    responses={404: {"description": MENU_NOT_FOUND_DETAIL}},
)
def delete_menu(
    menu_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
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
        raise HTTPException(status_code=404, detail=MENU_NOT_FOUND_DETAIL)

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

@router.put(
    "/{menu_id}/image",
    response_model=MenuOut,
    responses={404: {"description": MENU_NOT_FOUND_DETAIL}},
)
def update_menu_image(
    menu_id: UUID,
    image: UploadFile = File(...),
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(get_current_user)],
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
        raise HTTPException(status_code=404, detail=MENU_NOT_FOUND_DETAIL)

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
