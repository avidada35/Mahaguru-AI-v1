"""Utility functions for processing documents (PDFs, text, etc.)."""
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
from pydantic import BaseModel

from app.core.config import settings
from app.models.document import Document as DocumentModel
from app.schemas.document import DocumentChunkCreate

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunk(BaseModel):
    """Represents a chunk of text from a document with metadata."""
    text: str
    page_number: int
    chunk_index: int
    metadata: dict = {}


class DocumentProcessor:
    """Handles document processing tasks like text extraction and chunking."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Maximum size of each text chunk (in characters)
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def extract_text_from_pdf(self, file_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from a PDF file, returning a list of (text, page_number) tuples.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of (text, page_number) tuples
        """
        try:
            text_pages = []
            with fitz.open(file_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text("text")
                    text_pages.append((text, page_num + 1))  # 1-based page numbers
            return text_pages
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    def chunk_text(self, text: str, page_num: int) -> List[DocumentChunk]:
        """
        Split text into chunks of specified size with overlap.
        
        Args:
            text: The text to chunk
            page_num: The page number this text came from
            
        Returns:
            List of DocumentChunk objects
        """
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Adjust end to not break in the middle of a word if possible
            if end < len(text):
                # Find the last space in the chunk to avoid breaking words
                last_space = text.rfind(' ', start, end)
                if last_space > start + (self.chunk_size // 2):
                    end = last_space
            
            chunk_text = text[start:end].strip()
            if chunk_text:  # Only add non-empty chunks
                chunks.append(DocumentChunk(
                    text=chunk_text,
                    page_number=page_num,
                    chunk_index=chunk_index,
                    metadata={
                        "char_start": start,
                        "char_end": end,
                        "chunk_size": self.chunk_size,
                    }
                ))
                chunk_index += 1
            
            # Move the start position, accounting for overlap
            start = end - self.chunk_overlap if end - self.chunk_overlap > start else end
        
        return chunks
    
    async def process_document(
        self,
        document: DocumentModel,
        db: 'Session'
    ) -> Tuple[bool, str]:
        """
        Process a document: extract text and create chunks.
        
        Args:
            document: The document model instance
            db: Database session
            
        Returns:
            Tuple of (success, message)
        """
        from app.crud import crud_document, crud_document_chunk
        
        try:
            # Update document status to processing
            document = crud_document.document.update_status(
                db, db_obj=document, status="processing"
            )
            
            # Extract text from the document
            if not os.path.exists(document.file_path):
                raise FileNotFoundError(f"Document file not found: {document.file_path}")
            
            # Get the appropriate text extractor based on file type
            file_ext = os.path.splitext(document.file_path)[1].lower()
            
            if file_ext == '.pdf':
                text_pages = await self.extract_text_from_pdf(document.file_path)
            else:
                # For now, only PDF is supported
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Process each page and create chunks
            chunks_created = 0
            for page_text, page_num in text_pages:
                chunks = self.chunk_text(page_text, page_num)
                
                # Save chunks to database
                for chunk in chunks:
                    chunk_data = DocumentChunkCreate(
                        content=chunk.text,
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        metadata=chunk.metadata,
                        document_id=document.id
                    )
                    crud_document_chunk.document_chunk.create(db, obj_in=chunk_data)
                    chunks_created += 1
            
            # Update document status to processed
            document = crud_document.document.update_status(
                db, db_obj=document, status="processed"
            )
            
            return True, f"Successfully processed document with {chunks_created} chunks"
            
        except Exception as e:
            error_msg = f"Error processing document {document.id}: {str(e)}"
            logger.error(error_msg)
            
            # Update document status to failed
            if 'document' in locals():
                crud_document.document.update_status(
                    db, 
                    db_obj=document, 
                    status="failed",
                    error_message=str(e)[:500]  # Truncate long error messages
                )
            
            return False, error_msg
