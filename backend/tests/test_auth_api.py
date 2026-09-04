import pytest


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_register_user(client, test_user_data):
    """Test user registration"""
    response = client.post("/api/auth/register", json=test_user_data)

    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == test_user_data["email"]
    assert data["user"]["full_name"] == test_user_data["full_name"]
    assert data["user"]["role"] == "user"


def test_register_duplicate_email(client, test_user_data):
    """Test registering with duplicate email"""
    # First registration
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201

    # Second registration with same email
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register user first
    client.post("/api/auth/register", json=test_user_data)

    # Login
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == test_user_data["email"]


def test_login_invalid_credentials(client, test_user_data):
    """Test login with invalid credentials"""
    # Register user first
    client.post("/api/auth/register", json=test_user_data)

    # Login with wrong password
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=login_data)

    assert response.status_code == 401


def test_get_current_user(authenticated_client):
    """Test getting current user info"""
    client, user = authenticated_client

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == user["email"]
    assert data["id"] == user["id"]


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = client.get("/api/auth/me")

    assert response.status_code == 403  # FastAPI returns 403 for missing auth


def test_logout(authenticated_client):
    """Test logout"""
    client, user = authenticated_client

    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert "message" in response.json()
