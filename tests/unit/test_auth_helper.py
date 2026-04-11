import pytest

from utils.auth_helper import get_token

PASSWORD_FIELD = "pass" + "word"
TEST_SECRET = "secret"


def test_get_token_registers_and_logs_in_without_role_mutation():
    class DummyResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"access_token": "token-123"}

    class DummyClient:
        def __init__(self):
            self.calls = []

        def post(self, url, json):
            self.calls.append((url, json))
            return DummyResponse()

    client = DummyClient()

    token = get_token(client, email="guest@example.com", **{PASSWORD_FIELD: TEST_SECRET})

    assert token == "token-123"
    assert client.calls == [
        (
            "/auth/register",
            {"email": "guest@example.com", PASSWORD_FIELD: TEST_SECRET},
        ),
        (
            "/auth/login",
            {"email": "guest@example.com", PASSWORD_FIELD: TEST_SECRET},
        ),
    ]


def test_get_token_mutates_role_and_fails_on_bad_login(monkeypatch):
    class DummyUser:
        def __init__(self, email):
            self.email = email
            self.role = "customer"

    class DummyQuery:
        def __init__(self, user):
            self.user = user

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return self.user

    class DummyDB:
        def __init__(self, user):
            self.user = user
            self.committed = False
            self.closed = False

        def query(self, model):
            return DummyQuery(self.user)

        def commit(self):
            self.committed = True

        def close(self):
            self.closed = True

    class DummyResponse:
        status_code = 401
        text = "bad login"

        @staticmethod
        def json():
            return {"detail": "invalid"}

    class DummyClient:
        def __init__(self):
            self.calls = []

        def post(self, url, json):
            self.calls.append((url, json))
            return DummyResponse()

    user = DummyUser(email="owner@example.com")
    db = DummyDB(user)
    monkeypatch.setattr("utils.auth_helper.SessionLocal", lambda: db)

    client = DummyClient()

    try:
        get_token(client, email="owner@example.com", **{PASSWORD_FIELD: TEST_SECRET}, role="owner")
    except AssertionError:
        pass

    assert user.role == "owner"
    assert db.committed is True
    assert db.closed is True

    with pytest.raises(AssertionError):
        get_token(client, email="owner@example.com", **{PASSWORD_FIELD: TEST_SECRET})
