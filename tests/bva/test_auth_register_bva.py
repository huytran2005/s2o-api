"""
Standard BVA Test: POST /auth/register
Password [8-32], Display Name [1-50], Phone [10-11]

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import pytest


class TestRegisterPasswordStandardBVA:
    """Standard BVA for password length [8-32]"""

    def test_register_password_min_8_chars(self, client):
        """BVA: password = min = 8 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_pwd_min_8_{id(self)}@test.com",
                "password": "Pass1234",  # exactly 8
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"

    def test_register_password_min_plus_9_chars(self, client):
        """BVA: password = min+ = 9 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_pwd_min9_{id(self)}@test.com",
                "password": "Pass12345",  # 9 chars
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_password_nom_20_chars(self, client):
        """BVA: password = nom (average) = 20 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_pwd_nom_{id(self)}@test.com",
                "password": "Pass" + "x" * 16,  # 20 chars
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_password_max_minus_31_chars(self, client):
        """BVA: password = max- = 31 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_pwd_max_minus_{id(self)}@test.com",
                "password": "Pass" + "x" * 27,  # 31 chars
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_password_max_32_chars(self, client):
        """BVA: password = max = 32 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_pwd_max_{id(self)}@test.com",
                "password": "Pass" + "x" * 28,  # 32 chars
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]


class TestRegisterDisplayNameStandardBVA:
    """Standard BVA for display_name length [1-50]"""

    def test_register_name_min_1_char(self, client):
        """BVA: display_name = min = 1 char"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_name_min_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "A"  # 1 char
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_name_min_plus_2_chars(self, client):
        """BVA: display_name = min+ = 2 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_name_min_plus_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "AB"  # 2 chars
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_name_nom_25_chars(self, client):
        """BVA: display_name = nom = 25 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_name_nom_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "A" * 25  # 25 chars
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_name_max_minus_49_chars(self, client):
        """BVA: display_name = max- = 49 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_name_max_minus_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "A" * 49  # 49 chars
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_name_max_50_chars(self, client):
        """BVA: display_name = max = 50 chars"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_name_max_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "A" * 50  # 50 chars
            }
        )
        assert resp.status_code in [200, 201]


class TestRegisterPhoneStandardBVA:
    """Standard BVA for phone length [10-11]"""

    def test_register_phone_min_10_digits(self, client):
        """BVA: phone = min = 10 digits"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_phone_min_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "User",
                "phone": "0123456789"  # 10 digits
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_phone_min_plus_10_alt(self, client):
        """BVA: phone = min+ (close to min) = 10 digits alt"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_phone_min_plus_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "User",
                "phone": "9876543210"  # 10 digits
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_phone_nom_10_or_11(self, client):
        """BVA: phone = nom (11 digits - common for international)"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_phone_nom_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "User",
                "phone": "84912345678"  # 11 digits
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_phone_max_minus_11(self, client):
        """BVA: phone = max- (close to max) = 11 digits"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_phone_max_minus_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "User",
                "phone": "11111111111"  # 11 digits
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_phone_max_11_digits(self, client):
        """BVA: phone = max = 11 digits"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"test_phone_max_{id(self)}@test.com",
                "password": "ValidPass123",
                "display_name": "User",
                "phone": "22222222222"  # 11 digits
            }
        )
        assert resp.status_code in [200, 201]


class TestRegisterEmailStandardBVA:
    """Standard BVA for email format - VALID emails only"""

    def test_register_email_short_but_valid(self, client):
        """BVA: email min (short but valid)"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"a@b.co",  # minimal valid email
                "password": "ValidPass123",
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_email_simple_valid(self, client):
        """BVA: email simple valid"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"user@test.com",
                "password": "ValidPass123",
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_email_with_numbers(self, client):
        """BVA: email nom (with numbers)"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"user123@example456.com",
                "password": "ValidPass123",
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_email_with_dots(self, client):
        """BVA: email max- (with dots and numbers)"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"first.last.123@sub.example.com",
                "password": "ValidPass123",
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]

    def test_register_email_long_valid(self, client):
        """BVA: email max (longer valid)"""
        resp = client.post(
            "/auth/register",
            json={
                "email": f"very.long.email.address.with.many.dots@very.long.domain.name.com",
                "password": "ValidPass123",
                "display_name": "User"
            }
        )
        assert resp.status_code in [200, 201]
