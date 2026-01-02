import pytest


@pytest.fixture
def customer_session(client):
    """
    Giả lập khách quét QR → lấy session_token
    """
    res = client.post(
        "/guest/scan",
        params={"code": "d8ac01f4-101e-4c38-bea8-459603ae9adf"}
    )

    assert res.status_code == 200
    return res.json()["session_token"]


@pytest.fixture
def staff_token(client):
    res = client.post("/auth/login", json={
        "email": "staff@gmail.com",
        "password": "123456"
    })

    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture
def order_id(client, customer_session):
    res = client.post("/orders", json={
        "session_token": customer_session,
        "items": [
            {
                "menu_item_id": "2052af57-7ac6-4dd8-ab63-dd8d961a1b84",
                "qty": 1
            }
        ]
    })

    assert res.status_code == 200
    return res.json()["id"]
