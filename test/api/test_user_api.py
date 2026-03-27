import os
import requests
import uuid

TEST_API_SCHEME = os.getenv("TEST_API_SCHEME", "http")
TEST_API_HOST = os.getenv("TEST_API_HOST", "127.0.0.1")
TEST_API_PORT = os.getenv("TEST_API_PORT", "8000")
BASE_URL = f"{TEST_API_SCHEME}://{TEST_API_HOST}:{TEST_API_PORT}"

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
