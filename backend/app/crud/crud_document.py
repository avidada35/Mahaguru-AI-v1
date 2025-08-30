from typing import List, Optional, Union, Dict, Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentChunkCreate


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    """CRUD operations for Document model."""
    
    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get multiple documents by owner ID."""
        return (
            db.query(self.model)
            .filter(Document.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_owner(
        self, db: Session, *, obj_in: DocumentCreate, owner_id: int
    ) -> Document:
        """Create a new document with an owner."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_status(
        self, db: Session, *, db_obj: Document, status: str, error_message: str = None
    ) -> Document:
        """Update document processing status."""
        db_obj.status = status
        if error_message:
            db_obj.error_message = error_message
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDDocumentChunk(CRUDBase[DocumentChunk, DocumentChunkCreate, Dict[str, Any]]):
    """CRUD operations for DocumentChunk model."""
    
    def get_multi_by_document(
        self, db: Session, *, document_id: int, skip: int = 0, limit: int = 100
    ) -> List[DocumentChunk]:
        """Get multiple chunks by document ID."""
        return (
            db.query(self.model)
            .filter(DocumentChunk.document_id == document_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_document(
        self, db: Session, *, obj_in: DocumentChunkCreate, document_id: int
    ) -> DocumentChunk:
        """Create a new chunk associated with a document."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, document_id=document_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_document_and_index(
        self, db: Session, *, document_id: int, chunk_index: int
    ) -> Optional[DocumentChunk]:
        """Get a chunk by document ID and chunk index."""
        return (
            db.query(self.model)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.chunk_index == chunk_index,
            )
            .first()
        )
    
    def get_similar_chunks(
        self, db: Session, *, embedding: List[float], threshold: float = 0.7, limit: int = 10
    ) -> List[DocumentChunk]:
        """
        Find document chunks that are similar to the provided embedding vector.
        
        Args:
            db: Database session
            embedding: The embedding vector to compare against
            threshold: Similarity threshold (0-1)
            limit: Maximum number of results to return
            
        Returns:
            List of similar document chunks with similarity scores
        """
        # Using PostgreSQL vector similarity search
        query = """
            SELECT *, embedding <=> :embedding::vector AS similarity
            FROM document_chunks
            WHERE (embedding <=> :embedding::vector) < :threshold
            ORDER BY similarity
            LIMIT :limit
        """
        
        results = db.execute(
            query, 
            {
                "embedding": embedding,
                "threshold": 1.0 - threshold,  # Convert to distance
                "limit": limit
            }
        ).fetchall()
        
        # Convert results to DocumentChunk objects with similarity score
        chunks = []
        for row in results:
            chunk = DocumentChunk(**dict(row))
            chunk.similarity = 1.0 - row.similarity  # Convert distance back to similarity
            chunks.append(chunk)
        
        return chunks


# Create singleton instances
document = CRUDDocument(Document)
document_chunk = CRUDDocumentChunk(DocumentChunk)
