import utils.jwt as jwt_module
from utils.jwt import create_access_token, decode_token


def test_create_access_token_round_trip():
    token = create_access_token({"user_id": "user-1", "role": "owner"})
    payload = decode_token(token)

    assert payload is not None
    assert payload["user_id"] == "user-1"
    assert payload["role"] == "owner"
    assert "exp" in payload


def test_decode_token_returns_none_for_invalid_token():
    assert decode_token("not-a-token") is None


def test_verify_token_returns_none_without_user_id(monkeypatch):
    monkeypatch.setattr(jwt_module, "decode_token", lambda token: {"role": "owner"})

    assert jwt_module.verify_token("token-without-user-id") is None
