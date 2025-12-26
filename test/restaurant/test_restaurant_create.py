def test_owner_create_restaurant(client, owner_headers):
    res = client.post(
        "/restaurants",
        headers=owner_headers,
        json={
            "name": "Test Restaurant",
            "description": "pytest"
        }
    )

    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Test Restaurant"
    assert data["image_preview"] is None


def test_customer_cannot_create_restaurant(client, customer_headers):
    res = client.post(
        "/restaurants",
        headers=customer_headers,
        json={"name": "Forbidden"}
    )

    assert res.status_code == 403
