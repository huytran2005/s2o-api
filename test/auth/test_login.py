import uuid

def test_login_success(client):
    email = f"{uuid.uuid4()}@test.com"
    password = "123456"

    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

    res = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )

    assert res.status_code == 200
    assert "access_token" in res.json()
