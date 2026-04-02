from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import get_db
from models.order import Order
from models.point_transaction import PointTransaction
from models.user import User
from models.user_point import UserPoint
from utils.dependencies import get_current_user
from utils.permissions import require_roles

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
VALIDATION_ERROR_RESPONSE = {422: {"description": "Validation Error"}}

router = APIRouter(
    prefix="/dashboard/points",
    tags=["Dashboard - Loyalty Points"],
)


@router.get("/summary")
def point_summary(
    db: DbSession,
    current_user: CurrentUser,
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


@router.get("/top-customers", responses=VALIDATION_ERROR_RESPONSE)
def top_customers_by_points(
    db: DbSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    require_roles(current_user, ["owner", "staff"])

    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 100")

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
            "user_id": row.id,
            "name": row.display_name or row.email,
            "total_points": row.total_points,
        }
        for row in rows
    ]


@router.get("/transactions")
def point_transactions(
    db: DbSession,
    current_user: CurrentUser,
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
            "transaction_id": row.id,
            "order_id": row.order_id,
            "customer": row.display_name or row.email,
            "points": row.points,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
