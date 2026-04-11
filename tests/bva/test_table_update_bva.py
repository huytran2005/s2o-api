"""
Standard BVA Test: PUT /tables/{id}
Name [2-10], Capacity [1-20]

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import pytest


class TestTableUpdateNameStandardBVA:
    """Standard BVA for table name update [2-10]"""

    def test_update_table_name_min_2(self, client, owner_headers, test_table):
        """BVA: name = min = 2 chars"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"name": "T1"},  # 2 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_name_min_plus_3(self, client, owner_headers, test_table):
        """BVA: name = min+ = 3 chars"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"name": "TAB"},  # 3 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_name_nom_6(self, client, owner_headers, test_table):
        """BVA: name = nom = 6 chars"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"name": "N" * 6},  # 6 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_name_max_minus_9(self, client, owner_headers, test_table):
        """BVA: name = max- = 9 chars"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"name": "N" * 9},  # 9 chars
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_name_max_10(self, client, owner_headers, test_table):
        """BVA: name = max = 10 chars"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"name": "N" * 10},  # 10 chars
            headers=owner_headers
        )
        assert resp.status_code != 422


class TestTableUpdateCapacityStandardBVA:
    """Standard BVA for capacity update [1-20]"""

    def test_update_table_seats_min_1(self, client, owner_headers, test_table):
        """BVA: seats = min = 1"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"seats": 1},
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_seats_min_plus_2(self, client, owner_headers, test_table):
        """BVA: seats = min+ = 2"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"seats": 2},
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_seats_nom_10(self, client, owner_headers, test_table):
        """BVA: seats = nom = 10"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"seats": 10},
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_seats_max_minus_19(self, client, owner_headers, test_table):
        """BVA: seats = max- = 19"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"seats": 19},
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_seats_max_20(self, client, owner_headers, test_table):
        """BVA: seats = max = 20"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"seats": 20},
            headers=owner_headers
        )
        assert resp.status_code != 422


class TestTableUpdateBothStandardBVA:
    """Standard BVA for both name and capacity"""

    def test_update_table_both_min(self, client, owner_headers, test_table):
        """BVA: both = min"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={
                "name": "T1",  # 2
                "seats": 1
            },
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_both_nom(self, client, owner_headers, test_table):
        """BVA: both = nom"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={
                "name": "N" * 6,  # 6
                "seats": 10
            },
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_both_max(self, client, owner_headers, test_table):
        """BVA: both = max"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={
                "name": "N" * 10,  # 10
                "seats": 20
            },
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_name_only_min(self, client, owner_headers, test_table):
        """BVA: name only, min"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"name": "T1"},
            headers=owner_headers
        )
        assert resp.status_code != 422

    def test_update_table_seats_only_max(self, client, owner_headers, test_table):
        """BVA: seats only, max"""
        resp = client.put(
            f"/tables/{test_table.id}",
            json={"seats": 20},
            headers=owner_headers
        )
        assert resp.status_code != 422
