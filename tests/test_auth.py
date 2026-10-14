"""Tests for authentication endpoints (register, login, me)."""

from fastapi import status
from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient, user_a_data: dict) -> None:
    """Test registering a new user with valid details."""
    response = client.post("/api/v1/auth/register", json=user_a_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_a_data["email"].lower()
    assert data["full_name"] == user_a_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data  # Never expose passwords or hashes!


def test_register_duplicate_email(client: TestClient, user_a_data: dict) -> None:
    """Test duplicate registration returns 409 Conflict."""
    client.post("/api/v1/auth/register", json=user_a_data)
    response = client.post("/api/v1/auth/register", json=user_a_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"]


def test_register_invalid_email(client: TestClient) -> None:
    """Test registering with an invalid email returns 422."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "Password123!"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_short_password(client: TestClient) -> None:
    """Test registering with a password less than 8 characters returns 422."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "valid@example.com", "password": "short"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success_json(client: TestClient, user_a_data: dict) -> None:
    """Test login using JSON body."""
    client.post("/api/v1/auth/register", json=user_a_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_a_data["email"], "password": user_a_data["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_success_form_data(client: TestClient, user_a_data: dict) -> None:
    """Test login using OAuth2 form-data (as used by Swagger UI)."""
    client.post("/api/v1/auth/register", json=user_a_data)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user_a_data["email"], "password": user_a_data["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient, user_a_data: dict) -> None:
    """Test login with an incorrect password returns 401."""
    client.post("/api/v1/auth/register", json=user_a_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_a_data["email"], "password": "WrongPassword!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient) -> None:
    """Test login with non-existent user returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_profile(
    client: TestClient, user_a_data: dict, auth_headers_a: dict
) -> None:
    """Test accessing /auth/me with valid Bearer token."""
    response = client.get("/api/v1/auth/me", headers=auth_headers_a)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_a_data["email"].lower()
    assert data["full_name"] == user_a_data["full_name"]
    assert "hashed_password" not in data


def test_get_current_user_missing_token(client: TestClient) -> None:
    """Test accessing protected route without Authorization header returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_invalid_token(client: TestClient) -> None:
    """Test accessing protected route with malformed or tampered token returns 401."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
