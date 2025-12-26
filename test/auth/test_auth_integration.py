import uuid

def test_register_user(client):
    email = f"{uuid.uuid4()}@test.com"

    res = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "123456"
        }
    )

    assert res.status_code in (200, 201)
