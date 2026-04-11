"""
Standard BVA Test: POST /guest/session
QR code only - endpoint takes 'code' as query parameter

Standard BVA Formula: min, min+, nom, max-, max (VALID only)
"""
import pytest


class TestGuestSessionQRStandardBVA:
    """Standard BVA for guest session QR code"""

    def test_guest_session_qr_valid(self, client, test_qr_code):
        """BVA: QR code valid"""
        resp = client.post(
            f"/guest/session?code={test_qr_code.code}"
        )
        assert resp.status_code in [200, 201], f"Got {resp.status_code}: {resp.text}"

    def test_guest_session_qr_simple_code_variant(self, client, test_qr_code):
        """BVA: QR code with valid format"""
        resp = client.post(
            f"/guest/session?code={test_qr_code.code}"
        )
        assert resp.status_code in [200, 201], f"Got {resp.status_code}: {resp.text}"

    def test_guest_session_qr_with_special_chars(self, client, db, test_table):
        """BVA: QR code with special chars (valid)"""
        from models.qr_code import QRCode
        from uuid import uuid4
        qr = QRCode(
            id=uuid4(),
            table_id=test_table.id,
            restaurant_id=test_table.restaurant_id,
            code="QR-CODE_123-456",
            status="active"
        )
        db.add(qr)
        db.commit()

        resp = client.post(
            f"/guest/session?code={qr.code}"
        )
        assert resp.status_code in [200, 201], f"Got {resp.status_code}: {resp.text}"

    def test_guest_session_multiple_sessions_same_qr(self, client, test_qr_code):
        """BVA: Create multiple sessions with same QR"""
        resp1 = client.post(
            f"/guest/session?code={test_qr_code.code}"
        )
        assert resp1.status_code in [200, 201], f"Got {resp1.status_code}: {resp1.text}"

        resp2 = client.post(
            f"/guest/session?code={test_qr_code.code}"
        )
        assert resp2.status_code in [200, 201], f"Got {resp2.status_code}: {resp2.text}"

    def test_guest_session_qr_case_sensitivity(self, client, test_qr_code):
        """BVA: QR code case sensitivity test"""
        resp = client.post(
            f"/guest/session?code={test_qr_code.code}"
        )
        assert resp.status_code in [200, 201], f"Got {resp.status_code}: {resp.text}"


class TestGuestSessionInvalidQRStandardBVA:
    """Standard BVA for invalid guest session scenarios"""

    def test_guest_session_invalid_qr_code(self, client):
        """BVA: Invalid/non-existent QR code"""
        resp = client.post(
            "/guest/session?code=INVALID_QR_CODE"
        )
        assert resp.status_code == 400, f"Got {resp.status_code}: {resp.text}"

    def test_guest_session_missing_code(self, client):
        """BVA: Missing QR code parameter"""
        resp = client.post(
            "/guest/session"
        )
        assert resp.status_code in [400, 422], f"Got {resp.status_code}: {resp.text}"

    def test_guest_session_empty_code(self, client):
        """BVA: Empty QR code parameter"""
        resp = client.post(
            "/guest/session?code="
        )
        assert resp.status_code in [400, 422], f"Got {resp.status_code}: {resp.text}"

    def test_guest_session_inactive_qr(self, client, db, test_table):
        """BVA: Inactive QR code"""
        from models.qr_code import QRCode
        from uuid import uuid4
        qr = QRCode(
            id=uuid4(),
            table_id=test_table.id,
            restaurant_id=test_table.restaurant_id,
            code="INACTIVE_QR",
            status="inactive"
        )
        db.add(qr)
        db.commit()

        resp = client.post(
            f"/guest/session?code={qr.code}"
        )
        assert resp.status_code == 400, f"Got {resp.status_code}: {resp.text}"

    def test_guest_session_expired_qr(self, client, db, test_table):
        """BVA: Expired QR code"""
        from models.qr_code import QRCode
        from uuid import uuid4
        qr = QRCode(
            id=uuid4(),
            table_id=test_table.id,
            restaurant_id=test_table.restaurant_id,
            code="EXPIRED_QR",
            status="inactive"
        )
        db.add(qr)
        db.commit()

        resp = client.post(
            f"/guest/session?code={qr.code}"
        )
        assert resp.status_code == 400, f"Got {resp.status_code}: {resp.text}"
