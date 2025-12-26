import io
import os

def test_update_preview_image(client, owner_headers):
    # 1️⃣ tạo restaurant
    res = client.post(
        "/restaurants",
        headers=owner_headers,
        json={"name": "Preview Test"}
    )
    assert res.status_code == 201
    restaurant_id = res.json()["id"]

    # 2️⃣ upload preview lần 1 (fake image)
    image_1 = io.BytesIO(b"fake image content 1")
    image_1.name = "test1.png"

    res = client.put(
        f"/restaurants/{restaurant_id}/preview-image",
        headers=owner_headers,
        files={"image": ("test1.png", image_1, "image/png")}
    )

    assert res.status_code == 200
    path_1 = res.json()["image_preview"]
    assert os.path.exists(path_1)

    # 3️⃣ upload preview lần 2 (replace)
    image_2 = io.BytesIO(b"fake image content 2")
    image_2.name = "test2.png"

    res = client.put(
        f"/restaurants/{restaurant_id}/preview-image",
        headers=owner_headers,
        files={"image": ("test2.png", image_2, "image/png")}
    )

    assert res.status_code == 200
    path_2 = res.json()["image_preview"]

    # 4️⃣ kiểm tra ảnh cũ bị xoá
    assert path_1 != path_2
    assert not os.path.exists(path_1)
    assert os.path.exists(path_2)
