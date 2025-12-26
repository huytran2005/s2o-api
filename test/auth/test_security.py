from utils.security import hash_password, verify_password


def test_hash_password_returns_hashed_value():
    password = "123456"

    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_success():
    password = "123456"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_fail_with_wrong_password():
    password = "123456"
    hashed = hash_password(password)

    assert verify_password("wrong-password", hashed) is False
