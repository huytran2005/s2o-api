import io
import os

def test_preview_image_replace_flow(client, owner_headers):
    # CREATE
    res = client.post(
        "/restaurants",
        headers=owner_headers,
        json={"name": "Preview API"}
    )
    restaurant_id = res.json()["id"]

    # UPLOAD 1
    img1 = io.BytesIO(b"image-1")
    img1.name = "img1.png"

    res = client.put(
        f"/restaurants/{restaurant_id}/preview-image",
        headers=owner_headers,
        files={"image": ("img1.png", img1, "image/png")}
    )
    assert res.status_code == 200
    path1 = res.json()["image_preview"]
    assert os.path.exists(path1)

    # UPLOAD 2 (replace)
    img2 = io.BytesIO(b"image-2")
    img2.name = "img2.png"

    res = client.put(
        f"/restaurants/{restaurant_id}/preview-image",
        headers=owner_headers,
        files={"image": ("img2.png", img2, "image/png")}
    )
    assert res.status_code == 200
    path2 = res.json()["image_preview"]

    assert path1 != path2
    assert not os.path.exists(path1)
    assert os.path.exists(path2)
