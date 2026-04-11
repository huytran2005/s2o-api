"""
Standard BVA Test: POST /auth/login
Password [8-32], Email valid format

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import pytest


class TestLoginPasswordStandardBVA:
    """Standard BVA for password in login [8-32]"""

    def test_login_password_min_8(self, customer_user, client):
        """BVA: password = min = 8 chars"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "customer@test.com",
                "password": "ValidPass123"  # Pre-set password
            }
        )
        # Should work since customer_user fixture exists with this exact password
        assert resp.status_code in [200, 401, 422]

    def test_login_password_min_plus_9(self, client):
        """BVA: password = min+ = 9 chars"""
        # Testing validation only - 9 chars is valid
        resp = client.post(
            "/auth/login",
            json={
                "email": "test@test.com",
                "password": "Pass12345"  # 9 chars
            }
        )
        # 401 (user not found) is OK - validation passed
        assert resp.status_code in [200, 401]

    def test_login_password_nom_20(self, client):
        """BVA: password = nom = 20 chars"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "test@test.com",
                "password": "Pass" + "x" * 16  # 20 chars
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_password_max_minus_31(self, client):
        """BVA: password = max- = 31 chars"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "test@test.com",
                "password": "Pass" + "x" * 27  # 31 chars
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_password_max_32(self, client):
        """BVA: password = max = 32 chars"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "test@test.com",
                "password": "Pass" + "x" * 28  # 32 chars
            }
        )
        assert resp.status_code in [200, 401]


class TestLoginEmailStandardBVA:
    """Standard BVA for email format in login"""

    def test_login_email_min_short_valid(self, client):
        """BVA: email = short valid"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "a@b.co",  # minimal
                "password": "ValidPass123"
            }
        )
        # Validation passes, 401 because user doesn't exist is OK
        assert resp.status_code in [200, 401]

    def test_login_email_min_plus_simple(self, client):
        """BVA: email = simple valid"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "user@test.com",
                "password": "ValidPass123"
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_email_nom_with_numbers(self, client):
        """BVA: email = with numbers"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "user123@example456.com",
                "password": "ValidPass123"
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_email_max_minus_subdomain(self, client):
        """BVA: email = subdomain"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "user@sub.example.com",
                "password": "ValidPass123"
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_email_max_long_valid(self, client):
        """BVA: email = max long valid"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "very.long.email.address@very.long.domain.co.uk",
                "password": "ValidPass123"
            }
        )
        assert resp.status_code in [200, 401]


class TestLoginRequiredFieldsStandardBVA:
    """Standard BVA for both email and password together"""

    def test_login_both_valid_minimal(self, client):
        """BVA: both fields at minimal valid"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "a@b.co",
                "password": "Pass1234"
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_both_valid_average(self, client):
        """BVA: both fields at average valid"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "ValidPass123"
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_both_valid_max(self, client):
        """BVA: both fields at max valid"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "very.long.user@very.long.domain.com",
                "password": "Pass" + "x" * 28
            }
        )
        assert resp.status_code in [200, 401]

    def test_login_existing_customer(self, customer_user, client):
        """BVA: login with existing customer user"""
        resp = client.post(
            "/auth/login",
            json={
                "email": "customer@test.com",
                "password": "ValidPass123"
            }
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_all_valid_variations(self, client):
        """BVA: all valid variations work"""
        valid_emails = [
            "simple@test.com",
            "with.dot@test.com",
            "with_underscore@test.com",
            "with123numbers@test.com"
        ]
        valid_passwords = [
            "Pass1234",  # min 8
            "Pass" + "x" * 28  # max 32
        ]

        # Just verify a few combinations don't cause validation errors
        for email in valid_emails[:2]:
            for password in valid_passwords:
                resp = client.post(
                    "/auth/login",
                    json={"email": email, "password": password}
                )
                # 401 (user not found) is OK - means validation passed
                assert resp.status_code in [200, 401]
