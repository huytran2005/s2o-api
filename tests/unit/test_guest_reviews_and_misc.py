from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import asyncio
from fastapi import HTTPException, Response
from fastapi import WebSocket
from pydantic import ValidationError
from starlette.requests import Request

from controllers.guest.guest_qr import qr_entry as guest_qr_entry
from controllers.guest.me import guest_me
from controllers.guest.me_mobile import me_mobile
from controllers.guest.qr_entry import qr_entry
from controllers.guest.scan import scan_qr
from controllers.guest.session_mobile import create_guest_session_mobile
from controllers.guest.session_web import create_guest_session
from controllers.points_controller import my_points
from controllers.review_controller import create_menu_item_review, get_menu_item_review_stats
from models.guest_session import GuestSession
from models.order import Order
from models.order_line import OrderLine
from schemas.order_schema import OrderCreate, OrderLineResponse, OrderResponse
from schemas.point_schema import PointResponse
from schemas.qr_schema import QRCreateResponse, QRScanResponse
from schemas.review_schema import ReviewCreate
from utils.analytics import log_analytics
from utils.rabbitmq import publish_event
from utils.review_service import (
    check_review_exists,
    create_review,
    validate_order_completed,
    validate_order_line,
)
from utils.reward import reward_on_order_served
from utils.ws_manager import ConnectionManager


class QueryStub:
    def __init__(self, first_value=None, all_value=None):
        self.first_value = first_value
        self.all_value = list(all_value or [])
        self.deleted = None

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.first_value

    def all(self):
        return list(self.all_value)

    def delete(self, synchronize_session=False):
        self.deleted = synchronize_session
        return 1


class DBSequence:
    def __init__(self, queries):
        self.queries = list(queries)
        self.added = []
        self.committed = False
        self.refreshed = []

    def query(self, *args, **kwargs):
        return self.queries.pop(0)

    def add(self, instance):
        self.added.append(instance)

    def commit(self):
        self.committed = True

    def refresh(self, instance):
        self.refreshed.append(instance)


def make_request(user_agent: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [(b"user-agent", user_agent.encode())],
        }
    )


def test_guest_qr_entry_reads_template_and_injects_base_url(monkeypatch, tmp_path):
    template = tmp_path / "guest_qr.html"
    template.write_text("<a>__WEB_BASE_URL__</a>", encoding="utf-8")
    monkeypatch.setattr("controllers.guest.guest_qr.HTML_PATH", template)
    monkeypatch.setenv("WEB_BASE_URL", "https://web.example")

    response = guest_qr_entry(code="abc")

    assert response.status_code == 200
    assert "https://web.example" in response.body.decode()


def test_guest_qr_entry_handles_missing_template(monkeypatch, tmp_path):
    monkeypatch.setattr("controllers.guest.guest_qr.HTML_PATH", tmp_path / "missing.html")

    response = guest_qr_entry(code="abc")

    assert response.status_code == 500


def test_guest_me_endpoints_return_session_payload():
    session = SimpleNamespace(qr_id=uuid4(), expires_at=datetime(2026, 3, 27, 12, 0, 0))

    assert guest_me(session=session)["message"] == "Session OK"
    assert me_mobile(session=session)["message"] == "Mobile session OK"


def test_scan_qr_and_qr_entry_handle_valid_and_invalid_codes():
    qr = SimpleNamespace(code="code-1", table_id="table-1", restaurant_id="rest-1", status="active")
    db = DBSequence([QueryStub(first_value=qr)])
    result = scan_qr("code-1", db=db)
    assert result["qr_code"] == "code-1"

    request = make_request("Android")
    db = DBSequence([QueryStub(first_value=qr)])
    response = qr_entry("code-1", request=request, db=db)
    assert response.status_code == 302
    assert "intent://qr/open?code=code-1" in response.headers["location"]

    request = make_request("Mozilla")
    db = DBSequence([QueryStub(first_value=qr)])
    response = qr_entry("code-1", request=request, db=db)
    assert response.headers["location"].endswith("/?code=code-1")

    with pytest.raises(HTTPException):
        scan_qr("missing", db=DBSequence([QueryStub(first_value=None)]))


def test_guest_session_endpoints_create_sessions(monkeypatch):
    qr = SimpleNamespace(id=uuid4(), table_id=uuid4(), restaurant_id=uuid4())
    db = DBSequence([QueryStub(first_value=qr)])
    monkeypatch.setattr("controllers.guest.session_web.secrets.token_urlsafe", lambda _: "token-web")

    response = Response()
    result = create_guest_session("code-1", response=response, db=db)

    assert result["session_token"] == "token-web"
    assert db.committed is True
    assert isinstance(db.added[0], GuestSession)
    assert "guest_session=token-web" in response.headers["set-cookie"]

    db = DBSequence([QueryStub(first_value=qr)])
    monkeypatch.setattr("controllers.guest.session_mobile.secrets.token_urlsafe", lambda _: "token-mobile")
    mobile_result = create_guest_session_mobile("code-1", db=db)
    assert mobile_result["session_token"] == "token-mobile"


