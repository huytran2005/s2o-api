def test_full_restaurant_flow(client, owner_headers):
    # CREATE
    res = client.post(
        "/restaurants",
        headers=owner_headers,
        json={"name": "API Restaurant"}
    )
    assert res.status_code == 201
    restaurant_id = res.json()["id"]

    # UPDATE
    res = client.put(
        f"/restaurants/{restaurant_id}",
        headers=owner_headers,
        json={"description": "Updated via API test"}
    )
    assert res.status_code == 200

    # LIST
    res = client.get(
        "/restaurants",
        headers=owner_headers
    )
    assert res.status_code == 200

    # ❌ OWNER KHÔNG ĐƯỢC XOÁ
    res = client.delete(
        f"/restaurants/{restaurant_id}",
        headers=owner_headers
    )
    assert res.status_code == 403
