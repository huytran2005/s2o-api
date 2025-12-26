def test_owner_list_restaurants(client, owner_headers):
    res = client.get(
        "/restaurants",
        headers=owner_headers
    )

    assert res.status_code == 200
    assert isinstance(res.json(), list)
