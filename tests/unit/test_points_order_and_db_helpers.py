import asyncio
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

import db.database as database_module
import db.session as session_module
import utils.jwt as jwt_module
import utils.points as points_module
from controllers.order_controller import (
    accept_order,
    create_or_update_order,
    ensure_transition,
    kitchen_ws,
    list_kitchen_orders,
    my_orders,
    preparing_order,
    served_order,
    ready_order,
    top_10_most_ordered_menu_items,
    update_status,
    customer_ws,
)
from schemas.order_schema import OrderCreate, OrderItemCreate


class QueryStub:
    def __init__(self, first_value=None, all_value=None, scalar_value=None):
        self.first_value = first_value
        self.all_value = list(all_value or [])
        self.scalar_value = scalar_value

    def filter(self, *args, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def options(self, *args, **kwargs):
        return self

    def group_by(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def first(self):
        return self.first_value

    def all(self):
        return list(self.all_value)

    def scalar(self):
        return self.scalar_value


class DBSequence:
    def __init__(self, queries):
        self.queries = list(queries)
        self.added = []
        self.committed = False
        self.refreshed = []
        self.flushed = False
        self.closed = False

    def query(self, *args, **kwargs):
        return self.queries.pop(0)

    def add(self, instance):
        if getattr(instance, "id", None) is None:
            instance.id = uuid4()
        if getattr(instance, "created_at", None) is None:
            instance.created_at = datetime(2026, 3, 27, 10, 0, 0)
        self.added.append(instance)

    def commit(self):
        self.committed = True

    def refresh(self, instance):
        self.refreshed.append(instance)

    def flush(self):
        self.flushed = True
        for instance in self.added:
            if getattr(instance, "id", None) is None:
                instance.id = uuid4()
            if getattr(instance, "created_at", None) is None:
                instance.created_at = datetime(2026, 3, 27, 10, 0, 0)

    def close(self):
        self.closed = True


def test_earn_points_from_order_handles_all_paths(monkeypatch):
    class DummyColumn:
        def __eq__(self, other):
            return other

    class FakePointTransaction:
        order_id = DummyColumn()
        reason = DummyColumn()

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class FakeUserPoint:
        user_id = DummyColumn()

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(points_module, "PointTransaction", FakePointTransaction)
    monkeypatch.setattr(points_module, "UserPoint", FakeUserPoint)

    order = SimpleNamespace(id=uuid4(), total_amount=100)
    assert points_module.earn_points_from_order(
        DBSequence([QueryStub(first_value=object())]),
        user_id=uuid4(),
        order=order,
    ) == 0

    zero_order = SimpleNamespace(id=uuid4(), total_amount=0)
    assert points_module.earn_points_from_order(
        DBSequence([QueryStub(first_value=None)]),
        user_id=uuid4(),
        order=zero_order,
    ) == 0

    user_id = uuid4()
    db = DBSequence([QueryStub(first_value=None), QueryStub(first_value=None)])
    earned = points_module.earn_points_from_order(db, user_id=user_id, order=order)
    assert earned == 1
    assert db.flushed is True
    assert len(db.added) == 2

    existing_user_point = SimpleNamespace(total_points=5)
    db = DBSequence([QueryStub(first_value=None), QueryStub(first_value=existing_user_point)])
    earned = points_module.earn_points_from_order(db, user_id=user_id, order=order)
    assert earned == 1
    assert existing_user_point.total_points == 6


def test_verify_token_and_db_generators(monkeypatch):
    assert jwt_module.verify_token("bad-token") is None

    user = SimpleNamespace(id="user-1")

    class SessionFactory:
        def __call__(self):
            return DBSequence([QueryStub(first_value=user)])

    monkeypatch.setattr(jwt_module, "decode_token", lambda token: {"user_id": "user-1"})
    monkeypatch.setattr(jwt_module, "SessionLocal", SessionFactory())
    assert jwt_module.verify_token("good-token") is user

    monkeypatch.setattr(jwt_module, "decode_token", lambda token: {})
    assert jwt_module.verify_token("missing-user") is None

    db = DBSequence([])
    monkeypatch.setattr(database_module, "SessionLocal", lambda: db)
    gen = database_module.get_db()
    assert next(gen) is db
    with pytest.raises(StopIteration):
        next(gen)
    assert db.closed is True

    db = DBSequence([])
    monkeypatch.setattr(session_module, "SessionLocal", lambda: db)
    gen = session_module.get_db()
    assert next(gen) is db
    with pytest.raises(StopIteration):
        next(gen)
    assert db.closed is True


def test_order_transition_helpers_and_listing(monkeypatch):
    ensure_transition("pending", "confirmed")
    with pytest.raises(HTTPException):
        ensure_transition("pending", "ready")

    calls = []
    monkeypatch.setattr("controllers.order_controller.publish_event", lambda event, payload: calls.append((event, payload)))
    monkeypatch.setattr(
        "controllers.order_controller.manager",
        SimpleNamespace(broadcast=lambda key, message: calls.append((key, message))),
    )

    order = SimpleNamespace(id=uuid4(), restaurant_id=uuid4(), qr_id=uuid4(), status="confirmed")
    db = DBSequence([])
    update_status(db, order, "preparing")
    assert order.status == "preparing"
    assert db.committed is True
    assert db.refreshed == [order]
    assert calls[0][0] == "ORDER_STATUS_UPDATED"

    user = SimpleNamespace(role="staff", restaurant_id=uuid4(), id=uuid4())
    order_row = SimpleNamespace(
        id=uuid4(),
        status="pending",
        created_at="2026-03-27T10:00:00",
        table=SimpleNamespace(name="A1"),
        lines=[
            SimpleNamespace(
                menu_item_id=uuid4(),
                item_name="Tea",
                qty=2,
                note=None,
                menu_item=SimpleNamespace(image_url="/img.png"),
            )
        ],
    )

    kitchen = list_kitchen_orders(db=DBSequence([QueryStub(all_value=[order_row])]), current_user=user)
    assert kitchen[0]["table_name"] == "A1"
    assert kitchen[0]["lines"][0]["item_name"] == "Tea"

    my_result = my_orders(db=DBSequence([QueryStub(all_value=[order_row])]), current_user=user)
    assert my_result == [order_row]


def test_top_ordered_and_create_or_update_order_new_flow(monkeypatch):
    calls = []

    async def broadcast(key, message):
        calls.append((key, message))

    monkeypatch.setattr("controllers.order_controller.publish_event", lambda event, payload: calls.append((event, payload)))
    monkeypatch.setattr("controllers.order_controller.manager", SimpleNamespace(broadcast=broadcast))

    menu_row = SimpleNamespace(
        id=uuid4(),
        name="Pho",
        price=Decimal("12.5"),
        image_url="/img.png",
        total_qty=7,
    )
    ranked = top_10_most_ordered_menu_items(
        restaurant_id=uuid4(),
        db=DBSequence([QueryStub(all_value=[menu_row])]),
    )
    assert ranked == [
        {
            "id": menu_row.id,
            "name": "Pho",
            "price": 12.5,
            "image_url": "/img.png",
            "total_ordered": 7,
        }
    ]

    restaurant_id = uuid4()
    table_id = uuid4()
    qr_id = uuid4()
    menu_id = uuid4()
    current_user = SimpleNamespace(id=uuid4())
    payload = OrderCreate(
        session_token="session-1",
        items=[OrderItemCreate(menu_item_id=menu_id, qty=2, note="less spicy")],
    )
    db = DBSequence(
        [
            QueryStub(first_value=SimpleNamespace(qr_id=qr_id)),
            QueryStub(first_value=SimpleNamespace(id=qr_id, restaurant_id=restaurant_id, table_id=table_id)),
            QueryStub(first_value=None),
            QueryStub(first_value=SimpleNamespace(id=menu_id, name="Tea", price=Decimal("3.5"), is_available=True)),
            QueryStub(first_value=None),
            QueryStub(scalar_value=Decimal("7.0")),
        ]
    )

    order = asyncio.run(create_or_update_order(payload, db=db, current_user=current_user))

    assert order.user_id == current_user.id
    assert order.total_amount == Decimal("7.0")
    assert db.flushed is True
    assert len(db.added) == 2
    assert calls[0][0] == "ORDER_CREATED"
    assert calls[1][0] == str(order.qr_id)
    assert calls[2][0] == f"kitchen:{order.restaurant_id}"


def test_create_or_update_order_updates_existing_and_rejects_invalid_inputs(monkeypatch):
    calls = []

    async def broadcast(key, message):
        calls.append((key, message))

    monkeypatch.setattr("controllers.order_controller.publish_event", lambda event, payload: calls.append((event, payload)))
    monkeypatch.setattr("controllers.order_controller.manager", SimpleNamespace(broadcast=broadcast))

    restaurant_id = uuid4()
    table_id = uuid4()
    qr_id = uuid4()
    menu_id = uuid4()
    current_user = SimpleNamespace(id=uuid4())
    paid_order = SimpleNamespace(
        id=uuid4(),
        restaurant_id=restaurant_id,
        table_id=table_id,
        qr_id=qr_id,
        status="paid",
        total_amount=0,
        created_at=datetime(2026, 3, 27, 10, 0, 0),
    )
    existing_order = SimpleNamespace(
        id=uuid4(),
        restaurant_id=restaurant_id,
        table_id=table_id,
        qr_id=qr_id,
        status="confirmed",
        total_amount=0,
        created_at=datetime(2026, 3, 27, 10, 0, 0),
        user_id=None,
    )
    line = SimpleNamespace(qty=1)
    payload = OrderCreate(
        session_token="session-2",
        items=[OrderItemCreate(menu_item_id=menu_id, qty=2, note=None)],
    )

    db = DBSequence(
        [
            QueryStub(first_value=SimpleNamespace(qr_id=qr_id)),
            QueryStub(first_value=SimpleNamespace(id=qr_id, restaurant_id=restaurant_id, table_id=table_id)),
            QueryStub(first_value=existing_order),
            QueryStub(first_value=SimpleNamespace(id=menu_id, name="Milk Tea", price=Decimal("5"), is_available=True)),
            QueryStub(first_value=line),
            QueryStub(scalar_value=Decimal("15")),
        ]
    )

    order = asyncio.run(create_or_update_order(payload, db=db, current_user=current_user))

    assert order is existing_order
    assert line.qty == 3
    assert calls[0][0] == "ORDER_UPDATED"
    assert calls[1][0] == str(qr_id)
    assert all(call[0] != f"kitchen:{restaurant_id}" for call in calls)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            create_or_update_order(
                payload,
                db=DBSequence(
                    [
                        QueryStub(first_value=SimpleNamespace(qr_id=qr_id)),
                        QueryStub(first_value=SimpleNamespace(id=qr_id, restaurant_id=restaurant_id, table_id=table_id)),
                        QueryStub(first_value=paid_order),
                    ]
                ),
                current_user=current_user,
            )
        )
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            create_or_update_order(
                payload,
                db=DBSequence([
                    QueryStub(first_value=SimpleNamespace(qr_id=qr_id)),
                    QueryStub(first_value=SimpleNamespace(id=qr_id, restaurant_id=restaurant_id, table_id=table_id)),
                    QueryStub(first_value=None),
                    QueryStub(first_value=None),
                    QueryStub(first_value=None),
                ]),
                current_user=current_user,
            )
        )
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            create_or_update_order(
                payload,
                db=DBSequence([
                    QueryStub(first_value=SimpleNamespace(qr_id=qr_id)),
                    QueryStub(first_value=None),
                ]),
                current_user=current_user,
            )
        )
    assert exc_info.value.status_code == 404

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            create_or_update_order(
                payload,
                db=DBSequence([
                    QueryStub(first_value=None),
                ]),
                current_user=current_user,
            )
        )
    assert exc_info.value.status_code == 401


