from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from utils.dependencies import get_current_user
from utils.permissions import require_roles

from models.user_point import UserPoint
from models.point_transaction import PointTransaction
from models.order import Order
from models.user import User

router = APIRouter(
    prefix="/dashboard/points",
    tags=["Dashboard - Loyalty Points"]
)
@router.get("/summary")
def point_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    total_points = (
        db.query(func.coalesce(func.sum(PointTransaction.points), 0))
        .join(Order, Order.id == PointTransaction.order_id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .scalar()
    )

    total_customers = (
        db.query(func.count(UserPoint.user_id))
        .join(Order, Order.user_id == UserPoint.user_id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            UserPoint.total_points > 0,
        )
        .distinct()
        .scalar()
    )

    return {
        "total_points_issued": total_points,
        "total_customers_with_points": total_customers,
    }
@router.get("/top-customers")
def top_customers_by_points(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    rows = (
        db.query(
            User.id,
            User.display_name,
            User.email,
            UserPoint.total_points,
        )
        .join(UserPoint, UserPoint.user_id == User.id)
        .join(Order, Order.user_id == User.id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            UserPoint.total_points > 0,
        )
        .order_by(UserPoint.total_points.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "user_id": r.id,
            "name": r.display_name or r.email,
            "total_points": r.total_points,
        }
        for r in rows
    ]
@router.get("/transactions")
def point_transactions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    rows = (
        db.query(
            PointTransaction.id,
            PointTransaction.points,
            PointTransaction.created_at,
            User.display_name,
            User.email,
            Order.id.label("order_id"),
        )
        .join(Order, Order.id == PointTransaction.order_id)
        .join(User, User.id == PointTransaction.user_id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .order_by(PointTransaction.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "transaction_id": r.id,
            "order_id": r.order_id,
            "customer": r.display_name or r.email,
            "points": r.points,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
