from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import Document  # noqa: F401

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    documents = relationship("Document", back_populates="owner")
    
    def __init__(self, **kwargs):
        if "password" in kwargs:
            self.set_password(kwargs.pop("password"))
        super().__init__(**kwargs)
    
    def set_password(self, password: str) -> None:
        """Set hashed password."""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return pwd_context.verify(password, self.hashed_password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary, excluding sensitive data."""
        data = super().to_dict()
        data.pop("hashed_password", None)
        return data
    
    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Generate a password hash."""
        return pwd_context.hash(password)
    
    @classmethod
    def create_superuser(
        cls, email: str, password: str, full_name: Optional[str] = None
    ) -> 'User':
        """Create a new superuser."""
        return cls(
            email=email,
            password=password,
            full_name=full_name or email.split("@")[0],
            is_active=True,
            is_superuser=True,
        )
