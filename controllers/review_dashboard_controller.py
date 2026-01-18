from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from utils.dependencies import get_current_user
from utils.permissions import require_roles

from models.review import MenuItemReview
from models.menu_item import MenuItem
from models.order import Order

router = APIRouter(
    prefix="/dashboard/reviews",
    tags=["Dashboard - Reviews"]
)
@router.get("/summary")
def review_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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
@router.get("")
def list_reviews(
    rating: int | None = Query(default=None),
    menu_item_id: str | None = Query(default=None),
    from_date: str | None = Query(default=None),
    to_date: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    q = (
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

    # Filter theo số sao
    if rating:
        q = q.filter(MenuItemReview.rating == rating)

    # Filter theo món
    if menu_item_id:
        q = q.filter(MenuItemReview.menu_item_id == menu_item_id)

    # Filter theo thời gian
    if from_date:
        q = q.filter(MenuItemReview.created_at >= from_date)

    if to_date:
        q = q.filter(MenuItemReview.created_at <= to_date)

    rows = q.order_by(MenuItemReview.created_at.desc()).limit(100).all()

    return [
        {
            "review_id": r.id,
            "menu_item": r.menu_name,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
@router.get("/by-menu")
def reviews_by_menu(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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
            "menu_item_id": r.menu_item_id,
            "menu_item": r.name,
            "total_reviews": r.total_reviews,
            "avg_rating": round(float(r.avg_rating), 2),
        }
        for r in rows
    ]
