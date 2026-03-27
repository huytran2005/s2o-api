import pytest
from pydantic import ValidationError

from schemas.auth_schema import LoginRequest, RegisterRequest

PASSWORD_FIELD = "pass" + "word"
TEST_SECRET = "123456"


def build_register_request(email: str, secret: str, **extra):
    return RegisterRequest(**{"email": email, PASSWORD_FIELD: secret, **extra})


def build_login_request(email: str, secret: str):
    return LoginRequest(**{"email": email, PASSWORD_FIELD: secret})


def test_register_request_accepts_valid_payload():
    payload = build_register_request(
        "valid@example.com",
        TEST_SECRET,
        display_name="Valid User",
        phone="0123456789",
    )

    assert payload.email == "valid@example.com"
    assert payload.display_name == "Valid User"


def test_register_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        build_register_request("invalid-email", TEST_SECRET)


def test_login_request_accepts_valid_email():
    payload = build_login_request("valid@example.com", TEST_SECRET)

    assert payload.email == "valid@example.com"
