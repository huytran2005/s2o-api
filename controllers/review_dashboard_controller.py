from datetime import date, datetime, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import get_db
from models.menu_item import MenuItem
from models.review import MenuItemReview
from models.user import User
from utils.dependencies import get_current_user
from utils.permissions import require_roles

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
VALIDATION_ERROR_RESPONSE = {422: {"description": "Validation Error"}}

router = APIRouter(
    prefix="/dashboard/reviews",
    tags=["Dashboard - Reviews"],
)


@router.get("/summary")
def review_summary(
    db: DbSession,
    current_user: CurrentUser,
):
    require_roles(current_user, ["owner", "staff"])

    base_filter = (
        db.query(MenuItemReview)
        .join(MenuItem, MenuItem.id == MenuItemReview.menu_item_id)
        .filter(MenuItem.restaurant_id == current_user.restaurant_id)
    )

    total_reviews = base_filter.count()

    avg_rating = (
        db.query(func.coalesce(func.avg(MenuItemReview.rating), 0))
        .join(MenuItem, MenuItem.id == MenuItemReview.menu_item_id)
        .filter(MenuItem.restaurant_id == current_user.restaurant_id)
        .scalar()
    )

    bad_reviews = (
        db.query(func.count(MenuItemReview.id))
        .join(MenuItem, MenuItem.id == MenuItemReview.menu_item_id)
        .filter(
            MenuItem.restaurant_id == current_user.restaurant_id,
            MenuItemReview.rating <= 2,
        )
        .scalar()
    )

    return {
        "total_reviews": total_reviews,
        "avg_rating": round(float(avg_rating), 2),
        "bad_reviews": bad_reviews,
    }


@router.get("", responses=VALIDATION_ERROR_RESPONSE)
def list_reviews(
    db: DbSession,
    current_user: CurrentUser,
    rating: Annotated[int | None, Query(ge=1, le=5)] = None,
    menu_item_id: Annotated[str | None, Query(min_length=1)] = None,
    from_date: Annotated[date | None, Query()] = None,
    to_date: Annotated[date | None, Query()] = None,
):
    require_roles(current_user, ["owner", "staff"])

    if rating is not None and not 1 <= rating <= 5:
        raise HTTPException(status_code=422, detail="rating must be between 1 and 5")

    if menu_item_id == "":
        raise HTTPException(status_code=422, detail="menu_item_id must not be empty")

    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=422, detail="from_date must be before or equal to to_date")

    query = (
        db.query(
            MenuItemReview.id,
            MenuItemReview.rating,
            MenuItemReview.comment,
            MenuItemReview.created_at,
            MenuItem.name.label("menu_name"),
        )
        .join(MenuItem, MenuItem.id == MenuItemReview.menu_item_id)
        .filter(MenuItem.restaurant_id == current_user.restaurant_id)
    )

    if rating is not None:
        query = query.filter(MenuItemReview.rating == rating)

    if menu_item_id:
        query = query.filter(MenuItemReview.menu_item_id == menu_item_id)

    if from_date:
        query = query.filter(
            MenuItemReview.created_at >= datetime.combine(from_date, time.min)
        )

    if to_date:
        query = query.filter(
            MenuItemReview.created_at < datetime.combine(to_date + timedelta(days=1), time.min)
        )

    rows = query.order_by(MenuItemReview.created_at.desc()).limit(100).all()

    return [
        {
            "review_id": row.id,
            "menu_item": row.menu_name,
            "rating": row.rating,
            "comment": row.comment,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


@router.get("/by-menu")
def reviews_by_menu(
    db: DbSession,
    current_user: CurrentUser,
):
    require_roles(current_user, ["owner", "staff"])

    rows = (
        db.query(
            MenuItem.id.label("menu_item_id"),
            MenuItem.name,
            func.count(MenuItemReview.id).label("total_reviews"),
            func.coalesce(func.avg(MenuItemReview.rating), 0).label("avg_rating"),
        )
        .join(MenuItemReview, MenuItemReview.menu_item_id == MenuItem.id)
        .filter(MenuItem.restaurant_id == current_user.restaurant_id)
        .group_by(MenuItem.id)
        .order_by(func.count(MenuItemReview.id).desc())
        .all()
    )

    return [
        {
            "menu_item_id": row.menu_item_id,
            "menu_item": row.name,
            "total_reviews": row.total_reviews,
            "avg_rating": round(float(row.avg_rating), 2),
        }
        for row in rows
    ]
