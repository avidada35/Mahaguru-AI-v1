"""Test utilities and helpers for Mahaguru AI backend tests."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.user import User

TEST_DATA_DIR = Path(__file__).parent / "test_data"

class TestClient(AsyncClient):
    """Extended AsyncClient with authentication support."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user = None
    
    async def authenticate(self, user: User):
        """Authenticate the client with a user."""
        self.user = user
        self.token = create_access_token(user.id)
        self.headers.update({"Authorization": f"Bearer {self.token}"})
        return self
    
    async def login(self, email: str, password: str):
        """Login with email and password."""
        response = await self.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password}
        )
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            self.token = data["access_token"]
            self.headers.update({"Authorization": f"Bearer {self.token}"})
        return response
    
    async def logout(self):
        """Clear authentication."""
        self.token = None
        self.user = None
        self.headers.pop("Authorization", None)


async def create_test_user(
    db: AsyncSession,
    email: str = None,
    password: str = "testpass123",
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    """Create a test user in the database."""
    from app.crud.crud_user import user_crud
    from app.schemas.user import UserCreate
    
    email = email or f"test_{uuid.uuid4().hex[:8]}@example.com"
    user_in = UserCreate(
        email=email,
        password=password,
        full_name="Test User",
    )
    user = await user_crud.create(db, obj_in=user_in)
    
    if is_active:
        user.is_active = True
    if is_superuser:
        user.is_superuser = True
    
    await db.commit()
    await db.refresh(user)
    return user


async def get_auth_headers(
    client: AsyncClient, email: str, password: str
) -> Dict[str, str]:
    """Get authentication headers for a test user."""
    login_data = {
        "username": email,
        "password": password,
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def read_test_data(filename: str) -> Union[Dict, List, str]:
    """Read test data from a JSON file in the test_data directory."""
    path = TEST_DATA_DIR / filename
    if not path.exists():
        return {}
    
    if path.suffix == ".json":
        with open(path, "r") as f:
            return json.load(f)
    else:
        return path.read_text()


def assert_paginated_response(
    response_data: Dict[str, Any],
    expected_count: int,
    total_pages: int = 1,
    current_page: int = 1,
    page_size: int = 10,
) -> None:
    """Assert that a paginated API response has the expected structure."""
    assert "items" in response_data
    assert "total" in response_data
    assert "page" in response_data
    assert "pages" in response_data
    assert "size" in response_data
    
    assert isinstance(response_data["items"], list)
    assert len(response_data["items"]) == expected_count
    assert response_data["total"] >= expected_count
    assert response_data["pages"] == total_pages
    assert response_data["page"] == current_page
    assert response_data["size"] == page_size


def assert_error_response(
    response_data: Dict[str, Any],
    status_code: int,
    detail: Optional[str] = None,
    error_type: Optional[str] = None,
) -> None:
    """Assert that an error response has the expected structure."""
    assert "detail" in response_data
    
    if detail is not None:
        if isinstance(detail, str):
            assert response_data["detail"] == detail
        else:
            # For validation errors, check if the message is in the detail
            assert any(detail in msg for msg in response_data["detail"])
    
    if error_type is not None:
        assert "type" in response_data
        assert response_data["type"] == error_type
