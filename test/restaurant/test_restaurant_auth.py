def test_create_restaurant_without_login(client):
    res = client.post(
        "/restaurants",
        json={"name": "No Auth"}
    )
    assert res.status_code == 401
