from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from functools import lru_cache
from datetime import datetime, timedelta

from db.database import get_db
from models.order import Order
from models.point_transaction import PointTransaction
from utils.dependencies import get_current_user
from utils.permissions import require_roles

router = APIRouter(prefix="/reports", tags=["Reports"])


# =========================
# INTERNAL: build overview
# =========================
def build_overview(db: Session, restaurant_id: int):
    # ===== Time range: today =====
    now = datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    # ===== 30-minute bucket (48 points/day) =====
    bucket_seconds = 30 * 60  # 1800s

    date_expr = func.to_timestamp(
        (func.extract("epoch", Order.created_at) / bucket_seconds)
        .cast(Integer)
        * bucket_seconds
    )

    # ===== CHART =====
    chart_rows = (
        db.query(
            date_expr.label("time"),
            func.coalesce(func.sum(Order.total_amount), 0).label("total_revenue"),
            func.count(Order.id).label("total_orders"),
        )
        .filter(
            Order.restaurant_id == restaurant_id,
            Order.status == "served",
            Order.created_at >= start_of_day,
            Order.created_at < end_of_day,
        )
        .group_by("time")
        .order_by("time")
        .all()
    )

    chart = [
        {
            "time": r.time.isoformat(),
            "total_revenue": float(r.total_revenue),
            "total_orders": r.total_orders,
        }
        for r in chart_rows
    ]

    # ===== SUMMARY (today) =====
    total_revenue, total_orders = (
        db.query(
            func.coalesce(func.sum(Order.total_amount), 0),
            func.count(Order.id),
        )
        .filter(
            Order.restaurant_id == restaurant_id,
            Order.status == "served",
            Order.created_at >= start_of_day,
            Order.created_at < end_of_day,
        )
        .one()
    )

    returning_customers = (
        db.query(Order.user_id)
        .filter(
            Order.restaurant_id == restaurant_id,
            Order.status == "served",
            Order.created_at >= start_of_day,
            Order.created_at < end_of_day,
            Order.user_id.isnot(None),
        )
        .group_by(Order.user_id)
        .having(func.count(Order.id) >= 2)
        .count()
    )

    total_points = (
        db.query(func.coalesce(func.sum(PointTransaction.points), 0))
        .join(Order, Order.id == PointTransaction.order_id)
        .filter(
            Order.restaurant_id == restaurant_id,
            Order.status == "served",
            Order.created_at >= start_of_day,
            Order.created_at < end_of_day,
        )
        .scalar()
    )

    return {
        "chart": chart,
        "summary": {
            "total_revenue": float(total_revenue),
            "total_orders": total_orders,
            "returning_customers": returning_customers,
            "total_points_issued": total_points,
        },
    }


# =========================
# CACHE: 5 minutes
# =========================
@lru_cache(maxsize=128)
def cached_overview(restaurant_id: int, five_min_key: int):
    from db.database import SessionLocal
    db = SessionLocal()
    try:
        return build_overview(db, restaurant_id)
    finally:
        db.close()


# =========================
# ROUTE
# =========================
@router.get("/overview")
def overview_report(
    request: Request,
    current_user=Depends(get_current_user),
):
    if request.method == "OPTIONS":
        return {}

    require_roles(current_user, ["owner", "staff"])

    # cache key: 5 minutes
    five_min_key = int(datetime.utcnow().timestamp() // 300)

    return cached_overview(
        current_user.restaurant_id,
        five_min_key,
    )
