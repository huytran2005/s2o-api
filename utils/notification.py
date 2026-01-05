def notify_order_status(user, status: str):
    # Stub: demo backend chỉ cần log
    mapping = {
        "confirmed": "Bếp đã nhận đơn",
        "preparing": "Đang chuẩn bị món",
        "served": "Món đã sẵn sàng",
    }
    msg = mapping.get(status)
    if not msg:
        return
    print(f"[NOTIFY] user={user.id} :: {msg}")
