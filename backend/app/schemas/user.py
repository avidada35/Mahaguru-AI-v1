from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    """Base schema for user stored in DB."""
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    class Config:
        from_attributes = True

class User(UserInDBBase):
    """Schema for returning user data (without sensitive information)."""
    pass

class UserInDB(UserInDBBase):
    """Schema for user stored in DB (includes hashed password)."""
    hashed_password: str

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

class UserPasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr

class UserPasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
