import importlib
import json
from types import SimpleNamespace

import pytest

import db.database as database_module
import utils.fcm as fcm
import utils.mq_worker as mq_worker
import utils.notification as notification
from models.order import Order
from models.user import User


class QueryStub:
    def __init__(self, first_value=None):
        self.first_value = first_value

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.first_value


class FakeDB:
    def __init__(self, query_map=None):
        self.query_map = query_map or {}
        self.committed = False
        self.closed = False

    def query(self, model):
        return QueryStub(self.query_map.get(model))

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


def test_send_fcm_initializes_once_and_sends_message(monkeypatch):
    calls = []

    class FakeNotification:
        def __init__(self, title, body):
            self.title = title
            self.body = body

    class FakeMessage:
        def __init__(self, notification, token):
            self.notification = notification
            self.token = token

    monkeypatch.setattr(fcm, "_firebase_app", None, raising=False)
    monkeypatch.setattr(fcm.credentials, "Certificate", lambda path: calls.append(("cert", path)) or path)
    monkeypatch.setattr(
        fcm.firebase_admin,
        "initialize_app",
        lambda cred: calls.append(("init", cred)) or "firebase-app",
    )
    monkeypatch.setattr(fcm.messaging, "Notification", FakeNotification)
    monkeypatch.setattr(fcm.messaging, "Message", FakeMessage)
    monkeypatch.setattr(
        fcm.messaging,
        "send",
        lambda message: calls.append(("send", message.token, message.notification.title, message.notification.body))
        or "msg-1",
    )

    first = fcm.send_fcm("token-1", "Hello", "World")
    second = fcm.send_fcm("token-2", "Again", "Body")

    assert first == "msg-1"
    assert second == "msg-1"
    assert calls == [
        ("cert", "secrets/firebase-admin.json"),
        ("init", "secrets/firebase-admin.json"),
        ("send", "token-1", "Hello", "World"),
        ("send", "token-2", "Again", "Body"),
    ]


def test_notify_order_status_prints_for_known_and_unknown_statuses(capsys):
    user = SimpleNamespace(id="user-1")

    notification.notify_order_status(user, "served")
    notification.notify_order_status(user, "cancelled")

    out = capsys.readouterr().out
    assert "[NOTIFY] user=user-1 :: Món đã sẵn sàng" in out
    assert "cancelled" not in out


