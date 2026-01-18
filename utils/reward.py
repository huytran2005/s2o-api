from sqlalchemy.orm import Session
from models.point_transaction import PointTransaction
from models.user_point import UserPoint

def reward_on_order_served(db: Session, order):
    # idempotency: chống cộng trùng
    existed = db.query(PointTransaction).filter(
        PointTransaction.order_id == order.id,
        PointTransaction.reason == "ORDER_SERVED"
    ).first()
    if existed:
        return False

    points = int(order.total_amount // 10000)  # ví dụ rule
    tx = PointTransaction(
        user_id=order.user_id,
        order_id=order.id,
        amount=points,
        reason="ORDER_SERVED"
    )
    db.add(tx)

    up = db.query(UserPoint).filter(UserPoint.user_id == order.user_id).first()
    if not up:
        up = UserPoint(user_id=order.user_id, total_points=0)
        db.add(up)
    up.total_points += points

    return True
