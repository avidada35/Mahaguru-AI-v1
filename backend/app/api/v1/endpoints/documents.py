"""Document management endpoints for uploading, retrieving, and managing documents."""
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, List, Optional

from fastapi import (
    APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, 
    Request, status
)
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core import background_tasks
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.document import DocumentStatus
from app.schemas.document import (
    Document as DocumentSchema,
    DocumentChunk as DocumentChunkSchema,
    DocumentCreate,
    DocumentUpdate,
    DocumentChunkCreate,
    DocumentChunkResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentSearchResponse,
    DocumentSearchResult,
    DocumentStatus as DocumentStatusSchema,
)
from app.utils import file_utils
from app.utils.embeddings import EmbeddingService, EmbeddingError

router = APIRouter()
logger = logging.getLogger(__name__)

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

class DocumentMetadata(BaseModel):
    """Metadata for document upload."""
    title: str = Field(..., description="Title of the document")
    description: Optional[str] = Field(None, description="Description of the document")
    tags: List[str] = Field(default_factory=list, description="List of tags for the document")
    source: Optional[str] = Field(None, description="Source of the document")
    source_url: Optional[HttpUrl] = Field(None, description="URL of the document source")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    id: int
    title: str
    file_name: str
    file_size: int
    status: str
    task_id: Optional[str] = None


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    *,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: str = Form("{}"),
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> DocumentResponse:
    """
    Upload a document for processing and indexing.
    
    Supported formats: PDF, TXT
    Max file size: 10MB
    """
    try:
        # Parse metadata
        try:
            meta = json.loads(metadata)
            doc_meta = DocumentMetadata(**meta)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid metadata format. Must be a valid JSON string.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid metadata: {str(e)}",
            )
        
        # Validate file type
        if not file_utils.is_valid_file_type(file.filename, ["pdf", "txt"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and TXT files are supported.",
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes",
            )
        
        # Generate a unique filename
        file_ext = file_utils.get_file_extension(file.filename)
        file_hash = file_utils.get_file_hash(file_content)
        safe_filename = f"{file_hash}.{file_ext}"
        
        # Ensure upload directory exists
        upload_dir = file_utils.ensure_upload_dir()
        file_path = upload_dir / safe_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Create document in database
        doc_in = DocumentCreate(
            title=doc_meta.title or file.filename,
            description=doc_meta.description,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=len(file_content),
            file_type=file_ext,
            file_hash=file_hash,
            metadata={
                "tags": doc_meta.tags,
                "source": doc_meta.source,
                "source_url": str(doc_meta.source_url) if doc_meta.source_url else None,
            },
            owner_id=current_user.id,
            status=DocumentStatus.UPLOADED.value,
        )
        
        document = await crud.document.create(db, obj_in=doc_in)
        
        # Schedule document processing in background
        task_id = background_tasks.task_manager.schedule_document_processing(document.id)
        
        return DocumentResponse(
            id=document.id,
            title=document.title,
            file_name=document.file_name,
            file_size=document.file_size,
            status=document.status,
            task_id=task_id,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )
    finally:
        await file.close()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> DocumentResponse:
    """
    Get document by ID.
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check if user has permission to access this document
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return document


@router.get("/{document_id}/chunks", response_model=List[DocumentChunkResponse])
async def get_document_chunks(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> List[DocumentChunkResponse]:
    """
    Get chunks for a document.
    """
    # Verify document exists and user has access
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get paginated chunks
    chunks = await crud.document_chunk.get_multi_by_document(
        db, document_id=document_id, skip=skip, limit=limit
    )
    
    return chunks


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Download a document file.
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server",
        )
    
    return FileResponse(
        document.file_path,
        filename=document.file_name,
        media_type="application/octet-stream",
    )


@router.delete("/{document_id}", response_model=schemas.Msg)
async def delete_document(
    document_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> schemas.Msg:
    """
    Delete a document.
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Delete the file if it exists
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            logger.error(f"Error deleting file {document.file_path}: {str(e)}")
    
    # Delete the document and its chunks from the database
    await crud.document.remove(db, id=document_id)
    
    return {"msg": "Document deleted successfully"}


@router.get("/{document_id}/status", response_model=DocumentStatusSchema)
async def get_document_status(
    document_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> DocumentStatusSchema:
    """
    Get the processing status of a document.
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return {
        "status": document.status,
        "error": document.error_message,
        "processed_at": document.processed_at,
    }


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> List[DocumentResponse]:
    """
    List all documents for the current user.
    """
    if current_user.is_superuser:
        documents = await crud.document.get_multi(db, skip=skip, limit=limit)
    else:
        documents = await crud.document.get_multi_by_owner(
            db, owner_id=current_user.id, skip=skip, limit=limit
        )
    
    return documents
