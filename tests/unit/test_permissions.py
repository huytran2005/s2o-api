import pytest
from fastapi import HTTPException

from utils.permissions import require_roles


class DummyUser:
    def __init__(self, role):
        self.role = role


def test_require_roles_allows_matching_role():
    require_roles(DummyUser("owner"), ["owner", "admin"])


def test_require_roles_rejects_other_roles():
    with pytest.raises(HTTPException) as exc_info:
        require_roles(DummyUser("customer"), ["owner", "admin"])

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Permission denied"
