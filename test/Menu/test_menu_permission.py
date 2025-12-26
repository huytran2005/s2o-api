def test_customer_cannot_create_menu(client, customer_headers):
    response = client.post(
        "/menus?restaurant_id=015f0bcf-e1e0-437e-94db-b20b4b576a57",
        headers=customer_headers,
        json={
            "name": "Hack thử",
            "price": 1000,
            "category_id": "2aab07d3-910f-43a8-8f3e-950e28f10dab"
        }
    )

    assert response.status_code == 403
