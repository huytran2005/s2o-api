def test_create_category(client, owner_headers):
    response = client.post(
        "/categories?restaurant_id=11111111-1111-1111-1111-111111111111",
        headers=owner_headers,
        json={
            "name": "Món chính",
            "icon": "🍜"
        }
    )

    assert response.status_code in (200, 201)
