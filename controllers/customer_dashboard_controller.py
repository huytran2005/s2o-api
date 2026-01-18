from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from utils.dependencies import get_current_user
from utils.permissions import require_roles

from models.user import User
from models.order import Order
from models.user_point import UserPoint

router = APIRouter(
    prefix="/dashboard/customers",
    tags=["Dashboard - Customers"]
)

@router.get("")
def list_customers(
    search: str | None = Query(default=None),
    filter: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    # Base query: khách đã từng order tại quán
    q = (
        db.query(
            User.id.label("user_id"),
            User.display_name,
            User.email,
            User.phone,
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.sum(Order.total_amount), 0).label("total_spent"),
            func.max(Order.created_at).label("last_visit"),
            func.coalesce(UserPoint.total_points, 0).label("total_points"),
        )
        .join(Order, Order.user_id == User.id)
        .outerjoin(UserPoint, UserPoint.user_id == User.id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .group_by(User.id, UserPoint.total_points)
    )

    # =====================
    # SEARCH
    # =====================
    if search:
        q = q.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.display_name.ilike(f"%{search}%")) |
            (User.phone.ilike(f"%{search}%"))
        )

    # =====================
    # FILTERS
    # =====================
    if filter == "new":
        # khách mới: chỉ có 1 đơn
        q = q.having(func.count(Order.id) == 1)

    elif filter == "returning":
        # khách quay lại: >= 2 đơn
        q = q.having(func.count(Order.id) >= 2)

    elif filter == "high_points":
        # khách có nhiều điểm (threshold đơn giản)
        q = q.having(func.coalesce(UserPoint.total_points, 0) >= 1000)

    rows = q.order_by(func.max(Order.created_at).desc()).all()

    return [
        {
            "user_id": r.user_id,
            "name": r.display_name or r.email,
            "email": r.email,
            "phone": r.phone,
            "total_orders": r.total_orders,
            "total_spent": float(r.total_spent),
            "total_points": r.total_points,
            "last_visit": r.last_visit.isoformat() if r.last_visit else None,
        }
        for r in rows
    ]
