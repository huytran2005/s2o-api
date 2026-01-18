import os
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Response
)
from sqlalchemy.orm import Session

from db.database import get_db
from models.restaurant import Restaurant
from schemas.restaurant_schema import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantResponse,
)
from utils.dependencies import get_current_user
from utils.permissions import require_roles
from utils.file_upload import save_restaurant_image
from utils.redis import redis_client
import json

CACHE_TTL = 30

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurant"]
)

@router.get("/", response_model=list[RestaurantResponse])
def list_restaurants(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "admin"])

    return (
        db.query(Restaurant)
        .filter(Restaurant.owner_id == current_user.id)
        .all()
    )

# ======================
# CREATE RESTAURANT
# ======================
@router.post("/", response_model=RestaurantResponse, status_code=201)
def create_restaurant(
    data: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "admin"])

    restaurant = Restaurant(
        **data.model_dump(),
        owner_id=current_user.id
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


# ======================
# LIST RESTAURANTS
# ======================
@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: UUID,
    response: Response,
    db: Session = Depends(get_db),
):
    cache_key = f"restaurant:{restaurant_id}"

    cached = await redis_client.get(cache_key)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return json.loads(cached)

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    data = RestaurantResponse.model_validate(restaurant).model_dump()

    await redis_client.setex(
        cache_key,
        60,
        json.dumps(data, default=str)
    )

    response.headers["X-Cache"] = "MISS"
    return data

# ======================
# UPDATE RESTAURANT INFO
# ======================
@router.put("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: UUID,
    data: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "admin"])

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()

    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


# ======================
# UPDATE PREVIEW IMAGE (REPLACE)
# ======================
@router.put("/{restaurant_id}/preview-image")
def update_preview_image(
    restaurant_id: UUID,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "admin"])

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()

    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    # 1️⃣ lưu đường dẫn ảnh cũ
    old_image = restaurant.image_preview

    # 2️⃣ lưu ảnh mới
    new_image = save_restaurant_image(image)

    # 3️⃣ update DB
    restaurant.image_preview = new_image
    db.commit()

    # 4️⃣ xoá file cũ (sau commit)
    if old_image and os.path.exists(old_image):
        try:
            os.remove(old_image)
        except Exception:
            pass

    return {
        "image_preview": new_image
    }


# ======================
# DELETE RESTAURANT
# ======================
@router.delete("/{restaurant_id}")
def delete_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    # xoá ảnh preview nếu có
    if restaurant.image_preview and os.path.exists(restaurant.image_preview):
        try:
            os.remove(restaurant.image_preview)
        except Exception:
            pass

    db.delete(restaurant)
    db.commit()

    return {"message": "Restaurant deleted"}
