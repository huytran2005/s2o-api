from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
)
from sqlalchemy.orm import Session

from db.database import get_db
from models.order import Order
from models.order_line import OrderLine
from models.guest_session import GuestSession
from models.qr_code import QRCode
from models.menu_item import MenuItem

from schemas.order_schema import OrderCreate
from utils.ws_manager import manager
from utils.dependencies import get_current_user
from utils.permissions import require_roles
from utils.jwt import verify_token

router = APIRouter(prefix="/orders", tags=["Orders"])

ACTIVE_STATUSES = ["pending", "confirmed", "preparing"]

# =====================================================
# CREATE / UPDATE ORDER (GUEST – KHÔNG LOGIN)
# =====================================================
@router.post("/")
async def create_or_update_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
):
    # 1. Validate guest session
    session = db.query(GuestSession).filter(
        GuestSession.session_token == payload.session_token,
        GuestSession.expires_at > datetime.utcnow()
    ).first()

    if not session:
        raise HTTPException(status_code=401, detail="Session expired")

    # 2. Get QR
    qr = db.query(QRCode).filter(QRCode.id == session.qr_id).first()
    if not qr:
        raise HTTPException(404, "QR not found")

    # 3. Get active order
    order = db.query(Order).filter(
        Order.qr_id == qr.id,
        Order.status.in_(ACTIVE_STATUSES)
    ).order_by(Order.created_at.desc()).first()

    is_new_order = False
    if not order:
        order = Order(
            restaurant_id=qr.restaurant_id,
            table_id=qr.table_id,
            qr_id=qr.id,
            status="pending",
            total_amount=0
        )
        db.add(order)
        db.flush()  # để có order.id
        is_new_order = True

    if order.status == "paid":
        raise HTTPException(400, "Order already paid")

    # 4. Add / merge items
    for item in payload.items:
        menu = db.query(MenuItem).filter(
            MenuItem.id == item.menu_item_id,
            MenuItem.is_available == True
        ).first()

        if not menu:
            raise HTTPException(400, "Menu item not available")

        line = db.query(OrderLine).filter(
            OrderLine.order_id == order.id,
            OrderLine.menu_item_id == menu.id
        ).first()

        if line:
            line.qty += item.qty
        else:
            db.add(OrderLine(
                order_id=order.id,
                menu_item_id=menu.id,
                item_name=menu.name,
                qty=item.qty,
                unit_price=menu.price,
                note=item.note
            ))

    # 5. Recalculate total (AN TOÀN)
    order.total_amount = sum(
        l.qty * l.unit_price for l in order.lines
    )

    db.commit()
    db.refresh(order)

    # =================================================
    # REALTIME PUSH
    # =================================================

    # Push realtime cho KHÁCH
    await manager.broadcast(
        str(order.qr_id),
        {
            "type": "ORDER_UPDATED",
            "order_id": str(order.id),
            "status": order.status,
            "total": float(order.total_amount)
        }
    )

    # Push realtime cho BẾP (chỉ khi order mới)
    if is_new_order:
        await manager.broadcast(
            f"kitchen:{order.restaurant_id}",
            {
                "type": "NEW_ORDER",
                "order_id": str(order.id),
                "table_id": str(order.table_id),
                "total": float(order.total_amount),
                "created_at": order.created_at.isoformat()
            }
        )

    return order


# =====================================================
# STAFF / BẾP NHẬN ĐƠN (BẮT BUỘC LOGIN)
# =====================================================
@router.patch("/{order_id}/accept")
def accept_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    if order.status != "pending":
        raise HTTPException(400, "Order already handled")

    order.status = "confirmed"
    db.commit()

    # Push realtime lại cho khách
    manager.broadcast(
        str(order.qr_id),
        {
            "type": "ORDER_STATUS",
            "order_id": str(order.id),
            "status": order.status
        }
    )

    return {"ok": True, "status": order.status}


# =====================================================
# WEBSOCKET – CUSTOMER (KHÔNG LOGIN)
# =====================================================
@router.websocket("/ws/orders/{qr_id}")
async def customer_ws(websocket: WebSocket, qr_id: str):
    await manager.connect(qr_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(qr_id, websocket)


# =====================================================
# WEBSOCKET – KITCHEN (STAFF / OWNER – LOGIN BẮT BUỘC)
# =====================================================
@router.websocket("/ws/kitchen/{restaurant_id}")
async def kitchen_ws(
    websocket: WebSocket,
    restaurant_id: str,
    token: str | None = None,
):
    if not token:
        await websocket.close(code=1008)
        return

    user = verify_token(token)
    if not user or user.role not in ["staff", "owner"]:
        await websocket.close(code=1008)
        return

    await manager.connect(f"kitchen:{restaurant_id}", websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(f"kitchen:{restaurant_id}", websocket)
VALID_TRANSITIONS = {
    "pending": "confirmed",
    "confirmed": "preparing",
    "preparing": "served",
}

def ensure_transition(current: str, next_status: str):
    expected = VALID_TRANSITIONS.get(current)
    if expected != next_status:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status {current} → {next_status}"
        )


def update_status(db, order, next_status: str):
    ensure_transition(order.status, next_status)

    order.status = next_status
    db.commit()
    db.refresh(order)

    # Push realtime cho khách
    manager.broadcast(
        str(order.qr_id),
        {
            "type": "ORDER_STATUS",
            "order_id": str(order.id),
            "status": order.status
        }
    )
@router.patch("/{order_id}/accept")
def accept_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    update_status(db, order, "confirmed")
    return {"ok": True, "status": "confirmed"}
@router.patch("/{order_id}/preparing")
def preparing_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    update_status(db, order, "preparing")
    return {"ok": True, "status": "preparing"}
@router.patch("/{order_id}/served")
def served_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    update_status(db, order, "served")
    return {"ok": True, "status": "served"}
@router.get("/kitchen")
def list_kitchen_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    orders = (
        db.query(Order)
        .filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status.in_(["pending", "confirmed", "preparing"])
        )
        .order_by(Order.created_at.asc())
        .all()
    )

    return orders
