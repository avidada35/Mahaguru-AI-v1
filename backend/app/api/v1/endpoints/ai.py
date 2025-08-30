from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.core.config import settings
from app.core.security import get_current_active_user
from app.services.retrieval_service import HybridRetriever, SearchResult
from app.services.embedding_service import get_embedding_service, EmbeddingService
from app.services.chunking_service import DocumentChunker, ChunkingConfig
from app.db.session import async_session

router = APIRouter(prefix="/ai", tags=["ai"])

# Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_RESULTS = 50
RERANK_TOP_K = 10

class SearchRequest(BaseModel):
    """Schema for document search request."""
    query: str = Field(..., description="The search query")
    document_ids: Optional[List[int]] = Field(
        None,
        description="Filter by specific document IDs"
    )
    top_k: int = Field(
        MAX_RESULTS,
        gt=0,
        le=100,
        description="Maximum number of results to return"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional filters for the search"
    )
    use_hybrid: bool = Field(
        True,
        description="Whether to use hybrid search (dense + sparse)"
    )
    use_reranker: bool = Field(
        True,
        description="Whether to use reranking for better results"
    )

class SearchResultItem(BaseModel):
    """Schema for a single search result."""
    chunk_id: int
    document_id: int
    score: float
    text: str
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    """Schema for search response."""
    results: List[SearchResultItem]
    total: int
    model: str
    query: str

class AnswerRequest(SearchRequest):
    """Schema for answer generation request."""
    max_tokens: int = Field(
        1000,
        gt=0,
        le=4000,
        description="Maximum number of tokens in the generated answer"
    )
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for answer generation"
    )

class AnswerResponse(BaseModel):
    """Schema for answer generation response."""
    answer: str
    sources: List[SearchResultItem]
    model: str
    tokens_used: int


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: models.User = Depends(get_current_active_user),
) -> SearchResponse:
    """
    Search through documents using hybrid retrieval (dense + sparse).
    
    This endpoint performs a semantic search across the user's documents,
    returning the most relevant chunks based on the query.
    """
    # Get embedding service
    embedding_service = await get_embedding_service()
    
    # Get database session
    async with async_session() as db:
        # Initialize retriever
        retriever = HybridRetriever(
            db_session=db,
            embedding_service=embedding_service,
            config={
                "top_k": request.top_k,
                "rerank_top_k": RERANK_TOP_K,
                "use_reranker": request.use_reranker
            }
        )
        
        # Prepare filters
        filters = request.filters or {}
        if request.document_ids:
            filters["document_id"] = request.document_ids
        
        # Perform search
        results = await retriever.search(
            query=request.query,
            user_id=current_user.id,
            filters=filters,
            use_hybrid=request.use_hybrid,
            use_reranker=request.use_reranker
        )
        
        # Convert to response model
        search_results = [
            SearchResultItem(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                score=result.score,
                text=result.text,
                metadata=result.metadata
            )
            for result in results
        ]
        
        return SearchResponse(
            results=search_results,
            total=len(search_results),
            model=embedding_service.get_model_name(),
            query=request.query
        )

@router.post("/answer", response_model=AnswerResponse)
async def generate_answer(
    request: AnswerRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_active_user),
) -> AnswerResponse:
    """
    Generate an answer to a question based on the user's documents.
    
    This endpoint first retrieves relevant document chunks and then uses
    them as context to generate a natural language answer.
    """
    # Get embedding service
    embedding_service = await get_embedding_service()
    
    # Get database session
    async with async_session() as db:
        # Initialize retriever
        retriever = HybridRetriever(
            db_session=db,
            embedding_service=embedding_service,
            config={
                "top_k": request.top_k,
                "rerank_top_k": RERANK_TOP_K,
                "use_reranker": request.use_reranker
            }
        )
        
        # Prepare filters
        filters = request.filters or {}
        if request.document_ids:
            filters["document_id"] = request.document_ids
        
        # Perform search to get relevant chunks
        results = await retriever.search(
            query=request.query,
            user_id=current_user.id,
            filters=filters,
            use_hybrid=request.use_hybrid,
            use_reranker=request.use_reranker
        )
        
        # Format context from top results
        context = "\n\n".join(
            f"[Document {i+1}, Score: {result.score:.2f}]\n{result.text}"
            for i, result in enumerate(results[:RERANK_TOP_K])
        )
        
        # Generate answer using the context
        # In a real implementation, this would call an LLM
        answer = await _generate_answer_with_llm(
            query=request.query,
            context=context,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Convert results to response model
        source_results = [
            SearchResultItem(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                score=result.score,
                text=result.text,
                metadata=result.metadata
            )
            for result in results[:RERANK_TOP_K]
        ]
        
        return AnswerResponse(
            answer=answer,
            sources=source_results,
            model=embedding_service.get_model_name(),
            tokens_used=len(answer.split())  # Approximate
        )

async def _generate_answer_with_llm(
    query: str,
    context: str,
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> str:
    """
    Generate an answer using an LLM with the given context.
    
    This is a placeholder implementation that simulates an LLM call.
    In a real implementation, this would call an actual LLM API.
    """
    # This is a simplified example - in a real implementation, you would:
    # 1. Call an LLM API (e.g., OpenAI, Anthropic, etc.)
    # 2. Format the prompt with the query and context
    # 3. Parse and return the response
    
    prompt = f"""You are an AI assistant that answers questions based on the provided context.
    
    Context:
    {context}
    
    Question: {query}
    
    Answer the question based on the context above. If the context doesn't contain
    enough information to answer the question, say "I don't have enough information
    to answer this question based on the provided documents."
    """
    
    # Simulate LLM call
    # In a real implementation, you would make an API call here
    await asyncio.sleep(0.1)  # Simulate network delay
    
    # Return a simple response for demonstration
    return (
        "Based on the provided documents, here's the answer to your question:\n\n"
        f"{query}\n\n"
        "This is a placeholder response. In a real implementation, this would be "
        "generated by an LLM based on the retrieved document chunks."
    )


async def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text using the embedding service.
    
    Args:
        text: The text to embed
        
    Returns:
        A list of floats representing the embedding vector
    """
    embedding_service = await get_embedding_service()
    result = await embedding_service.embed_texts([text])
    return result.embeddings[0] if result.embeddings else []


@router.post("/documents/{document_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_document(
    *,
    document_id: int,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Initiate processing of a document (extract text, generate embeddings, etc.).
    
    This endpoint starts an asynchronous task to process the document.
    """
    async with async_session() as db:
        # Check if document exists and user has access
        document = await db.get(models.Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Add background task to process the document
        background_tasks.add_task(
            _process_document_task,
            document_id=document_id,
            file_path=document.file_path,
            user_id=current_user.id
        )
        
        return {
            "status": "processing_started",
            "document_id": document_id,
            "message": "Document processing has been queued"
        }

async def _process_document_task(document_id: int, file_path: str, user_id: int):
    """Background task to process a document."""
    from app.services.document_processor import DocumentProcessor
    from app.services.embedding_service import get_embedding_service
    
    try:
        async with async_session() as db:
            # Get services
            embedding_service = await get_embedding_service()
            processor = DocumentProcessor(db, embedding_service)
            
            # Process the document
            await processor.process_document(
                document_id=document_id,
                file_path=file_path,
                user_id=user_id
            )
            
            logger.info(f"Successfully processed document {document_id}")
            
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
        # TODO: Update document status to indicate failure
