import pytest
from pydantic import ValidationError

from schemas.auth_schema import LoginRequest, RegisterRequest


def test_register_request_accepts_valid_payload():
    payload = RegisterRequest(
        email="valid@example.com",
        password="123456",
        display_name="Valid User",
        phone="0123456789",
    )

    assert payload.email == "valid@example.com"
    assert payload.display_name == "Valid User"


def test_register_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(email="invalid-email", password="123456")


def test_login_request_accepts_valid_email():
    payload = LoginRequest(email="valid@example.com", password="123456")

    assert payload.email == "valid@example.com"
