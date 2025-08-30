"""Embedding service for generating and managing text embeddings with multiple providers."""
import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Any, Union

import numpy as np
from pydantic import BaseModel, Field, validator, PrivateAttr
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryCallState
)

logger = logging.getLogger(__name__)

class EmbeddingProviderType(str, Enum):
    """Supported embedding providers."""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    JINA = "jina"
    COHERE = "cohere"
    DEFAULT = SENTENCE_TRANSFORMERS

class EmbeddingModelConfig(BaseModel):
    """Configuration for an embedding model."""
    name: str = Field(..., description="Name of the model")
    provider: EmbeddingProviderType = Field(..., description="Provider of the model")
    dimensions: int = Field(..., description="Dimension of the embedding vectors")
    batch_size: int = Field(default=32, description="Batch size for processing texts")
    max_retries: int = Field(default=3, description="Maximum number of retries on failure")
    timeout: int = Field(default=30, description="Timeout in seconds for API calls")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    base_url: Optional[str] = Field(default=None, description="Base URL for the API")
    additional_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific parameters"
    )
    
    class Config:
        extra = "forbid"
        use_enum_values = True

class EmbeddingRequest(BaseModel):
    """Request for generating embeddings."""
    texts: List[str] = Field(..., description="List of texts to embed")
    model: Optional[str] = Field(
        default=None,
        description="Name of the model to use (overrides default)"
    )
    batch_size: Optional[int] = Field(
        default=None,
        description="Batch size for processing (overrides model config)"
    )

class EmbeddingResponse(BaseModel):
    """Response containing generated embeddings."""
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    model: str = Field(..., description="Name of the model used")
    dimensions: int = Field(..., description="Dimension of the embedding vectors")
    total_tokens: Optional[int] = Field(
        default=None,
        description="Total tokens processed (if available)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the request"
    )

