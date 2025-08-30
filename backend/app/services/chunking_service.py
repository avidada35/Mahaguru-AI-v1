"""Document chunking service for processing and normalizing text into chunks."""
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF
from langdetect import detect
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    document_id: int
    chunk_index: int
    page_number: Optional[int] = None
    section: Optional[str] = None
    metadata: Optional[Dict] = None

class ChunkingConfig(BaseModel):
    """Configuration for document chunking."""
    chunk_size: int = Field(default=1000, description="Target chunk size in characters")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks in characters")
    min_chunk_size: int = Field(default=100, description="Minimum chunk size")
    max_chunk_size: int = Field(default=2000, description="Maximum chunk size")
    split_by_headings: bool = Field(default=True, description="Whether to split by headings")
    detect_language: bool = Field(default=True, description="Whether to detect language")
    
    class Config:
        extra = "forbid"

class DocumentChunker:
    """Handles chunking of documents into smaller pieces with metadata."""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize the chunker with configuration."""
        self.config = config or ChunkingConfig()
        self.heading_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
        
    async def chunk_document(
        self,
        file_path: str,
        document_id: int,
        metadata: Optional[Dict] = None
    ) -> List[TextChunk]:
        """
        Chunk a document from file path.
        
        Args:
            file_path: Path to the document file
            document_id: ID of the document
            metadata: Additional metadata for the chunks
            
        Returns:
            List of text chunks with metadata
        """
        try:
            # Extract text based on file type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return await self._chunk_pdf(file_path, document_id, metadata)
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                return await self._chunk_text(text, document_id, metadata)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error chunking document {document_id}: {str(e)}")
            raise
    
    async def _chunk_pdf(
        self,
        file_path: str,
        document_id: int,
        metadata: Optional[Dict] = None
    ) -> List[TextChunk]:
        """Chunk a PDF document."""
        chunks = []
        
        try:
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                
                # Extract headings from the page
                headings = self._extract_headings(text)
                
                # Chunk the page text
                page_chunks = await self._chunk_text(
                    text, 
                    document_id, 
                    {**metadata, 'page_number': page_num + 1} if metadata else {'page_number': page_num + 1}
                )
                
                # Add section information to chunks
                for chunk in page_chunks:
                    # Find the most recent heading before this chunk
                    chunk_section = self._find_section_for_chunk(chunk, headings)
                    if chunk_section:
                        chunk.section = chunk_section
                    
                    chunks.append(chunk)
            
            return chunks
            
        finally:
            if 'doc' in locals():
                doc.close()
    
    async def _chunk_text(
        self,
        text: str,
        document_id: int,
        metadata: Optional[Dict] = None
    ) -> List[TextChunk]:
        """Chunk plain text into smaller pieces."""
        # Normalize text
        text = self._normalize_text(text)
        
        # Detect language if enabled
        language = None
        if self.config.detect_language and text.strip():
            try:
                language = detect(text)
            except Exception as e:
                logger.warning(f"Language detection failed: {str(e)}")
        
        # Split into chunks
        if self.config.split_by_headings:
            chunks = self._split_by_headings(text, document_id, metadata)
        else:
            chunks = self._split_by_length(text, document_id, metadata)
        
        # Add language to metadata
        if language:
            for chunk in chunks:
                if chunk.metadata is None:
                    chunk.metadata = {}
                chunk.metadata['language'] = language
        
        return chunks
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace, normalizing unicode, etc."""
        import unicodedata
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Replace various whitespace with single space
        text = ' '.join(text.split())
        
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        return text.strip()
    
    def _extract_headings(self, text: str) -> List[Tuple[str, int, int]]:
        """Extract headings from text with their positions."""
        headings = []
        for match in self.heading_pattern.finditer(text):
            heading_text = match.group(1).strip()
            if heading_text:
                headings.append((heading_text, match.start(), match.end()))
        return headings
    
    def _find_section_for_chunk(self, chunk: TextChunk, headings: List[Tuple[str, int, int]]) -> Optional[str]:
        """Find the most recent heading before the chunk."""
        if not headings:
            return None
            
        # Find the last heading that starts before the chunk
        for heading_text, start, end in reversed(headings):
            if start < chunk.chunk_index * self.config.chunk_size:
                return heading_text
        return None
    
    def _split_by_headings(self, text: str, document_id: int, metadata: Optional[Dict]) -> List[TextChunk]:
        """Split text into chunks based on headings."""
        # First, split by double newlines as potential section breaks
        sections = re.split(r'\n\s*\n', text)
        chunks = []
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
                
            # If section is small enough, add as is
            if len(section) <= self.config.chunk_size + self.config.chunk_overlap:
                chunks.append(TextChunk(
                    text=section.strip(),
                    document_id=document_id,
                    chunk_index=len(chunks),
                    metadata=metadata
                ))
            else:
                # Otherwise, split by length
                chunks.extend(self._split_by_length(section, document_id, metadata, len(chunks)))
        
        return chunks
    
    def _split_by_length(
        self, 
        text: str, 
        document_id: int, 
        metadata: Optional[Dict],
        start_index: int = 0
    ) -> List[TextChunk]:
        """Split text into chunks of approximately chunk_size with overlap."""
        chunks = []
        start = 0
        chunk_index = start_index
        
        while start < len(text):
            # Find the end of the chunk
            end = start + self.config.chunk_size
            
            # Don't go past the end of the text
            if end >= len(text):
                end = len(text)
            else:
                # Try to split at a sentence boundary
                sentence_end = self._find_sentence_boundary(text, end)
                if sentence_end > start + self.config.min_chunk_size:
                    end = sentence_end
                
                # If we're at the end of a paragraph, include the newline
                if end < len(text) and text[end-1] == '\n':
                    end = end
                # Otherwise, try to split at a word boundary
                elif end < len(text):
                    word_boundary = text.rfind(' ', start, end)
                    if word_boundary > start + self.config.min_chunk_size:
                        end = word_boundary
            
            # Get the chunk text and clean it up
            chunk_text = text[start:end].strip()
            if chunk_text:  # Only add non-empty chunks
                chunks.append(TextChunk(
                    text=chunk_text,
                    document_id=document_id,
                    chunk_index=chunk_index,
                    metadata=metadata.copy() if metadata else None
                ))
                chunk_index += 1
            
            # Move the start position, accounting for overlap
            start = end - self.config.chunk_overlap
            if start <= 0:  # Prevent infinite loop with very small chunks
                start = end
                
            # If we didn't make progress, force advance to prevent infinite loop
            if start <= start - self.config.chunk_overlap:
                start = end
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, position: int) -> int:
        """Find the next sentence boundary after position."""
        # Look for common sentence endings followed by whitespace and capital letter
        sentence_endings = ['. ', '! ', '? ', '\n', '\n\n']
        
        # Find the earliest sentence ending after position
        min_pos = len(text)
        for ending in sentence_endings:
            pos = text.find(ending, position)
            if 0 < pos < min_pos:
                min_pos = pos + len(ending)
        
        # If we found a boundary, return it; otherwise, return the original position
        return min_pos if min_pos < len(text) else position
