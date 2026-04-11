"""
Standard BVA Test: POST /tables/
Name [2-10], Capacity [1-20]

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import pytest


class TestTableCreateNameStandardBVA:
    """Standard BVA for table name [2-10]"""

    def test_create_table_name_min_2(self, client, owner_headers, test_restaurant):
        """BVA: name = min = 2 chars"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "T1",  # 2 chars
                "seats": 4
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201], f"Got {resp.status_code}: {resp.text}"

    def test_create_table_name_min_plus_3(self, client, owner_headers, test_restaurant):
        """BVA: name = min+ = 3 chars"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "TAB",  # 3 chars
                "seats": 4
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_name_nom_6(self, client, owner_headers, test_restaurant):
        """BVA: name = nom = 6 chars"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "N" * 6,  # 6 chars
                "seats": 4
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_name_max_minus_9(self, client, owner_headers, test_restaurant):
        """BVA: name = max- = 9 chars"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "N" * 9,  # 9 chars
                "seats": 4
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_name_max_10(self, client, owner_headers, test_restaurant):
        """BVA: name = max = 10 chars"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "N" * 10,  # 10 chars
                "seats": 4
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]


class TestTableCreateCapacityStandardBVA:
    """Standard BVA for capacity [1-20]"""

    def test_create_table_seats_min_1(self, client, owner_headers, test_restaurant):
        """BVA: seats = min = 1"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "Table1",
                "seats": 1
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_seats_min_plus_2(self, client, owner_headers, test_restaurant):
        """BVA: seats = min+ = 2"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "Table2",
                "seats": 2
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_seats_nom_10(self, client, owner_headers, test_restaurant):
        """BVA: seats = nom = 10"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "Table3",
                "seats": 10
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_seats_max_minus_19(self, client, owner_headers, test_restaurant):
        """BVA: seats = max- = 19"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "Table4",
                "seats": 19
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_seats_max_20(self, client, owner_headers, test_restaurant):
        """BVA: seats = max = 20"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "Table5",
                "seats": 20
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]


class TestTableCreateBothStandardBVA:
    """Standard BVA for both name and capacity"""

    def test_create_table_both_min(self, client, owner_headers, test_restaurant):
        """BVA: both = min"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "T1",  # 2
                "seats": 1
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_both_nom(self, client, owner_headers, test_restaurant):
        """BVA: both = nom"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "N" * 6,  # 6
                "seats": 10
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_both_max(self, client, owner_headers, test_restaurant):
        """BVA: both = max"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "N" * 10,  # 10
                "seats": 20
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_mixed_name_min_seats_max(self, client, owner_headers, test_restaurant):
        """BVA: name min, seats max"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "T1",
                "seats": 20
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]

    def test_create_table_mixed_name_max_seats_min(self, client, owner_headers, test_restaurant):
        """BVA: name max, seats min"""
        resp = client.post(
            "/tables/",
            json={
                "restaurant_id": str(test_restaurant.id),
                "name": "N" * 10,
                "seats": 1
            },
            headers=owner_headers
        )
        assert resp.status_code in [200, 201]
