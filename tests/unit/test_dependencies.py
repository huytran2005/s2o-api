from datetime import datetime, timedelta
import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import utils.dependencies as dependencies


def test_get_current_user_optional_returns_none_without_header():
    request = SimpleNamespace(headers={})

    assert dependencies.get_current_user_optional(request) is None


def test_get_current_user_optional_decodes_bearer_token(monkeypatch):
    request = SimpleNamespace(headers={"Authorization": "Bearer token-123"})
    monkeypatch.setattr(dependencies, "verify_token", lambda token: {"token": token})

    payload = dependencies.get_current_user_optional(request)

    assert payload == {"token": "token-123"}


def test_get_current_user_returns_user(monkeypatch):
    expected_user = SimpleNamespace(id=uuid.uuid4(), role="owner")

    class DummyQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return expected_user

    class DummyDB:
        def query(self, model):
            return DummyQuery()

    monkeypatch.setattr(
        dependencies,
        "decode_token",
        lambda token: {"user_id": str(expected_user.id)},
    )

    result = dependencies.get_current_user(token="valid-token", db=DummyDB())

    assert result is expected_user


def test_get_current_user_rejects_invalid_payload(monkeypatch):
    monkeypatch.setattr(dependencies, "decode_token", lambda token: None)

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token="invalid-token", db=object())

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_missing_payload_or_user(monkeypatch):
    class DummyQuery:
        def __init__(self, user=None):
            self.user = user

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return self.user

    class DummyDB:
        def __init__(self, user=None):
            self.user = user

        def query(self, model):
            return DummyQuery(self.user)

    monkeypatch.setattr(dependencies, "decode_token", lambda token: {})
    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token="missing-user-id", db=DummyDB())
    assert exc_info.value.status_code == 401

    monkeypatch.setattr(dependencies, "decode_token", lambda token: {"user_id": "u-1"})
    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token="no-user", db=DummyDB(user=None))
    assert exc_info.value.status_code == 401


def test_get_guest_session_and_mobile_validate_tokens(monkeypatch):
    session = SimpleNamespace(session_token="guest-token", expires_at=datetime.utcnow() + timedelta(hours=1))

    class DummyQuery:
        def __init__(self, result):
            self.result = result

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return self.result

    class DummyDB:
        def __init__(self, result):
            self.result = result

        def query(self, model):
            return DummyQuery(self.result)

    assert dependencies.get_guest_session(guest_session="guest-token", db=DummyDB(session)) is session

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_guest_session(guest_session=None, db=DummyDB(session))
    assert exc_info.value.status_code == 401

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_guest_session(guest_session="bad", db=DummyDB(None))
    assert exc_info.value.status_code == 401

    assert dependencies.get_guest_session_mobile(
        authorization="Bearer guest-token",
        db=DummyDB(session),
    ) is session

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_guest_session_mobile(authorization="guest-token", db=DummyDB(session))
    assert exc_info.value.status_code == 401

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_guest_session_mobile(authorization="Bearer bad", db=DummyDB(None))
    assert exc_info.value.status_code == 401