def test_accept_served_and_websocket_order_paths(monkeypatch):
    calls = []
    monkeypatch.setattr("controllers.order_controller.publish_event", lambda event, payload: calls.append((event, payload)))
    monkeypatch.setattr(
        "controllers.order_controller.manager",
        SimpleNamespace(
            broadcast=lambda key, message: calls.append((key, message)),
            connect=None,
            disconnect=None,
        ),
    )

    user = SimpleNamespace(role="staff", restaurant_id=uuid4(), id=uuid4())
    order = SimpleNamespace(
        id=uuid4(),
        qr_id=uuid4(),
        restaurant_id=user.restaurant_id,
        status="pending",
    )
    assert accept_order(order.id, db=DBSequence([QueryStub(first_value=order)]), current_user=user) == {
        "ok": True,
        "status": "confirmed",
    }
    assert calls[-1][0] == str(order.qr_id)
    assert order.status == "confirmed"

    with pytest.raises(HTTPException):
        accept_order(uuid4(), db=DBSequence([QueryStub(first_value=None)]), current_user=user)

    handled_order = SimpleNamespace(id=uuid4(), qr_id=uuid4(), restaurant_id=user.restaurant_id, status="confirmed")
    with pytest.raises(HTTPException):
        accept_order(handled_order.id, db=DBSequence([QueryStub(first_value=handled_order)]), current_user=user)

    served_calls = []
    monkeypatch.setattr("controllers.order_controller.publish_event", lambda event, payload: served_calls.append((event, payload)))
    monkeypatch.setattr(
        "controllers.order_controller.manager",
        SimpleNamespace(broadcast=lambda key, message: served_calls.append((key, message))),
    )
    monkeypatch.setattr("controllers.order_controller.earn_points_from_order", lambda db, user_id, order: 1)

    served_order_row = SimpleNamespace(
        id=uuid4(),
        qr_id=uuid4(),
        restaurant_id=user.restaurant_id,
        status="ready",
        user_id=user.id,
        total_amount=0,
    )
    served_db = DBSequence([
        QueryStub(first_value=served_order_row),
        QueryStub(scalar_value=Decimal("20")),
        QueryStub(first_value=None),
    ])
    assert served_order(served_order_row.id, db=served_db, current_user=user) == {
        "ok": True,
        "status": "served",
    }
    assert served_order_row.status == "served"
    assert served_calls[0][0] == "ORDER_STATUS_UPDATED"
    assert served_calls[-1][0] == str(served_order_row.qr_id)

    with pytest.raises(HTTPException):
        served_order(
            uuid4(),
            db=DBSequence([
                QueryStub(first_value=SimpleNamespace(id=uuid4(), qr_id=uuid4(), restaurant_id=user.restaurant_id, status="ready", user_id=user.id)),
                QueryStub(scalar_value=Decimal("0")),
                QueryStub(first_value=None),
            ]),
            current_user=user,
        )

    earned_calls = []
    monkeypatch.setattr("controllers.order_controller.earn_points_from_order", lambda db, user_id, order: earned_calls.append((user_id, order)) or 1)

    served_order_no_reward = SimpleNamespace(
        id=uuid4(),
        qr_id=uuid4(),
        restaurant_id=user.restaurant_id,
        status="ready",
        user_id=user.id,
        total_amount=0,
    )
    served_db_no_reward = DBSequence([
        QueryStub(first_value=served_order_no_reward),
        QueryStub(scalar_value=Decimal("25")),
        QueryStub(first_value=object()),
    ])
    assert served_order(served_order_no_reward.id, db=served_db_no_reward, current_user=user) == {
        "ok": True,
        "status": "served",
    }
    assert earned_calls == []

    served_order_no_user = SimpleNamespace(
        id=uuid4(),
        qr_id=uuid4(),
        restaurant_id=user.restaurant_id,
        status="ready",
        user_id=None,
        total_amount=0,
    )
    served_db_no_user = DBSequence([
        QueryStub(first_value=served_order_no_user),
        QueryStub(scalar_value=Decimal("30")),
        QueryStub(first_value=None),
    ])
    assert served_order(served_order_no_user.id, db=served_db_no_user, current_user=user) == {
        "ok": True,
        "status": "served",
    }

    with pytest.raises(HTTPException):
        served_order(uuid4(), db=DBSequence([QueryStub(first_value=None)]), current_user=user)

    class FakeWebSocket:
        def __init__(self):
            self.accepted = False
            self.closed = None
            self.received = 0
            self.sent = []

        async def accept(self):
            self.accepted = True

        async def receive_text(self):
            self.received += 1
            raise RuntimeError("stop")

        async def send_json(self, message):
            self.sent.append(message)

        async def close(self, code):
            self.closed = code

    ws_events = []

    async def connect(key, websocket):
        ws_events.append(("connect", key))

    def disconnect(key, websocket):
        ws_events.append(("disconnect", key))

    monkeypatch.setattr(
        "controllers.order_controller.manager",
        SimpleNamespace(
            connect=connect,
            disconnect=disconnect,
        ),
    )

    websocket = FakeWebSocket()
    asyncio.run(customer_ws(websocket, qr_id="qr-1"))
    assert ws_events == [("connect", "qr-1"), ("disconnect", "qr-1")]

    websocket = FakeWebSocket()
    asyncio.run(kitchen_ws(websocket, restaurant_id="rest-1", token=None))
    assert websocket.closed == 1008

    monkeypatch.setattr("controllers.order_controller.verify_token", lambda token: None)
    websocket = FakeWebSocket()
    asyncio.run(kitchen_ws(websocket, restaurant_id="rest-1", token="bad"))
    assert websocket.closed == 1008

    monkeypatch.setattr(
        "controllers.order_controller.verify_token",
        lambda token: SimpleNamespace(role="staff"),
    )
    ws_events.clear()
    websocket = FakeWebSocket()
    asyncio.run(kitchen_ws(websocket, restaurant_id="rest-1", token="good"))
    assert ws_events == [("connect", "kitchen:rest-1"), ("disconnect", "kitchen:rest-1")]


def test_preparing_and_ready_order_routes(monkeypatch):
    user = SimpleNamespace(role="staff", restaurant_id=uuid4())
    order = SimpleNamespace(id=uuid4(), status="confirmed")
    transitions = []
    monkeypatch.setattr("controllers.order_controller.update_status", lambda db, order, next_status: transitions.append(next_status))

    assert preparing_order(order.id, db=DBSequence([QueryStub(first_value=order)]), current_user=user) == {
        "ok": True,
        "status": "preparing",
    }
    assert ready_order(order.id, db=DBSequence([QueryStub(first_value=order)]), current_user=user) == {
        "ok": True,
        "status": "ready",
    }
    assert transitions == ["preparing", "ready"]

    with pytest.raises(HTTPException):
        preparing_order(uuid4(), db=DBSequence([QueryStub(first_value=None)]), current_user=user)

    with pytest.raises(HTTPException):
        ready_order(uuid4(), db=DBSequence([QueryStub(first_value=None)]), current_user=user)
