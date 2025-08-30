"""Background task processing for long-running operations."""
import asyncio
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from fastapi import BackgroundTasks
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.utils.document_processor import DocumentProcessor
from app.utils.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

# Type variables for generic function typing
T = TypeVar('T')
P = TypeVar('P', bound=BaseModel)


class BackgroundTaskManager:
    """Manages background tasks for the application."""
    
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, str] = {}
    
    async def process_document_task(self, document_id: int) -> None:
        """
        Process a document in the background.
        
        Args:
            document_id: ID of the document to process
        """
        task_id = f"process_document_{document_id}"
        
        try:
            # Initialize services
            doc_processor = DocumentProcessor()
            embedding_service = EmbeddingService()
            
            # Get database session
            async with AsyncSessionLocal() as db:
                from app.crud import crud_document
                from app.models.document import Document
                
                # Get the document
                document = await crud_document.document.get(db, id=document_id)
                if not document:
                    raise ValueError(f"Document with ID {document_id} not found")
                
                # Update status to processing
                document = await crud_document.document.update_status(
                    db, db_obj=document, status="processing"
                )
                await db.commit()
                
                # Process the document
                success, message = await doc_processor.process_document(document, db)
                
                if success:
                    # Generate embeddings for all chunks
                    chunks = await crud_document.document.get_document_chunks(db, document_id=document_id)
                    
                    # Update status to embedding
                    document = await crud_document.document.update_status(
                        db, db_obj=document, status="embedding"
                    )
                    await db.commit()
                    
                    # Generate embeddings in batches
                    batch_size = 50  # Adjust based on rate limits
                    for i in range(0, len(chunks), batch_size):
                        batch = chunks[i:i + batch_size]
                        texts = [chunk.content for chunk in batch]
                        embeddings = await embedding_service.get_embeddings_batch(texts)
                        
                        # Update chunks with embeddings
                        for chunk, embedding in zip(batch, embeddings):
                            chunk.embedding = embedding
                        
                        # Commit after each batch
                        await db.commit()
                    
                    # Update status to completed
                    document = await crud_document.document.update_status(
                        db, db_obj=document, status="completed"
                    )
                    await db.commit()
                    
                    self.results[task_id] = {
                        "success": True,
                        "message": f"Successfully processed document {document_id}",
                        "chunks_processed": len(chunks)
                    }
                else:
                    raise Exception(f"Document processing failed: {message}")
                    
        except Exception as e:
            error_msg = f"Error processing document {document_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Update document status to failed
            try:
                async with AsyncSessionLocal() as db:
                    from app.crud import crud_document
                    document = await crud_document.document.get(db, id=document_id)
                    if document:
                        await crud_document.document.update_status(
                            db, 
                            db_obj=document, 
                            status="failed",
                            error_message=str(e)[:500]  # Truncate long error messages
                        )
                        await db.commit()
            except Exception as db_error:
                logger.error(f"Error updating document status: {db_error}")
            
            self.errors[task_id] = error_msg
            self.results[task_id] = {
                "success": False,
                "error": str(e)
            }
    
    def add_task(
        self, 
        func: Callable[..., T], 
        *args: Any, 
        **kwargs: Any
    ) -> str:
        """
        Add a background task to be executed.
        
        Args:
            func: The async function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Task ID for tracking status
        """
        # Create a task ID based on function name and timestamp
        import time
        task_id = f"{func.__name__}_{int(time.time())}"
        
        # Create and store the task
        task = asyncio.create_task(self._run_task(task_id, func, *args, **kwargs))
        self.tasks[task_id] = task
        
        return task_id
    
    async def _run_task(
        self, 
        task_id: str, 
        func: Callable[..., T], 
        *args: Any, 
        **kwargs: Any
    ) -> None:
        """
        Run a task and store the result.
        
        Args:
            task_id: ID of the task
            func: The async function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        try:
            result = await func(*args, **kwargs)
            self.results[task_id] = result
        except Exception as e:
            self.errors[task_id] = str(e)
            logger.error(f"Error in background task {task_id}: {e}", exc_info=True)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a background task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Dictionary with task status and result/error if available
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.done():
                if task_id in self.errors:
                    return {
                        "status": "error",
                        "error": self.errors[task_id]
                    }
                return {
                    "status": "completed",
                    "result": self.results.get(task_id)
                }
            return {"status": "running"}
        return {"status": "not_found"}
    
    def schedule_document_processing(self, document_id: int) -> str:
        """
        Schedule a document for background processing.
        
        Args:
            document_id: ID of the document to process
            
        Returns:
            Task ID for tracking status
        """
        return self.add_task(self.process_document_task, document_id)


# Create a singleton instance of the task manager
task_manager = BackgroundTaskManager()


def get_background_tasks() -> BackgroundTaskManager:
    """
    Get the background task manager instance.
    
    Returns:
        BackgroundTaskManager instance
    """
    return task_manager
