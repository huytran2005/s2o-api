import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"
# hoặc http://127.0.0.1:8000

def test_register_api():
    email = f"{uuid.uuid4()}@test.com"

    res = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": "123456"
        }
    )

    assert res.status_code in (200, 201)


def test_login_api():
    email = f"{uuid.uuid4()}@test.com"
    password = "123456"

    requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": password}
    )

    res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )

    assert res.status_code == 200
    assert "access_token" in res.json()
