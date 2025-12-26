def test_login_success(client):
    res = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "123"
        }
    )
    assert res.status_code == 200
    assert "access_token" in res.json()
