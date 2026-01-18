from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from utils.dependencies import get_current_user
from utils.permissions import require_roles

from models.order import Order
from models.order_line import OrderLine
from models.menu_item import MenuItem

router = APIRouter(
    prefix="/dashboard/menu",
    tags=["Dashboard - Menu Analytics"]
)
@router.get("/top-items")
def top_menu_items(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    rows = (
        db.query(
            MenuItem.id.label("menu_item_id"),
            MenuItem.name.label("menu_name"),
            func.sum(OrderLine.qty).label("total_qty"),
            func.sum(OrderLine.qty * OrderLine.unit_price).label("revenue"),
        )
        .join(OrderLine, OrderLine.menu_item_id == MenuItem.id)
        .join(Order, Order.id == OrderLine.order_id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .group_by(MenuItem.id)
        .order_by(func.sum(OrderLine.qty).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "menu_item_id": r.menu_item_id,
            "name": r.menu_name,
            "sold_qty": int(r.total_qty or 0),
            "revenue": float(r.revenue or 0),
        }
        for r in rows
    ]
@router.get("/revenue")
def menu_revenue(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    rows = (
        db.query(
            MenuItem.name.label("menu_name"),
            func.sum(OrderLine.qty * OrderLine.unit_price).label("revenue"),
        )
        .join(OrderLine, OrderLine.menu_item_id == MenuItem.id)
        .join(Order, Order.id == OrderLine.order_id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
        )
        .group_by(MenuItem.name)
        .order_by(func.sum(OrderLine.qty * OrderLine.unit_price).desc())
        .all()
    )

    return [
        {
            "name": r.menu_name,
            "revenue": float(r.revenue or 0),
        }
        for r in rows
    ]
@router.get("/trends")
def menu_trends(
    menu_item_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["owner", "staff"])

    rows = (
        db.query(
            func.date_trunc("day", Order.created_at).label("day"),
            func.sum(OrderLine.qty).label("sold_qty"),
        )
        .join(OrderLine, OrderLine.order_id == Order.id)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == "served",
            OrderLine.menu_item_id == menu_item_id,
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    return [
        {
            "date": r.day.date().isoformat(),
            "sold_qty": int(r.sold_qty or 0),
        }
        for r in rows
    ]
