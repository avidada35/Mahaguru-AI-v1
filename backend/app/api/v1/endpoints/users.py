"""User management endpoints for creating, reading, updating, and deleting users."""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.models.user import User as UserModel
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserListResponse,
)

router = APIRouter()


class UserFilterParams(BaseModel):
    """Query parameters for filtering users."""
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> UserResponse:
    """
    Get current user information.
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> UserResponse:
    """
    Get a specific user by ID.
    
    Only superusers can access other users' data.
    """
    if user_id == current_user.id or current_user.is_superuser:
        user = await crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions",
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    user_in: UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> UserResponse:
    """
    Create a new user.
    
    Only superusers can create new users.
    """
    # Check if user with email already exists
    existing_user = await crud.user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    
    # Create the user
    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    user_id: int,
    user_in: UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> UserResponse:
    """
    Update a user.
    
    Users can update their own information, but only superusers can update other users.
    """
    # Check if user exists
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check permissions
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user",
        )
    
    # Prevent non-superusers from changing their role
    if not current_user.is_superuser and user_in.is_superuser != user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can change user roles",
        )
    
    # Update the user
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.Msg)
async def delete_user(
    *,
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> schemas.Msg:
    """
    Delete a user.
    
    Only superusers can delete users.
    """
    # Prevent users from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )
    
    # Check if user exists
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Delete the user
    await crud.user.remove(db, id=user_id)
    return {"msg": "User deleted successfully"}


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> List[UserResponse]:
    """
    List all users.
    
    Only superusers can list all users.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    *,
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> UserResponse:
    """
    Deactivate a user account.
    
    Only superusers can deactivate users.
    """
    # Prevent users from deactivating themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )
    
    # Check if user exists
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Deactivate the user
    user = await crud.user.deactivate(db, db_obj=user)
    return user


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    *,
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> UserResponse:
    """
    Activate a user account.
    
    Only superusers can activate users.
    """
    # Check if user exists
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Activate the user
    user = await crud.user.activate(db, db_obj=user)
    return user


@router.get("/{user_id}/documents", response_model=List[schemas.DocumentResponse])
async def get_user_documents(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> List[schemas.DocumentResponse]:
    """
    Get all documents for a specific user.
    
    Users can only see their own documents, unless they are superusers.
    """
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view these documents",
        )
    
    documents = await crud.document.get_multi_by_owner(
        db, owner_id=user_id, skip=skip, limit=limit
    )
    return documents
