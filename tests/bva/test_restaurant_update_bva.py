"""
Standard BVA Test: PUT /restaurants/{id}
Name [3-50], Description [10-200]

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import pytest
from uuid import uuid4


class TestRestaurantUpdateNameStandardBVA:
    """Standard BVA for restaurant name update [3-50]"""

    fake_id = str(uuid4())

    def test_update_restaurant_name_min_3(self, client, owner_headers):
        """BVA: name = min = 3 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"name": "Res"},  # 3 chars
            headers=owner_headers
        )
        # 404 OK (not found), 422 is validation error
        assert resp.status_code != 422

    def test_update_restaurant_name_min_plus_4(self, client, owner_headers):
        """BVA: name = min+ = 4 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"name": "Rest"},  # 4 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_name_nom_26(self, client, owner_headers):
        """BVA: name = nom = 26 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"name": "N" * 26},  # 26 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_name_max_minus_49(self, client, owner_headers):
        """BVA: name = max- = 49 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"name": "N" * 49},  # 49 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_name_max_50(self, client, owner_headers):
        """BVA: name = max = 50 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"name": "N" * 50},  # 50 chars
            headers=owner_headers
        )
        assert resp.status_code != 422


class TestRestaurantUpdateDescStandardBVA:
    """Standard BVA for restaurant description update [10-200]"""

    fake_id = str(uuid4())

    def test_update_restaurant_desc_min_10(self, client, owner_headers):
        """BVA: description = min = 10 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"description": "D" * 10},  # 10 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_desc_min_plus_11(self, client, owner_headers):
        """BVA: description = min+ = 11 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"description": "D" * 11},  # 11 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_desc_nom_105(self, client, owner_headers):
        """BVA: description = nom = 105 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"description": "D" * 105},  # 105 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_desc_max_minus_199(self, client, owner_headers):
        """BVA: description = max- = 199 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"description": "D" * 199},  # 199 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_desc_max_200(self, client, owner_headers):
        """BVA: description = max = 200 chars"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"description": "D" * 200},  # 200 chars
            headers=owner_headers
        )
        assert resp.status_code != 422


class TestRestaurantUpdateBothStandardBVA:
    """Standard BVA for both fields together"""

    fake_id = str(uuid4())

    def test_update_restaurant_both_min(self, client, owner_headers):
        """BVA: both = min"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={
                "name": "Res",  # 3
                "description": "D" * 10  # 10
            },
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_both_nom(self, client, owner_headers):
        """BVA: both = nom"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={
                "name": "N" * 26,  # 26
                "description": "D" * 105  # 105
            },
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_both_max(self, client, owner_headers):
        """BVA: both = max"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={
                "name": "N" * 50,  # 50
                "description": "D" * 200  # 200
            },
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_name_only_min(self, client, owner_headers):
        """BVA: only name, min"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"name": "Res"},
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_restaurant_desc_only_max(self, client, owner_headers):
        """BVA: only description, max"""
        resp = client.put(
            f"/restaurants/{self.fake_id}",
            json={"description": "D" * 200},
            headers=owner_headers
        )
        assert resp.status_code != 422
