from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.order_line import OrderLine
from models.order import Order
from models.review import MenuItemReview


ALLOWED_ORDER_STATUS = ["completed", "paid", "closed","served"]


def validate_order_line(db: Session, order_line_id):
    line = db.query(OrderLine).filter(OrderLine.id == order_line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Order line not found")
    return line


def validate_order_completed(db: Session, order: Order):
    if order.status not in ALLOWED_ORDER_STATUS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order not completed yet"
        )


def check_review_exists(db: Session, order_line_id):
    exists = (
        db.query(MenuItemReview)
        .filter(MenuItemReview.order_line_id == order_line_id)
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This item has already been reviewed"
        )


def create_review(
    db: Session,
    order: Order,
    order_line: OrderLine,
    rating: int,
    comment: str | None
):
    review = MenuItemReview(
        restaurant_id=order.restaurant_id,
        order_id=order.id,
        order_line_id=order_line.id,
        menu_item_id=order_line.menu_item_id,
        rating=rating,
        comment=comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
