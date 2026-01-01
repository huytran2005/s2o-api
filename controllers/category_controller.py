from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.category import Category
from schemas.category_schema import CategoryCreate, CategoryOut
from utils.dependencies import get_current_user
from utils.permissions import require_roles

router = APIRouter(
    prefix="/categories",
    tags=["Category"]
)

@router.post("/", response_model=CategoryOut)
def create_category(
    restaurant_id: UUID,
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    name = data.name.strip()

    existing = (
        db.query(Category)
        .filter(
            Category.restaurant_id == restaurant_id,
            Category.name == name
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category = Category(
        restaurant_id=restaurant_id,
        name=name,
        icon=data.icon
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/", response_model=list[CategoryOut])
def list_categories(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    return (
        db.query(Category)
        .filter(Category.restaurant_id == restaurant_id)
        .order_by(Category.name)
        .all()
    )
