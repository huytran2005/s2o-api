import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def owner_token(client):
    res = client.post(
        "/auth/login",
        json={
            "email": "owner@gmail.com",
            "password": "123456"
        }
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def customer_token(client):
    res = client.post(
        "/auth/login",
        json={
            "email": "customer@gmail.com",
            "password": "123456"
        }
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def owner_headers(owner_token):
    return {
        "Authorization": f"Bearer {owner_token}"
    }


@pytest.fixture
def customer_headers(customer_token):
    return {
        "Authorization": f"Bearer {customer_token}"
    }
