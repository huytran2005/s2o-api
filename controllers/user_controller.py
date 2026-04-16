from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from db.session import get_db
from models.user import User
from models.restaurant import Restaurant
from schemas.user_schema import CreateStaffRequest, CreateStaffResponse
from utils.security import hash_password
from utils.dependencies import get_current_user

# 🔥 PHẢI CÓ DÒNG NÀY
router = APIRouter(prefix="", tags=["User"])


# =========================
# CREATE STAFF (MULTI RESTAURANT)
# =========================
@router.post("/restaurants/{restaurant_id}/staff", response_model=CreateStaffResponse)
def create_staff(
    restaurant_id: UUID,
    data: CreateStaffRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # check role
    if current_user.role != "owner":
        raise HTTPException(403, "Only owner can create staff")

    # check restaurant thuộc owner
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id,
        Restaurant.owner_id == current_user.id
    ).first()

    if not restaurant:
        raise HTTPException(403, "Not your restaurant")

    # check email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already exists")

    staff = User(
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        phone=data.phone,
        role="staff",
        restaurant_id=restaurant_id
    )

    db.add(staff)
    db.commit()

    return {
        "message": "Staff created successfully",
        "staff_id": str(staff.id),
        "restaurant_id": str(restaurant_id),
    }