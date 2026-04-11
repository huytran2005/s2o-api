"""
Standard BVA Test: PUT /restaurants/{id}/preview-image
File size [0.1MB - 5MB]

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import io
import pytest


class TestImageUploadSizeStandardBVA:
    """Standard BVA for image file size [0.1MB - 5MB]"""

    def create_file(self, size_bytes):
        """Helper to create file bytes"""
        return b"x" * size_bytes

    def test_upload_image_size_min_100kb(self, client, owner_headers, test_restaurant):
        """BVA: size = min = 100KB (0.1MB)"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201], f"Got {resp.status_code}: {resp.text}"

    def test_upload_image_size_min_plus_200kb(self, client, owner_headers, test_restaurant):
        """BVA: size = min+ = 200KB"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(200 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_size_nom_2_5mb(self, client, owner_headers, test_restaurant):
        """BVA: size = nom = 2.5MB"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(int(2.5 * 1024 * 1024))),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_size_max_minus_4mb(self, client, owner_headers, test_restaurant):
        """BVA: size = max- = 4MB"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(4 * 1024 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_size_max_5mb(self, client, owner_headers, test_restaurant):
        """BVA: size = max = 5MB"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(5 * 1024 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]


class TestImageUploadFormatStandardBVA:
    """Standard BVA for image format validation"""

    def create_file(self, size_bytes):
        """Helper to create file bytes"""
        return b"x" * size_bytes

    def test_upload_image_format_jpg(self, client, owner_headers, test_restaurant):
        """BVA: format = JPEG"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_format_png(self, client, owner_headers, test_restaurant):
        """BVA: format = PNG"""
        files = {
            "image": (
                "test.png",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/png"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_format_jpeg_alt(self, client, owner_headers, test_restaurant):
        """BVA: format = JPEG alternative"""
        files = {
            "image": (
                "test.jpeg",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_format_gif(self, client, owner_headers, test_restaurant):
        """BVA: format = GIF (if supported)"""
        files = {
            "image": (
                "test.gif",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/gif"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        # GIF might not be supported, but we're testing all formats
        assert resp.status_code in [200, 201, 400, 422]

    def test_upload_image_format_webp(self, client, owner_headers, test_restaurant):
        """BVA: format = WebP (if supported)"""
        files = {
            "image": (
                "test.webp",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/webp"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201, 400, 422]


class TestImageUploadCombinedStandardBVA:
    """Standard BVA for size and format combined"""

    def create_file(self, size_bytes):
        """Helper to create file bytes"""
        return b"x" * size_bytes

    def test_upload_image_min_size_jpg(self, client, owner_headers, test_restaurant):
        """BVA: min size, JPEG format"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_nom_size_png(self, client, owner_headers, test_restaurant):
        """BVA: nom size, PNG format"""
        files = {
            "image": (
                "test.png",
                io.BytesIO(self.create_file(int(2.5 * 1024 * 1024))),
                "image/png"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_max_size_jpg(self, client, owner_headers, test_restaurant):
        """BVA: max size, JPEG format"""
        files = {
            "image": (
                "test.jpg",
                io.BytesIO(self.create_file(5 * 1024 * 1024)),
                "image/jpeg"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_mixed_min_size_png(self, client, owner_headers, test_restaurant):
        """BVA: min size, PNG format"""
        files = {
            "image": (
                "test.png",
                io.BytesIO(self.create_file(100 * 1024)),
                "image/png"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_upload_image_mixed_max_size_png(self, client, owner_headers, test_restaurant):
        """BVA: max size, PNG format"""
        files = {
            "image": (
                "test.png",
                io.BytesIO(self.create_file(5 * 1024 * 1024)),
                "image/png"
            )
        }
        resp = client.put(
            f"/restaurants/{test_restaurant.id}/preview-image",
            files=files,
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]
