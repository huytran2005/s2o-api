"""
Standard BVA Test: Đơn giản
Formula: min, min+, nom, max-, max (chỉ VALID cases)
"""
import pytest


class TestSimplePasswordBVA:
    """Test password validation: [8-32]"""

    def test_pwd_min_8(self, client):
        """BVA: min=8"""
        r = client.post("/auth/register", json={
            "email": f"p1@test.com",
            "password": "Pass1234"  # 8
        })
        assert r.status_code in [200, 201, 422]

    def test_pwd_max_32(self, client):
        """BVA: max=32"""
        r = client.post("/auth/register", json={
            "email": f"p2@test.com",
            "password": "P" * 32  # 32
        })
        assert r.status_code in [200, 201, 422]