def test_points_and_review_controller_paths(monkeypatch):
    user = SimpleNamespace(id=uuid4())
    db = DBSequence([QueryStub(first_value=SimpleNamespace(total_points=77))])
    assert my_points(db=db, current_user=user) == {"total_points": 77}

    order_line = SimpleNamespace(id=uuid4(), order_id=uuid4())
    order = SimpleNamespace(id=order_line.order_id)
    review = SimpleNamespace(id=uuid4(), rating=5, comment="ok", created_at=datetime(2026, 3, 27, 10, 0, 0))
    monkeypatch.setattr("controllers.review_controller.validate_order_line", lambda db, oid: order_line)
    monkeypatch.setattr("controllers.review_controller.validate_order_completed", lambda db, order: None)
    monkeypatch.setattr("controllers.review_controller.check_review_exists", lambda db, oid: None)
    monkeypatch.setattr("controllers.review_controller.create_review", lambda **kwargs: review)

    result = create_menu_item_review(
        payload=ReviewCreate(order_line_id=order_line.id, rating=5, comment="ok"),
        db=DBSequence([QueryStub(first_value=order)]),
    )
    assert result is review

    stats = get_menu_item_review_stats(
        "menu-1",
        db=DBSequence([QueryStub(all_value=[SimpleNamespace(rating=4), SimpleNamespace(rating=5)])]),
    )
    assert stats == {"avg_rating": 4.5, "total_reviews": 2}
    assert get_menu_item_review_stats("menu-2", db=DBSequence([QueryStub(all_value=[])])) == {
        "avg_rating": 0,
        "total_reviews": 0,
    }


def test_review_service_and_reward_helpers():
    line = SimpleNamespace(id=uuid4(), menu_item_id=uuid4())
    db = DBSequence([QueryStub(first_value=line)])
    assert validate_order_line(db, line.id) is line

    with pytest.raises(HTTPException):
        validate_order_line(DBSequence([QueryStub(first_value=None)]), uuid4())

    validate_order_completed(db=None, order=Order(status="served"))
    with pytest.raises(HTTPException):
        validate_order_completed(db=None, order=Order(status="pending"))

    check_review_exists(DBSequence([QueryStub(first_value=None)]), uuid4())
    with pytest.raises(HTTPException):
        check_review_exists(DBSequence([QueryStub(first_value=object())]), uuid4())

    db = DBSequence([])
    order = Order(id=uuid4(), restaurant_id=uuid4())
    order_line = OrderLine(id=uuid4(), menu_item_id=uuid4())
    created = create_review(db=db, order=order, order_line=order_line, rating=4, comment="nice")
    assert created in db.added
    assert db.committed is True
    assert db.refreshed == [created]

    user_id = uuid4()
    order = SimpleNamespace(id=uuid4(), user_id=user_id, total_amount=25000)
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

    import utils.reward as reward_module

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(reward_module, "PointTransaction", FakePointTransaction)
    monkeypatch.setattr(reward_module, "UserPoint", FakeUserPoint)
    db = DBSequence([QueryStub(first_value=None), QueryStub(first_value=None)])
    assert reward_on_order_served(db, order) is True
    assert len(db.added) == 2

    db = DBSequence([QueryStub(first_value=object())])
    assert reward_on_order_served(db, order) is False
    monkeypatch.undo()


def test_misc_schemas_analytics_rabbitmq_and_ws(monkeypatch, capsys):
    PointResponse(total_points=10)
    QRCreateResponse(qr_id=uuid4(), code="abc")
    QRScanResponse(session_token="token", restaurant={"id": 1}, table=None)
    OrderCreate(session_token="token", items=[])
    OrderLineResponse(
        id=uuid4(),
        item_name="Tea",
        qty=1,
        unit_price=12.5,
        note=None,
        image_url=None,
    )
    OrderResponse(id=uuid4(), status="pending", total_amount=12.5, lines=[])

    with pytest.raises(ValidationError):
        QRScanResponse(session_token="token", restaurant={})

    log_analytics(None, "ORDER_CREATED", {"order_id": "1", "restaurant_id": "2", "status": "pending"})
    assert "[ANALYTICS]" in capsys.readouterr().out

    published = {}

    class Channel:
        def queue_declare(self, **kwargs):
            published["queue"] = kwargs

        def basic_publish(self, **kwargs):
            published["publish"] = kwargs

    class Connection:
        def channel(self):
            return Channel()

        def close(self):
            published["closed"] = True

    monkeypatch.setattr("utils.rabbitmq.pika.URLParameters", lambda url: url)
    monkeypatch.setattr("utils.rabbitmq.pika.BlockingConnection", lambda params: Connection())
    publish_event("ORDER_CREATED", {"id": "1"})
    assert published["queue"]["queue"] == "order_events"
    assert published["closed"] is True

    manager = ConnectionManager()
    sent = []

    class WebSocketStub(WebSocket):
        def __init__(self):
            self.accepted = False

        async def accept(self):
            await asyncio.sleep(0)
            self.accepted = True
            sent.append("accepted")

        async def send_json(self, message):
            await asyncio.sleep(0)
            sent.append(message)

    ws = WebSocketStub()
    asyncio.run(manager.connect("room", ws))
    asyncio.run(manager.broadcast("room", {"ok": True}))
    manager.disconnect("room", ws)
    assert sent == ["accepted", {"ok": True}]
