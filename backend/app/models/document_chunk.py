from typing import TYPE_CHECKING, Optional

import numpy as np
from sqlalchemy import Column, Float, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import Document  # noqa: F401


class Vector(TypeDecorator):
    """
    Custom type for storing vector embeddings in the database.
    Converts between numpy arrays and database format.
    """
    impl = ARRAY(Float)
    cache_ok = True
    
    def __init__(self, dim: Optional[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(Float, dimensions=1))
        return dialect.type_descriptor(Text())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, np.ndarray):
            return value.tolist()
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return np.array(value, dtype=np.float32)


class DocumentChunk(Base):
    """
    Represents a chunk of text from a document along with its embedding.
    Used for semantic search and retrieval.
    """
    __tablename__ = "document_chunks"
    
    # Text content
    text = Column(Text, nullable=False)
    
    # Position information
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    
    # Embedding vector (stored as JSONB in PostgreSQL)
    embedding = Column(Vector(1536), nullable=False)  # Default dimension for OpenAI embeddings
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON string of additional metadata
    
    # Relationships
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    document = relationship("Document", back_populates="chunks")
    
    def __init__(self, **kwargs):
        # Convert numpy array to list for JSON serialization if needed
        if "embedding" in kwargs and isinstance(kwargs["embedding"], np.ndarray):
            kwargs["embedding"] = kwargs["embedding"].tolist()
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert chunk to dictionary, excluding the embedding by default."""
        data = super().to_dict()
        # Don't include the full embedding in the dict by default as it's very large
        if "embedding" in data:
            data["embedding"] = f"Vector[{len(data['embedding'])}]" if data["embedding"] else None
        return data
    
    def to_dict_with_embedding(self) -> dict:
        """Convert chunk to dictionary including the full embedding vector."""
        data = self.to_dict()
        data["embedding"] = self.embedding.tolist() if self.embedding is not None else None
        return data
