from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class DocumentBase(BaseModel):
    """Base schema for document with common fields."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    pass

class DocumentUpdate(BaseModel):
    """Schema for updating document information."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class DocumentInDBBase(DocumentBase):
    """Base schema for document stored in DB."""
    id: int
    owner_id: int
    file_name: str
    file_path: str
    file_size: int
    file_type: str = "application/pdf"
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Document(DocumentInDBBase):
    """Schema for returning document data."""
    chunks_count: int = 0

class DocumentInDB(DocumentInDBBase):
    """Schema for document stored in DB."""
    pass

class DocumentChunkBase(BaseModel):
    """Base schema for document chunk."""
    content: str
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentChunkCreate(DocumentChunkBase):
    """Schema for creating a new document chunk."""
    document_id: int

class DocumentChunkInDBBase(DocumentChunkBase):
    """Base schema for document chunk stored in DB."""
    id: int
    document_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentChunk(DocumentChunkInDBBase):
    """Schema for returning document chunk data."""
    pass

class DocumentChunkWithScore(DocumentChunk):
    """Schema for document chunk with relevance score."""
    score: float

class DocumentWithChunks(Document):
    """Schema for document with its chunks."""
    chunks: List[DocumentChunk] = []

class DocumentProcessingStatus(BaseModel):
    """Schema for document processing status."""
    document_id: int
    status: str
    progress: float = 0.0
    message: Optional[str] = None
    chunks_processed: int = 0
    total_chunks: int = 0

class DocumentSearchQuery(BaseModel):
    """Schema for document search query."""
    query: str
    limit: int = 10
    threshold: float = 0.5
    include_chunks: bool = False

class DocumentSearchResult(BaseModel):
    """Schema for document search result."""
    document: Document
    chunks: List[DocumentChunkWithScore] = []
    score: float