class BaseEmbeddingProvider(ABC):
    """Base class for embedding providers."""
    
    def __init__(self, config: EmbeddingModelConfig):
        """Initialize the provider with configuration."""
        self.config = config
        self._client = None
    
    @abstractmethod
    async def initialize(self):
        """Initialize the provider (e.g., load models, create clients)."""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    async def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        pass
    
    async def close(self):
        """Clean up resources (e.g., close clients, unload models)."""
        pass
    
    def __str__(self):
        return f"{self.__class__.__name__}(model={self.config.name}, provider={self.config.provider})"

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider."""
    
    async def initialize(self):
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url or "https://api.openai.com/v1"
            )
        except ImportError:
            raise ImportError(
                "OpenAI client not installed. Install with: pip install openai"
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        from openai import APIError
        
        try:
            response = await self._client.embeddings.create(
                input=texts,
                model=self.config.name,
                **self.config.additional_params
            )
            
            # Sort embeddings by index to maintain order
            sorted_embeddings = sorted(
                response.data,
                key=lambda x: x.index
            )
            return [item.embedding for item in sorted_embeddings]
            
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def get_embedding_dimension(self) -> int:
        # For OpenAI, we can get the dimension from the model name or config
        if self.config.dimensions:
            return self.config.dimensions
        
        # Try to get from model name
        model_lower = self.config.name.lower()
        if "text-embedding-3-" in model_lower:
            # Format: text-embedding-3-{size} or text-embedding-3-{size}-{dim}
            parts = model_lower.split("-")
            if len(parts) >= 5 and parts[4].isdigit():
                return int(parts[4])
            return 1536  # Default for text-embedding-3 models
        elif "text-embedding-" in model_lower:
            return 1536  # Default for older models
        
        # Fallback to config or raise
        if not self.config.dimensions:
            raise ValueError("Could not determine embedding dimension")
        return self.config.dimensions

class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):
    """HuggingFace embedding provider."""
    
    async def initialize(self):
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = SentenceTransformer(
                self.config.name,
                device=device,
                **self.config.additional_params
            )
            
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers torch"
            )
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence-transformers."""
        try:
            # Convert to numpy array and then to list for consistency
            embeddings = self._model.encode(
                texts,
                batch_size=self.config.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def get_embedding_dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()
    
    async def close(self):
        # Clean up GPU memory if using CUDA
        if hasattr(self, '_model'):
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

class EmbeddingService:
    """Service for managing text embeddings with multiple providers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the embedding service.
        
        Args:
            config: Dictionary containing provider configurations
        """
        self._providers: Dict[str, BaseEmbeddingProvider] = {}
        self._default_provider: Optional[str] = None
        self._initialized = False
        
        if config:
            self.configure(config)
    
    def configure(self, config: Dict[str, Any]):
        """Configure the service with provider settings.
        
        Args:
            config: Dictionary with provider configurations
                Example:
                {
                    "default": "huggingface/all-MiniLM-L6-v2",
                    "providers": {
                        "huggingface/all-MiniLM-L6-v2": {
                            "provider": "huggingface",
                            "dimensions": 384,
                            "batch_size": 32
                        },
                        "text-embedding-3-small": {
                            "provider": "openai",
                            "dimensions": 1536,
                            "api_key": "your-api-key"
                        }
                    }
                }
        """
        self._default_provider = config.get("default")
        
        for model_name, model_config in config.get("providers", {}).items():
            self.add_provider(model_name, model_config)
    
    def add_provider(self, model_name: str, config: Dict[str, Any]):
        """Add an embedding provider.
        
        Args:
            model_name: Name of the model
            config: Configuration for the provider
        """
        # Create config object
        provider_config = EmbeddingModelConfig(
            name=model_name,
            **config
        )
        
        # Create provider instance based on type
        provider_type = provider_config.provider
        if provider_type == EmbeddingProviderType.OPENAI:
            provider = OpenAIEmbeddingProvider(provider_config)
        elif provider_type in [
            EmbeddingProviderType.HUGGINGFACE,
            EmbeddingProviderType.SENTENCE_TRANSFORMERS
        ]:
            provider = HuggingFaceEmbeddingProvider(provider_config)
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        # Store provider
        self._providers[model_name] = provider
        
        # Set as default if not set
        if self._default_provider is None:
            self._default_provider = model_name
    
    async def initialize(self):
        """Initialize all providers."""
        if self._initialized:
            return
            
        for provider in self._providers.values():
            await provider.initialize()
        
        self._initialized = True
    
    async def get_embedding_dimension(
        self,
        model: Optional[str] = None
    ) -> int:
        """Get the dimension of embeddings for a model.
        
        Args:
            model: Name of the model (uses default if not specified)
            
        Returns:
            Dimension of the embedding vectors
        """
        provider = await self._get_provider(model)
        return await provider.get_embedding_dimension()
    
    async def embed_texts(
        self,
        texts: List[str],
        model: Optional[str] = None,
        batch_size: Optional[int] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            model: Name of the model to use (uses default if not specified)
            batch_size: Batch size for processing (overrides model config)
            **kwargs: Additional parameters for the provider
            
        Returns:
            EmbeddingResponse containing the embeddings and metadata
        """
        if not texts:
            return EmbeddingResponse(embeddings=[], model="", dimensions=0)
        
        provider = await self._get_provider(model)
        
        # Process in batches
        batch_size = batch_size or provider.config.batch_size
        batches = [
            texts[i:i + batch_size]
            for i in range(0, len(texts), batch_size)
        ]
        
        all_embeddings = []
        
        for batch in batches:
            try:
                embeddings = await provider.embed_texts(batch)
                all_embeddings.extend(embeddings)
            except Exception as e:
                logger.error(f"Error embedding batch: {str(e)}")
                # Optionally: retry with smaller batch size
                if batch_size > 1:
                    logger.info(f"Retrying with smaller batch size: {batch_size//2}")
                    provider.config.batch_size = batch_size // 2
                    return await self.embed_texts(
                        texts, model, batch_size//2, **kwargs
                    )
                raise
        
        return EmbeddingResponse(
            embeddings=all_embeddings,
            model=provider.config.name,
            dimensions=await provider.get_embedding_dimension(),
            total_tokens=sum(len(t.split()) for t in texts),
            metadata={
                "provider": provider.config.provider,
                "batch_size": batch_size,
                "num_batches": len(batches)
            }
        )
    
    async def _get_provider(self, model_name: Optional[str] = None) -> BaseEmbeddingProvider:
        """Get a provider by name, falling back to default."""
        if not self._initialized:
            await self.initialize()
        
        name = model_name or self._default_provider
        if not name:
            raise ValueError("No default provider set and no model specified")
        
        provider = self._providers.get(name)
        if not provider:
            raise ValueError(f"No provider found for model: {name}")
        
        return provider
    
    async def close(self):
        """Clean up resources."""
        for provider in self._providers.values():
            try:
                await provider.close()
            except Exception as e:
                logger.error(f"Error closing provider {provider}: {str(e)}")
        
        self._initialized = False
    
    def __str__(self):
        return (
            f"EmbeddingService(providers={list(self._providers.keys())}, "
            f"default={self._default_provider})"
        )

# Global instance for convenience
_embedding_service = None

async def get_embedding_service(
    config: Optional[Dict[str, Any]] = None
) -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService(config)
        await _embedding_service.initialize()
    elif config is not None:
        # Reconfigure if new config is provided
        _embedding_service.configure(config)
        await _embedding_service.initialize()
    
    return _embedding_service

async def close_embedding_service():
    """Close the global embedding service and release resources."""
    global _embedding_service
    
    if _embedding_service is not None:
        await _embedding_service.close()
        _embedding_service = None
