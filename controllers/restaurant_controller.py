import os
import json
import asyncio

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
from models.user import User
from schemas.restaurant_schema import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantResponse,
)
from utils.dependencies import get_current_user
from utils.permissions import require_roles
from utils.file_upload import save_restaurant_image
from utils.redis import redis_client

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurant"]
)

CACHE_TTL = 60


# ======================
# LIST RESTAURANTS
# ======================
@router.get("/", response_model=list[RestaurantResponse])
async def list_restaurants(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "admin"])

    restaurants = db.query(Restaurant).filter(
        Restaurant.owner_id == current_user.id
    ).all()

    result = []

    for r in restaurants:
        staff = db.query(User).filter(
            User.restaurant_id == r.id
        ).all()

        result.append({
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "image_preview": r.image_preview,
            "staff_members": [
                {
                    "id": s.id,
                    "email": s.email,
                    "display_name": s.display_name,
                    "phone": s.phone,
                    "role": s.role,
                }
                for s in staff
            ]
        })

    return result


            "staff_members": []
        }
        for r in restaurants
    ]
# ======================
# CREATE RESTAURANT
# ======================
@router.post("/", response_model=RestaurantResponse, status_code=201)
async def create_restaurant(
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

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "description": restaurant.description,
        "image_preview": restaurant.image_preview,
        "staff_members": []  # ✅ fix schema
        "staff_members": []
    }


# ======================
# GET RESTAURANT DETAIL
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
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            response.headers["X-Cache"] = "HIT"
            return json.loads(cached)
    except Exception:
        pass

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    staff = db.query(User).filter(
        User.restaurant_id == restaurant_id
    ).all()

    result = {
        "id": restaurant.id,
        "name": restaurant.name,
        "description": restaurant.description,
        "image_preview": restaurant.image_preview,
        "staff_members": [
            {
                "id": s.id,
                "email": s.email,
                "display_name": s.display_name,
                "phone": s.phone,
                "role": s.role,
            }
            for s in staff
        ]
    }

    # SAVE CACHE
    await redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(result, default=str)
    )
    try:
        await redis_client.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(result, default=str)
        )
    except Exception:
        pass

    response.headers["X-Cache"] = "MISS"
    return result


# ======================
# UPDATE RESTAURANT
# ======================
@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
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
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)

    db.commit()
    db.refresh(restaurant)

    await redis_client.delete(f"restaurant:{restaurant_id}")
    try:
        await redis_client.delete(f"restaurant:{restaurant_id}")
    except Exception:
        pass

    staff = db.query(User).filter(
        User.restaurant_id == restaurant_id
    ).all()

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "description": restaurant.description,
        "image_preview": restaurant.image_preview,
        "staff_members": [
            {
                "id": s.id,
                "email": s.email,
                "display_name": s.display_name,
                "phone": s.phone,
                "role": s.role,
            }
            for s in staff
        ]
    }


# ======================
# UPDATE PREVIEW IMAGE
# ======================
@router.put("/{restaurant_id}/preview-image")
async def update_preview_image(
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
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # VALIDATE FORMAT
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image format")

    # VALIDATE SIZE
    contents = await image.read()
    size = len(contents)

    if size < 100 * 1024 or size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Invalid image size")

    image.file.seek(0)

    old_image = restaurant.image_preview
    new_image = save_restaurant_image(image)

    restaurant.image_preview = new_image
    db.commit()

    if old_image and os.path.exists(old_image):
        try:
            os.remove(old_image)
        except Exception:
            pass

    await redis_client.delete(f"restaurant:{restaurant_id}")
    try:
        await redis_client.delete(f"restaurant:{restaurant_id}")
    except Exception:
        pass

    return {"image_preview": new_image}


# ======================
# DELETE RESTAURANT
# ======================
@router.delete("/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["admin"])

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if restaurant.image_preview and os.path.exists(restaurant.image_preview):
        try:
            os.remove(restaurant.image_preview)
        except Exception:
            pass

    db.delete(restaurant)
    db.commit()

    await redis_client.delete(f"restaurant:{restaurant_id}")
    try:
        await redis_client.delete(f"restaurant:{restaurant_id}")
    except Exception:
        pass

    return {"message": "Restaurant deleted"}