"""Tests for authentication endpoints."""
import uuid
from typing import Dict

import pytest
from fastapi import status

from app.core.config import settings
from app.models.user import User
from tests.conftest import TestClient
from tests.utils import create_test_user, get_auth_headers

pytestmark = pytest.mark.asyncio


class TestAuth:
    """Test authentication endpoints."""

    async def test_login_success(self, async_client: TestClient, db_session):
        """Test successful user login."""
        # Create a test user
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "testpass123"
        await create_test_user(db_session, email=email, password=password)

        # Test login
        login_data = {
            "username": email,
            "password": password,
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, async_client: TestClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    async def test_get_current_user(self, async_client: TestClient, db_session):
        """Test retrieving the current user with a valid token."""
        # Create and authenticate a test user
        user = await create_test_user(db_session)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        response = await async_client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user.email
        assert data["is_active"] is True
        assert "hashed_password" not in data

    async def test_get_current_user_invalid_token(self, async_client: TestClient):
        """Test retrieving the current user with an invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate credentials"

    async def test_refresh_token(self, async_client: TestClient, db_session):
        """Test refreshing an access token."""
        # Create and login a test user
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "testpass123"
        await create_test_user(db_session, email=email, password=password)
        
        # Get refresh token from login
        login_data = {"username": email, "password": password}
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        refresh_token = login_response.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        
        # Test token refresh
        response = await async_client.post(
            "/api/v1/auth/refresh",
            cookies={settings.REFRESH_TOKEN_COOKIE_NAME: refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    async def test_logout(self, async_client: TestClient, db_session):
        """Test user logout."""
        # Create and login a test user
        user = await create_test_user(db_session)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        # Test logout
        response = await async_client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Successfully logged out"}
        
        # Verify the token is no longer valid
        response = await async_client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_register_new_user(self, async_client: TestClient, db_session):
        """Test registering a new user."""
        user_data = {
            "email": f"newuser_{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpass123",
            "full_name": "New User",
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "hashed_password" not in data
        
        # Verify the user exists in the database
        from app.crud.crud_user import user_crud
        db_user = await user_crud.get_by_email(db_session, email=user_data["email"])
        assert db_user is not None
        assert db_user.email == user_data["email"]
        assert db_user.is_active is True
        assert db_user.is_superuser is False

    async def test_register_existing_user(self, async_client: TestClient, db_session):
        """Test registering an existing user."""
        email = f"existing_{uuid.uuid4().hex[:8]}@example.com"
        await create_test_user(db_session, email=email)
        
        user_data = {
            "email": email,
            "password": "testpass123",
            "full_name": "Existing User",
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "The user with this email already exists"

    async def test_register_invalid_email(self, async_client: TestClient):
        """Test registering with an invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "testpass123",
            "full_name": "Invalid Email",
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "value is not a valid email address" in str(response.json())

    async def test_register_short_password(self, async_client: TestClient):
        """Test registering with a short password."""
        user_data = {
            "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
            "password": "short",
            "full_name": "Short Password",
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "ensure this value has at least 8 characters" in str(response.json())
