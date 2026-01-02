def test_invalid_status_transition(client, staff_token, order_id):
    res = client.patch(
        f"/orders/{order_id}/preparing",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert res.status_code == 400


def test_order_flow(client, staff_token, order_id):
    res = client.patch(
        f"/orders/{order_id}/accept",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert res.status_code == 200

    res = client.patch(
        f"/orders/{order_id}/preparing",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert res.status_code == 200

    res = client.patch(
        f"/orders/{order_id}/served",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    assert res.status_code == 200
