from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User  # noqa: F401
    from app.models.document_chunk import DocumentChunk  # noqa: F401


class Document(Base):
    """Document model for storing PDF metadata and file information."""
    
    __tablename__ = "documents"
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), default="application/pdf")
    
    # Document metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # Stored as a JSON array of strings
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, processed, failed
    error_message = Column(Text, nullable=True)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """Convert document to dictionary, including related chunks count."""
        data = super().to_dict()
        data["chunks_count"] = len(self.chunks) if hasattr(self, "chunks") else 0
        return data
    
    def update_status(self, status: str, error: Optional[str] = None) -> None:
        """Update document processing status."""
        self.status = status
        if error:
            self.error_message = error
