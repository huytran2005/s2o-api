from utils.security import hash_password, verify_password


def test_hash_password_returns_a_hash():
    hashed = hash_password("123456")

    assert hashed != "123456"
    assert isinstance(hashed, str)


def test_verify_password_accepts_valid_password():
    hashed = hash_password("123456")

    assert verify_password("123456", hashed) is True


def test_verify_password_rejects_invalid_password():
    hashed = hash_password("123456")

    assert verify_password("wrong-password", hashed) is False
