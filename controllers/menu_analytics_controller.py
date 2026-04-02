from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import get_db
from models.menu_item import MenuItem
from models.order import Order
from models.order_line import OrderLine
from models.user import User
from utils.dependencies import get_current_user
from utils.permissions import require_roles

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
VALIDATION_ERROR_RESPONSE = {422: {"description": "Validation Error"}}

router = APIRouter(
    prefix="/dashboard/menu",
    tags=["Dashboard - Menu Analytics"],
)


@router.get("/top-items", responses=VALIDATION_ERROR_RESPONSE)
def top_menu_items(
    db: DbSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    require_roles(current_user, ["owner", "staff"])

    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 100")

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
            "menu_item_id": row.menu_item_id,
            "name": row.menu_name,
            "sold_qty": int(row.total_qty or 0),
            "revenue": float(row.revenue or 0),
        }
        for row in rows
    ]


@router.get("/revenue")
def menu_revenue(
    db: DbSession,
    current_user: CurrentUser,
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
            "name": row.menu_name,
            "revenue": float(row.revenue or 0),
        }
        for row in rows
    ]


@router.get("/trends", responses=VALIDATION_ERROR_RESPONSE)
def menu_trends(
    menu_item_id: Annotated[str, Query(min_length=1)],
    db: DbSession,
    current_user: CurrentUser,
):
    require_roles(current_user, ["owner", "staff"])

    if not menu_item_id:
        raise HTTPException(status_code=422, detail="menu_item_id must not be empty")

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
            "date": row.day.date().isoformat(),
            "sold_qty": int(row.sold_qty or 0),
        }
        for row in rows
    ]
