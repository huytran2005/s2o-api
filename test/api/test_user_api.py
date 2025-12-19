import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def register_and_login():
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

    return res.json()["access_token"], email


def test_get_current_user():
    token, email = register_and_login()

    res = requests.get(
        f"{BASE_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 200
    assert res.json()["email"] == email
