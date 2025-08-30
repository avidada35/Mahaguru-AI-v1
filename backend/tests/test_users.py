"""Tests for user management endpoints."""
import uuid
from typing import Dict, List

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from tests.conftest import TestClient
from tests.utils import (
    assert_error_response,
    assert_paginated_response,
    create_test_user,
    get_auth_headers,
)

pytestmark = pytest.mark.asyncio


class TestUsers:
    """Test user management endpoints."""

    async def test_get_users_unauthorized(self, async_client: TestClient):
        """Test getting users without authentication."""
        response = await async_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_users_regular_user(self, async_client: TestClient, db_session: AsyncSession):
        """Test that regular users cannot list all users."""
        # Create and authenticate a regular user
        user = await create_test_user(db_session, is_superuser=False)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        response = await async_client.get("/api/v1/users/", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_users_superuser(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test that superusers can list all users."""
        # Create test users
        users = [
            await create_test_user(
                db_session,
                email=f"user_{i}@example.com",
                is_superuser=(i == 0),  # First user is superuser
            )
            for i in range(3)
        ]
        
        # Authenticate as superuser
        headers = await get_auth_headers(async_client, users[0].email, "testpass123")
        
        # Get all users
        response = await async_client.get("/api/v1/users/", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert_paginated_response(data, expected_count=3, total_pages=1)
        
        # Verify user data
        user_emails = {user["email"] for user in data["items"]}
        assert all(user.email in user_emails for user in users)

    async def test_get_user_me(self, async_client: TestClient, db_session: AsyncSession):
        """Test getting the current user's profile."""
        # Create and authenticate a test user
        user = await create_test_user(db_session)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        response = await async_client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["full_name"] == user.full_name
        assert "hashed_password" not in data

    async def test_get_user_by_id(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test getting a user by ID."""
        # Create test users
        user1 = await create_test_user(db_session, email="user1@example.com")
        user2 = await create_test_user(db_session, email="user2@example.com")
        
        # Authenticate as user1
        headers = await get_auth_headers(async_client, user1.email, "testpass123")
        
        # Get user2's profile
        response = await async_client.get(f"/api/v1/users/{user2.id}", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user2.id
        assert data["email"] == user2.email
        assert "hashed_password" not in data

    async def test_get_nonexistent_user(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test getting a user that doesn't exist."""
        user = await create_test_user(db_session)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        response = await async_client.get("/api/v1/users/999999", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"

    async def test_update_user_me(self, async_client: TestClient, db_session: AsyncSession):
        """Test updating the current user's profile."""
        user = await create_test_user(db_session, full_name="Original Name")
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com",
        }
        
        response = await async_client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["email"] == update_data["email"]
        
        # Verify the update in the database
        from app.crud.crud_user import user_crud
        db_user = await user_crud.get(db_session, id=user.id)
        assert db_user.full_name == update_data["full_name"]
        assert db_user.email == update_data["email"]

    async def test_update_user_me_password(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test updating the current user's password."""
        user = await create_test_user(db_session)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        update_data = {
            "password": "newpassword123",
        }
        
        response = await async_client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the new password works
        from app.crud.crud_user import user_crud
        db_user = await user_crud.authenticate(
            db_session, email=user.email, password="newpassword123"
        )
        assert db_user is not None

    async def test_update_user_me_invalid_email(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test updating with an invalid email."""
        user = await create_test_user(db_session)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        update_data = {
            "email": "invalid-email",
        }
        
        response = await async_client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "value is not a valid email address" in str(response.json())

    async def test_update_other_user_unauthorized(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test that users cannot update other users' profiles."""
        # Create two users
        user1 = await create_test_user(db_session, email="user1@example.com")
        user2 = await create_test_user(db_session, email="user2@example.com")
        
        # Authenticate as user1
        headers = await get_auth_headers(async_client, user1.email, "testpass123")
        
        # Try to update user2
        update_data = {"full_name": "Hacked"}
        response = await async_client.put(
            f"/api/v1/users/{user2.id}",
            json=update_data,
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Not enough permissions"

    async def test_delete_user_me(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test deleting the current user's account."""
        user = await create_test_user(db_session)
        headers = await get_auth_headers(async_client, user.email, "testpass123")
        
        response = await async_client.delete("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "User deleted successfully"}
        
        # Verify the user is deactivated
        from app.crud.crud_user import user_crud
        db_user = await user_crud.get(db_session, id=user.id)
        assert db_user is not None
        assert db_user.is_active is False

    async def test_delete_other_user_unauthorized(
        self, async_client: TestClient, db_session: AsyncSession
    ):
        """Test that users cannot delete other users' accounts."""
        # Create two users
        user1 = await create_test_user(db_session, email="user1@example.com")
        user2 = await create_test_user(db_session, email="user2@example.com")
        
        # Authenticate as user1
        headers = await get_auth_headers(async_client, user1.email, "testpass123")
        
        # Try to delete user2
        response = await async_client.delete(
            f"/api/v1/users/{user2.id}",
            headers=headers,
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Not enough permissions"
        
        # Verify user2 still exists and is active
        from app.crud.crud_user import user_crud
        db_user = await user_crud.get(db_session, id=user2.id)
        assert db_user is not None
        assert db_user.is_active is True
