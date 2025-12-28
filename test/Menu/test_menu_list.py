def test_list_menu(client, owner_headers):
    response = client.get(
        "/menus?restaurant_id=00000000-0000-0000-0000-000000000001",
        headers=owner_headers
    )

    assert response.status_code == 200
