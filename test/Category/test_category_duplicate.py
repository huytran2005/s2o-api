def test_duplicate_category(client, owner_headers):
    client.post(
        "/categories?restaurant_id=00000000-0000-0000-0000-000000000001",
        headers=owner_headers,
        json={
            "name": "Món chính",
            "icon": "🍜"
        }
    )

    response = client.post(
        "/categories?restaurant_id=00000000-0000-0000-0000-000000000001",
        headers=owner_headers,   # 👈 QUAN TRỌNG
        json={
            "name": "Món chính",
            "icon": "🍜"
        }
    )

    assert response.status_code == 400
