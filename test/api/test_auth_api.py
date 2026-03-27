import os
import requests
import uuid

TEST_API_SCHEME = os.getenv("TEST_API_SCHEME", "http")
TEST_API_HOST = os.getenv("TEST_API_HOST", "127.0.0.1")
TEST_API_PORT = os.getenv("TEST_API_PORT", "8000")
BASE_URL = f"{TEST_API_SCHEME}://{TEST_API_HOST}:{TEST_API_PORT}"

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
