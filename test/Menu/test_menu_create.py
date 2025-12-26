def test_create_menu(client, owner_headers):
    response = client.post(
        "/menus?restaurant_id=00000000-0000-0000-0000-000000000001",
        headers=owner_headers,
        json={
            "name": "Cơm gà",
            "price": 45000,
            "category_id": "00000000-0000-0000-0000-000000000002"
        }
    )

    assert response.status_code in (200, 201)
