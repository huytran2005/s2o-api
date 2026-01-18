from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import get_db
from models.order import Order
from models.point_transaction import PointTransaction
from utils.dependencies import get_current_user
from utils.permissions import require_roles

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/overview")
def overview_report(
    type: str,  # day | week | month
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    if type not in ["day", "week", "month"]:
        raise HTTPException(400, "Invalid type")

    # =========================
    # TIME BUCKET
    # =========================
    date_expr = {
        "day": func.date_trunc("day", Order.created_at),
        "week": func.date_trunc("week", Order.created_at),
        "month": func.date_trunc("month", Order.created_at),
    }[type]

    # =========================
    # CHART: revenue + orders
    # =========================
    chart_rows = (
        db.query(
            date_expr.label("time"),
            func.sum(Order.total_amount).label("total_revenue"),
            func.count(Order.id).label("total_orders"),
        )
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .group_by("time")
        .order_by("time")
        .all()
    )

    chart = [
        {
            "time": r.time.isoformat(),
            "total_revenue": float(r.total_revenue or 0),
            "total_orders": r.total_orders,
        }
        for r in chart_rows
    ]

    # =========================
    # SUMMARY KPI
    # =========================

    # Tổng doanh thu + tổng đơn (cùng timeframe)
    summary_row = (
        db.query(
            func.coalesce(func.sum(Order.total_amount), 0),
            func.count(Order.id),
        )
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .one()
    )

    total_revenue, total_orders = summary_row

    # =========================
    # Returning customers
    # Định nghĩa: user có >= 2 order served
    # =========================
    returning_customers = (
        db.query(Order.user_id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
            Order.user_id.isnot(None),
        )
        .group_by(Order.user_id)
        .having(func.count(Order.id) >= 2)
        .count()
    )

    # =========================
    # Total points issued
    # =========================
    total_points = (
        db.query(func.coalesce(func.sum(PointTransaction.points), 0))
        .join(Order, Order.id == PointTransaction.order_id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .scalar()
    )

    return {
        "chart": chart,
        "summary": {
            "total_revenue": float(total_revenue or 0),
            "total_orders": total_orders,
            "returning_customers": returning_customers,
            "total_points_issued": total_points,
        }
    }
