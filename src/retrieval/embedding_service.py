"""Embedding Service for generating and managing vector embeddings."""

import logging
from typing import Any

from openai import OpenAI

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generate embeddings using OpenAI's text-embedding-3-small model."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.embedding_dim = settings.vector_embedding_dim

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            # Sort by index to maintain order
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]

        except Exception as e:
            logger.error(f"Error generating embeddings batch: {e}")
            raise
