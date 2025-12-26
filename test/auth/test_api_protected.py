def test_protected_endpoint(client):
    email = "protected@test.com"
    password = "123456"

    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )

    token = login.json()["access_token"]

    res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200
