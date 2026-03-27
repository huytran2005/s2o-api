from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

import db.database as database_module
import db.session as session_module
import utils.jwt as jwt_module
import utils.points as points_module
from controllers.order_controller import (
    ensure_transition,
    list_kitchen_orders,
    my_orders,
    preparing_order,
    ready_order,
    update_status,
)


class QueryStub:
    def __init__(self, first_value=None, all_value=None):
        self.first_value = first_value
        self.all_value = list(all_value or [])

    def filter(self, *args, **kwargs):
        return self

    def options(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self.first_value

    def all(self):
        return list(self.all_value)


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
        self.added.append(instance)

    def commit(self):
        self.committed = True

    def refresh(self, instance):
        self.refreshed.append(instance)

    def flush(self):
        self.flushed = True

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
