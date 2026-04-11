"""
Standard BVA Test: POST /restaurants/
Name [3-50], Description [10-200]

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import pytest


class TestRestaurantCreateNameStandardBVA:
    """Standard BVA for restaurant name [3-50]"""

    def test_create_restaurant_name_min_3(self, client, owner_headers):
        """BVA: name = min = 3 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Res",  # 3 chars
                "description": "Valid description for restaurant"
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201], f"Got {resp.status_code}: {resp.text}"

    def test_create_restaurant_name_min_plus_4(self, client, owner_headers):
        """BVA: name = min+ = 4 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Rest",  # 4 chars
                "description": "Valid description for restaurant"
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_name_nom_26(self, client, owner_headers):
        """BVA: name = nom = 26 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "N" * 26,  # 26 chars
                "description": "Valid description for restaurant"
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_name_max_minus_49(self, client, owner_headers):
        """BVA: name = max- = 49 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "N" * 49,  # 49 chars
                "description": "Valid description for restaurant"
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_name_max_50(self, client, owner_headers):
        """BVA: name = max = 50 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "N" * 50,  # 50 chars
                "description": "Valid description for restaurant"
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]


class TestRestaurantCreateDescStandardBVA:
    """Standard BVA for restaurant description [10-200]"""

    def test_create_restaurant_desc_min_10(self, client, owner_headers):
        """BVA: description = min = 10 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Restaurant",
                "description": "D" * 10  # 10 chars
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_desc_min_plus_11(self, client, owner_headers):
        """BVA: description = min+ = 11 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Restaurant",
                "description": "D" * 11  # 11 chars
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_desc_nom_105(self, client, owner_headers):
        """BVA: description = nom = 105 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Restaurant",
                "description": "D" * 105  # 105 chars
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_desc_max_minus_199(self, client, owner_headers):
        """BVA: description = max- = 199 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Restaurant",
                "description": "D" * 199  # 199 chars
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_desc_max_200(self, client, owner_headers):
        """BVA: description = max = 200 chars"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Restaurant",
                "description": "D" * 200  # 200 chars
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]


class TestRestaurantCreateBothFieldsStandardBVA:
    """Standard BVA for both name and description together"""

    def test_create_restaurant_both_min(self, client, owner_headers):
        """BVA: both at min"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Res",  # min 3
                "description": "D" * 10  # min 10
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_both_nom(self, client, owner_headers):
        """BVA: both at nom"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "N" * 26,  # nom 26
                "description": "D" * 105  # nom 105
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_both_max(self, client, owner_headers):
        """BVA: both at max"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "N" * 50,  # max 50
                "description": "D" * 200  # max 200
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_mixed_boundaries(self, client, owner_headers):
        """BVA: mixed boundaries (name min, desc max)"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "Res",  # min
                "description": "D" * 200  # max
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_restaurant_mixed_boundaries_2(self, client, owner_headers):
        """BVA: mixed boundaries (name max, desc min)"""
        resp = client.post(
            "/restaurants/",
            json={
                "name": "N" * 50,  # max
                "description": "D" * 10  # min
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]
