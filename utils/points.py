from sqlalchemy.orm import Session
from models.user_point import UserPoint
from models.point_transaction import PointTransaction
from decimal import Decimal

POINT_RATE = Decimal("0.01")

def earn_points_from_order(db: Session, user_id, order):
    # ===== CHỐNG CỘNG TRÙNG =====
    existed = db.query(PointTransaction).filter(
        PointTransaction.order_id == order.id,
        PointTransaction.reason == "ORDER_SERVED"
    ).first()

    if existed:
        return 0

    earned = int(order.total_amount * POINT_RATE)
    if earned <= 0:
        return 0

    # ===== LẤY HOẶC TẠO USER_POINT =====
    user_point = db.query(UserPoint).filter(
        UserPoint.user_id == user_id
    ).first()

    if not user_point:
        user_point = UserPoint(
            user_id=user_id,
            total_points=0
        )
        db.add(user_point)
        db.flush()

    user_point.total_points += earned

    # ===== GHI LỊCH SỬ =====
    tx = PointTransaction(
        user_id=user_id,
        order_id=order.id,
        points=earned,
        reason="ORDER_SERVED"
    )
    db.add(tx)

    return earned
