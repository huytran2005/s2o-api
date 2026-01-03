from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.review_schema import ReviewCreate, ReviewResponse, ReviewStats
from models.order import Order
from models.review import MenuItemReview
from utils.review_service import (
    validate_order_line,
    validate_order_completed,
    check_review_exists,
    create_review
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse)
def create_menu_item_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
):
    order_line = validate_order_line(db, payload.order_line_id)

    order = db.query(Order).filter(Order.id == order_line.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    validate_order_completed(db, order)
    check_review_exists(db, order_line.id)

    review = create_review(
        db=db,
        order=order,
        order_line=order_line,
        rating=payload.rating,
        comment=payload.comment,
    )
    return review


@router.get("/menu-item/{menu_item_id}", response_model=ReviewStats)
def get_menu_item_review_stats(menu_item_id, db: Session = Depends(get_db)):
    reviews = (
        db.query(MenuItemReview)
        .filter(MenuItemReview.menu_item_id == menu_item_id)
        .all()
    )

    if not reviews:
        return {"avg_rating": 0, "total_reviews": 0}

    avg = sum(r.rating for r in reviews) / len(reviews)
    return {
        "avg_rating": round(avg, 2),
        "total_reviews": len(reviews)
    }
