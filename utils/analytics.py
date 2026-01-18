from datetime import datetime

def log_analytics(db, event: str, payload: dict):
    # Cách đơn giản: log ra stdout hoặc ghi bảng riêng
    print("[ANALYTICS]", {
        "event": event,
        "order_id": payload.get("order_id"),
        "restaurant_id": payload.get("restaurant_id"),
        "status": payload.get("status"),
        "ts": datetime.utcnow().isoformat()
    })
