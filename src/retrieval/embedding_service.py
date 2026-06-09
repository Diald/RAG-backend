"""Embedding Service for generating and managing vector embeddings."""

import logging

from google import genai

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generate embeddings using Google's embedding-001 model."""

    def __init__(self):
        """Initialize Google client."""
        genai.configure(api_key=settings.google_api_key)
        self.model = settings.google_embedding_model
        logger.info(f"Initialized Google embeddings with model: {self.model}")

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=f"models/{self.model}",
                content=text,
            )
            return result["embedding"]

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
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=f"models/{self.model}",
                    content=text,
                )
                embeddings.append(result["embedding"])
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings batch: {e}")
            raise
