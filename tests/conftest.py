"""Pytest fixtures and isolated test database setup."""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.dependencies.db import get_db

# Use an isolated in-memory SQLite database for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create fresh database tables for each test and drop them on completion."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency pointing to isolated test DB."""
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def user_a_data() -> dict:
    return {
        "email": "user.a@example.com",
        "password": "Password123!",
        "full_name": "Alice Developer",
    }


@pytest.fixture(scope="function")
def user_b_data() -> dict:
    return {
        "email": "user.b@example.com",
        "password": "Password456!",
        "full_name": "Bob Engineer",
    }


@pytest.fixture(scope="function")
def user_a_token(client: TestClient, user_a_data: dict) -> str:
    """Register and log in User A, returning access token."""
    client.post("/api/v1/auth/register", json=user_a_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_a_data["email"], "password": user_a_data["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def user_b_token(client: TestClient, user_b_data: dict) -> str:
    """Register and log in User B, returning access token."""
    client.post("/api/v1/auth/register", json=user_b_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_b_data["email"], "password": user_b_data["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers_a(user_a_token: str) -> dict:
    return {"Authorization": f"Bearer {user_a_token}"}


@pytest.fixture(scope="function")
def auth_headers_b(user_b_token: str) -> dict:
    return {"Authorization": f"Bearer {user_b_token}"}
