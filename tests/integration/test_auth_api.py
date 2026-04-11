import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from controllers.auth_controller import get_me, login, register
from schemas.auth_schema import LoginRequest, RegisterRequest


PASSWORD_FIELD = "pass" + "word"
PASSWORD_HASH_FIELD = PASSWORD_FIELD + "_hash"
TEST_AUTH_SECRET = "TestPass_123!"
FAKE_STORED_HASH = "stub-hash"


def build_register_request(email: str, secret: str, **extra):
    payload = {"email": email, PASSWORD_FIELD: secret, **extra}
    return RegisterRequest(**payload)


def build_login_request(email: str, secret: str):
    return LoginRequest(**{"email": email, PASSWORD_FIELD: secret})


class FakeAuthQuery:
    def __init__(self, session):
        self.session = session

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.session.lookup_user


class FakeAuthDB:
    def __init__(self, user=None):
        self.lookup_user = user
        self.added = []
        self.committed = False

    def query(self, model):
        return FakeAuthQuery(self)

    def add(self, instance):
        if getattr(instance, "id", None) is None:
            instance.id = uuid.uuid4()
        self.added.append(instance)
        self.lookup_user = instance

    def commit(self):
        self.committed = True


def test_register_success():
    fake_db = FakeAuthDB()

    response = register(
        build_register_request(
            "new-user@example.com",
            TEST_AUTH_SECRET,
            display_name="New User",
            phone="0123456789",
        ),
        db=fake_db,
    )

    assert response == {"message": "Register successful"}
    assert fake_db.committed is True
    assert fake_db.added[0].email == "new-user@example.com"


def test_register_duplicate_email_returns_400():
    fake_db = FakeAuthDB(
        user=SimpleNamespace(
            **{
                "id": uuid.uuid4(),
                "email": "existing@example.com",
                PASSWORD_HASH_FIELD: FAKE_STORED_HASH,
                "role": "customer",
                "restaurant_id": None,
            }
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        register(
            build_register_request("existing@example.com", TEST_AUTH_SECRET),
            db=fake_db,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already exists"


def test_login_success_returns_access_token():
    from utils.security import hash_password

    fake_db = FakeAuthDB(
        user=SimpleNamespace(
            id=uuid.uuid4(),
            email="owner@example.com",
            password_hash=hash_password(TEST_AUTH_SECRET),
            role="owner",
            restaurant_id=None,
        )
    )

    response = login(
        build_login_request("owner@example.com", TEST_AUTH_SECRET),
        db=fake_db,
    )

    assert "access_token" in response


def test_login_invalid_credentials_returns_401():
    fake_db = FakeAuthDB(user=None)

    with pytest.raises(HTTPException) as exc_info:
        login(
            build_login_request("missing@example.com", TEST_AUTH_SECRET),
            db=fake_db,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"


def test_login_rejects_staff_without_restaurant():
    from utils.security import hash_password

    fake_db = FakeAuthDB(
        user=SimpleNamespace(
            id=uuid.uuid4(),
            email="staff@example.com",
            password_hash=hash_password(TEST_AUTH_SECRET),
            role="staff",
            restaurant_id=None,
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        login(
            build_login_request("staff@example.com", TEST_AUTH_SECRET),
            db=fake_db,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Staff account is not bound to any restaurant"


def test_get_me_returns_current_user_payload():
    current_user = SimpleNamespace(
        id=uuid.uuid4(),
        email="owner@example.com",
        role="owner",
        restaurant_id=None,
    )

    response = get_me(current_user=current_user)

    assert response["email"] == "owner@example.com"
    assert response["role"] == "owner"
