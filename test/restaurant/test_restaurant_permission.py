def test_customer_cannot_delete_restaurant(
    client, owner_headers, customer_headers
):
    # owner tạo restaurant
    res = client.post(
        "/restaurants",
        headers=owner_headers,
        json={"name": "Delete Test"}
    )
    restaurant_id = res.json()["id"]

    # customer xoá
    res = client.delete(
        f"/restaurants/{restaurant_id}",
        headers=customer_headers
    )

    assert res.status_code == 403
