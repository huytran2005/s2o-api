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
    Query
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
CACHE_TTL = 60

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