def test_handle_event_ignores_non_status_events(monkeypatch):
    db = FakeDB()
    calls = []
    monkeypatch.setattr(mq_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(mq_worker, "log_analytics", lambda db, event, payload: calls.append(("analytics", event, payload)))
    monkeypatch.setattr(mq_worker, "notify_order_status", lambda *args, **kwargs: calls.append("notify"))
    monkeypatch.setattr(mq_worker, "reward_on_order_served", lambda *args, **kwargs: calls.append("reward"))

    mq_worker.handle_event("OTHER_EVENT", {"hello": "world"})

    assert calls == [("analytics", "OTHER_EVENT", {"hello": "world"})]
    assert db.closed is True


def test_handle_event_updates_status_and_rewards(monkeypatch):
    order = SimpleNamespace(id="order-1", user_id="user-1", total_amount=50000)
    user = SimpleNamespace(id="user-1")
    db = FakeDB({Order: order, User: user})
    calls = []

    monkeypatch.setattr(mq_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(mq_worker, "log_analytics", lambda db, event, payload: calls.append(("analytics", event)))
    monkeypatch.setattr(mq_worker, "notify_order_status", lambda found_user, status: calls.append(("notify", found_user.id, status)))
    monkeypatch.setattr(mq_worker, "reward_on_order_served", lambda db, order: True)

    mq_worker.handle_event(
        "ORDER_STATUS_UPDATED",
        {"order_id": "order-1", "status": "served"},
    )

    assert ("notify", "user-1", "served") in calls
    assert db.committed is True
    assert db.closed is True


def test_handle_event_skips_reward_when_duplicate(monkeypatch):
    order = SimpleNamespace(id="order-1", user_id="user-1", total_amount=50000)
    user = SimpleNamespace(id="user-1")
    db = FakeDB({Order: order, User: user})
    calls = []

    monkeypatch.setattr(mq_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(mq_worker, "log_analytics", lambda db, event, payload: calls.append(("analytics", event)))
    monkeypatch.setattr(mq_worker, "notify_order_status", lambda *args, **kwargs: calls.append("notify"))
    monkeypatch.setattr(mq_worker, "reward_on_order_served", lambda db, order: False)

    mq_worker.handle_event(
        "ORDER_STATUS_UPDATED",
        {"order_id": "order-1", "status": "served"},
    )

    assert "notify" in calls
    assert db.committed is False
    assert db.closed is True


def test_handle_event_skips_reward_when_not_served(monkeypatch):
    order = SimpleNamespace(id="order-1", user_id="user-1", total_amount=50000)
    user = SimpleNamespace(id="user-1")
    db = FakeDB({Order: order, User: user})
    calls = []

    monkeypatch.setattr(mq_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(mq_worker, "log_analytics", lambda db, event, payload: calls.append(("analytics", event)))
    monkeypatch.setattr(mq_worker, "notify_order_status", lambda found_user, status: calls.append(("notify", found_user.id, status)))
    monkeypatch.setattr(mq_worker, "reward_on_order_served", lambda *args, **kwargs: calls.append("reward"))

    mq_worker.handle_event(
        "ORDER_STATUS_UPDATED",
        {"order_id": "order-1", "status": "preparing"},
    )

    assert ("notify", "user-1", "preparing") in calls
    assert "reward" not in calls
    assert db.committed is False
    assert db.closed is True


def test_handle_event_skips_notification_when_no_user(monkeypatch):
    order = SimpleNamespace(id="order-1", user_id=None, total_amount=50000)
    db = FakeDB({Order: order})
    calls = []

    monkeypatch.setattr(mq_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(mq_worker, "log_analytics", lambda db, event, payload: calls.append(("analytics", event)))
    monkeypatch.setattr(mq_worker, "notify_order_status", lambda *args, **kwargs: calls.append("notify"))
    monkeypatch.setattr(mq_worker, "reward_on_order_served", lambda *args, **kwargs: calls.append("reward"))

    mq_worker.handle_event(
        "ORDER_STATUS_UPDATED",
        {"order_id": "order-1", "status": "served"},
    )

    assert "notify" not in calls
    assert "reward" not in calls
    assert db.committed is False
    assert db.closed is True


def test_handle_event_returns_when_order_missing(monkeypatch):
    db = FakeDB({Order: None})
    calls = []

    monkeypatch.setattr(mq_worker, "SessionLocal", lambda: db)
    monkeypatch.setattr(mq_worker, "log_analytics", lambda db, event, payload: calls.append(("analytics", event)))
    monkeypatch.setattr(mq_worker, "notify_order_status", lambda *args, **kwargs: calls.append("notify"))

    mq_worker.handle_event(
        "ORDER_STATUS_UPDATED",
        {"order_id": "missing", "status": "served"},
    )

    assert calls == [("analytics", "ORDER_STATUS_UPDATED")]
    assert db.closed is True


class StopWorker(RuntimeError):
    pass


def test_start_worker_acks_on_success(monkeypatch):
    callbacks = []
    events = []

    class Method:
        delivery_tag = "tag-1"

    class Channel:
        def queue_declare(self, **kwargs):
            self.queue_kwargs = kwargs

        def basic_consume(self, queue, on_message_callback):
            callbacks.append((queue, on_message_callback))
            on_message_callback(
                self,
                Method(),
                None,
                json.dumps({"event": "ORDER_STATUS_UPDATED", "payload": {"id": "1"}}).encode(),
            )

        def basic_ack(self, delivery_tag):
            events.append(("ack", delivery_tag))

        def basic_nack(self, delivery_tag, requeue=False):
            events.append(("nack", delivery_tag, requeue))

        def start_consuming(self):
            raise StopWorker()

    class Connection:
        def channel(self):
            return Channel()

    monkeypatch.setattr(mq_worker.pika, "URLParameters", lambda url: url)
    monkeypatch.setattr(mq_worker.pika, "BlockingConnection", lambda params: Connection())
    monkeypatch.setattr(mq_worker, "handle_event", lambda event, payload: events.append((event, payload)))

    with pytest.raises(StopWorker):
        mq_worker.start_worker()

    assert callbacks[0][0] == mq_worker.QUEUE_NAME
    assert ("ORDER_STATUS_UPDATED", {"id": "1"}) in events
    assert ("ack", "tag-1") in events


def test_start_worker_nacks_on_callback_error(monkeypatch):
    events = []

    class Method:
        delivery_tag = "tag-2"

    class Channel:
        def queue_declare(self, **kwargs):
            self.queue_kwargs = kwargs

        def basic_consume(self, queue, on_message_callback):
            on_message_callback(self, Method(), None, b"not-json")

        def basic_ack(self, delivery_tag):
            events.append(("ack", delivery_tag))

        def basic_nack(self, delivery_tag, requeue=False):
            events.append(("nack", delivery_tag, requeue))

        def start_consuming(self):
            raise StopWorker()

    class Connection:
        def channel(self):
            return Channel()

    monkeypatch.setattr(mq_worker.pika, "URLParameters", lambda url: url)
    monkeypatch.setattr(mq_worker.pika, "BlockingConnection", lambda params: Connection())

    with pytest.raises(StopWorker):
        mq_worker.start_worker()

    assert ("nack", "tag-2", False) in events


def test_database_module_uses_sqlite_connect_args(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./tmp-test.db")

    reloaded = importlib.reload(database_module)

    assert reloaded.DATABASE_URL.startswith("sqlite")
    assert reloaded.engine.url.drivername == "sqlite"
