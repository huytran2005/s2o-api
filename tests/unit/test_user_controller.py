import pytest
import uuid
from models.user import User
from models.restaurant import Restaurant
from utils.dependencies import get_current_user

def test_create_staff_not_owner(client, app):
    """Test creating staff by non-owner user should return 403."""
    current_user = User(id=uuid.uuid4(), role="customer", email="cust@test.com")
    app.dependency_overrides[get_current_user] = lambda: current_user
    
    resp = client.post(f"/restaurants/{uuid.uuid4()}/staff", json={
        "email": "staff@test.com",
        "password": "SecurePass123",
        "display_name": "Staff User",
        "phone": "12345678"
    })
    assert resp.status_code == 403
    assert "Only owner can create staff" in resp.json()["detail"]


def test_create_staff_not_your_restaurant(client, app, fake_db):
    """Test creating staff for a restaurant not owned by current owner should return 403."""
    owner = User(id=uuid.uuid4(), role="owner", email="owner@test.com")
    app.dependency_overrides[get_current_user] = lambda: owner
    
    # Another owner's restaurant
    other_owner_id = uuid.uuid4()
    rest = Restaurant(id=uuid.uuid4(), name="Other Rest", owner_id=other_owner_id)
    fake_db.add(rest)
    
    resp = client.post(f"/restaurants/{rest.id}/staff", json={
        "email": "staff@test.com",
        "password": "SecurePass123",
        "display_name": "Staff User",
        "phone": "12345678"
    })
    assert resp.status_code == 403
    assert "Not your restaurant" in resp.json()["detail"]


def test_create_staff_duplicate_email(client, app, fake_db):
    """Test creating staff with an email that already exists should return 400."""
    owner = User(id=uuid.uuid4(), role="owner", email="owner@test.com")
    app.dependency_overrides[get_current_user] = lambda: owner
    
    rest = Restaurant(id=uuid.uuid4(), name="My Rest", owner_id=owner.id)
    fake_db.add(rest)
    
    # Existing user with the same email
    existing_user = User(id=uuid.uuid4(), email="duplicate@test.com", role="customer")
    fake_db.add(existing_user)
    
    resp = client.post(f"/restaurants/{rest.id}/staff", json={
        "email": "duplicate@test.com",
        "password": "SecurePass123",
        "display_name": "Staff User",
        "phone": "12345678"
    })
    assert resp.status_code == 400
    assert "Email already exists" in resp.json()["detail"]


def test_create_staff_success(client, app, fake_db):
    """Test successful staff creation by restaurant owner."""
    owner = User(id=uuid.uuid4(), role="owner", email="owner@test.com")
    app.dependency_overrides[get_current_user] = lambda: owner
    
    rest = Restaurant(id=uuid.uuid4(), name="My Rest", owner_id=owner.id)
    fake_db.add(rest)
    
    staff_data = {
        "email": "new_staff@test.com",
        "password": "SecurePass123",
        "display_name": "New Staff",
        "phone": "12345678"
    }
    
    resp = client.post(f"/restaurants/{rest.id}/staff", json=staff_data)
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Staff created successfully"
    assert "staff_id" in data
    assert data["restaurant_id"] == str(rest.id)
    
    # Verify staff was actually added to DB
    staff = fake_db.query(User).filter(User.email == "new_staff@test.com").first()
    assert staff is not None
    assert staff.role == "staff"
    assert staff.restaurant_id == rest.id
    assert staff.display_name == "New Staff"
