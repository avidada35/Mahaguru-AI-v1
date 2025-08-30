"""Utility functions for generating and working with text embeddings."""
import logging
from typing import List, Optional

import numpy as np
from openai import AsyncOpenAI, OpenAIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class EmbeddingError(Exception):
    """Custom exception for embedding-related errors."""
    pass

class EmbeddingService:
    """Service for generating and managing text embeddings."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding service.
        
        Args:
            model: The name of the OpenAI embedding model to use
        """
        self.model = model
        self.dimensions = self._get_embedding_dimensions(model)
    
    def _get_embedding_dimensions(self, model: str) -> int:
        """
        Get the number of dimensions for the specified model.
        
        Args:
            model: The name of the embedding model
            
        Returns:
            Number of dimensions for the model's embeddings
        """
        # Map of model names to their dimensions
        model_dimensions = {
            "text-embedding-3-large": 3072,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536,
        }
        
        return model_dimensions.get(model, 1536)  # Default to 1536 if model not found
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((OpenAIError, Exception)),
    )
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get the embedding for a single piece of text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding
            
        Raises:
            EmbeddingError: If the embedding request fails
        """
        if not text.strip():
            raise ValueError("Cannot embed empty text")
        
        try:
            # Call the OpenAI API to get the embedding
            response = await client.embeddings.create(
                input=text,
                model=self.model,
            )
            
            # Extract the embedding from the response
            embedding = response.data[0].embedding
            
            # Ensure the embedding has the expected dimensions
            if len(embedding) != self.dimensions:
                logger.warning(
                    f"Unexpected embedding dimension: expected {self.dimensions}, "
                    f"got {len(embedding)}"
                )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise EmbeddingError(f"Failed to get embedding: {e}")
    
    async def get_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Get embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embeddings, one for each input text
        """
        if not texts:
            return []
        
        # Filter out empty texts
        non_empty_texts = [text for text in texts if text.strip()]
        if len(non_empty_texts) < len(texts):
            logger.warning("Some empty texts were provided and will be skipped")
        
        embeddings = []
        
        # Process texts in batches
        for i in range(0, len(non_empty_texts), batch_size):
            batch = non_empty_texts[i:i + batch_size]
            
            try:
                # Call the OpenAI API for the current batch
                response = await client.embeddings.create(
                    input=batch,
                    model=self.model,
                )
                
                # Extract embeddings from the response
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(f"Error getting embeddings for batch {i//batch_size}: {e}")
                # For failed batches, try to get embeddings one by one
                for text in batch:
                    try:
                        embedding = await self.get_embedding(text)
                        embeddings.append(embedding)
                    except Exception as inner_e:
                        logger.error(f"Failed to get embedding for text: {inner_e}")
                        # Add a zero vector as a fallback
                        embeddings.append([0.0] * self.dimensions)
        
        # Ensure we return the same number of embeddings as input texts
        result = []
        text_idx = 0
        for text in texts:
            if text.strip():
                if text_idx < len(embeddings):
                    result.append(embeddings[text_idx])
                    text_idx += 1
                else:
                    result.append([0.0] * self.dimensions)
            else:
                result.append([0.0] * self.dimensions)
        
        return result
    
    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate the cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity between the two embeddings (range: -1 to 1)
        """
        if not embedding1 or not embedding2:
            return 0.0
            
        # Convert to numpy arrays
        a = np.array(embedding1)
        b = np.array(embedding2)
        
        # Handle case where one of the vectors is all zeros
        if np.all(a == 0) or np.all(b == 0):
            return 0.0
            
        # Calculate cosine similarity
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    @staticmethod
    def find_most_similar(
        query_embedding: List[float], 
        document_embeddings: List[List[float]],
        k: int = 5
    ) -> List[tuple[int, float]]:
        """
        Find the k most similar document embeddings to the query embedding.
        
        Args:
            query_embedding: The query embedding vector
            document_embeddings: List of document embeddings to search through
            k: Number of results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity (highest first)
        """
        if not query_embedding or not document_embeddings:
            return []
        
        # Convert to numpy arrays for efficient computation
        query_vec = np.array(query_embedding)
        doc_matrix = np.array(document_embeddings)
        
        # Calculate cosine similarities
        norms_query = np.linalg.norm(query_vec)
        norms_docs = np.linalg.norm(doc_matrix, axis=1)
        
        # Handle zero vectors to avoid division by zero
        zero_norm_mask = (norms_docs == 0) | (norms_query == 0)
        similarities = np.zeros(len(document_embeddings))
        
        # Only calculate similarity for non-zero vectors
        valid_indices = ~zero_norm_mask
        if np.any(valid_indices):
            similarities[valid_indices] = np.dot(doc_matrix[valid_indices], query_vec) / (
                norms_docs[valid_indices] * norms_query
            )
        
        # Get indices of top k similarities
        if k > len(similarities):
            k = len(similarities)
            
        top_k_indices = np.argpartition(similarities, -k)[-k:]
        top_k_similarities = similarities[top_k_indices]
        
        # Sort by similarity (highest first)
        sorted_indices = np.argsort(-top_k_similarities)
        result = [
            (int(top_k_indices[i]), float(top_k_similarities[i])) 
            for i in sorted_indices
        ]
        
        return result
