import pytest
from uuid import uuid4

@pytest.fixture
def unique_id():
    return str(uuid4())

def test_successful_owner_registration(client, unique_id):
    """Test a new owner can successfully register."""
    owner_email = f"owner_{unique_id}@example.com"
    response = client.post(
        "/auth/register-owner",
        json={
            "email": owner_email,
            "password": "SecurePassword123",
            "display_name": "Test Owner",
            "phone": "123456789"
        },
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Register successful"}


def test_successful_customer_registration(client, unique_id):
    """Test a new customer can successfully register."""
    customer_email = f"customer_{unique_id}@example.com"
    response = client.post(
        "/auth/register",
        json={
            "email": customer_email,
            "password": "CustomerPassword123",
            "display_name": "Test Customer",
            "phone": "987654321"
        },
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Register successful"}


def test_duplicate_email_registration(client, unique_id):
    """Test that registering with a duplicate email returns a 400 error."""
    email = f"duplicate_{unique_id}@example.com"
    client.post(
        "/auth/register-owner",
        json={
            "email": email,
            "password": "Password1",
            "display_name": "First User",
            "phone": "111111"
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password2",
            "display_name": "Second User",
            "phone": "222222"
        },
    )
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]


def test_successful_login(client, unique_id):
    """Test that a registered user can successfully log in."""
    email = f"login_{unique_id}@example.com"
    password = "LoginPassword123"
    client.post(
        "/auth/register-owner",
        json={"email": email, "password": password, "display_name": "Login User", "phone": "000000"},
    )

    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_auth_me_with_valid_token(client, unique_id):
    """Test accessing /auth/me with a valid JWT token."""
    email = f"me_{unique_id}@example.com"
    password = "ValidTokenPass123"
    
    # Register
    client.post(
        "/auth/register-owner",
        json={"email": email, "password": password, "display_name": "Me User", "phone": "444555"},
    )

    # Login - Response should only have access_token and token_type
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    login_data = login_response.json()
    token = login_data["access_token"]
    
    # Check that user_id is NOT in the login response as per requirements
    assert "user_id" not in login_data

    # Use access_token to call /auth/me
    response = client.get(
        "/auth/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "owner"
    assert "id" in data
    assert data.get("restaurant_id") is None


def test_auth_me_without_token(client):
    """Test accessing /auth/me without an Authorization header."""
    response = client.get("/auth/me")
    assert response.status_code == 401
