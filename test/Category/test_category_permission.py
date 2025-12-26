def test_customer_cannot_create_category(client, customer_headers):
    response = client.post(
        "/categories?restaurant_id=00000000-0000-0000-0000-000000000001",
        headers=customer_headers,
        json={
            "name": "Hack thử",
            "icon": "😈"
        }
    )

    assert response.status_code == 403
