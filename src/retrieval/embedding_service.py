"""Embedding Service for generating and managing vector embeddings."""

from google import genai

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generate embeddings using Gemini embedding models."""

    def __init__(self):
        """Initialize Google GenAI client."""
        self.client = genai.Client(
            api_key=settings.google_api_key
        )

        self.model = settings.google_embedding_model

        logger.info(
            f"Initialized Google embeddings with model: {self.model}"
        )

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
            )

            return response.embeddings[0].values

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=texts,
            )

            return [
                embedding.values
                for embedding in response.embeddings
            ]

        except Exception as e:
            logger.error(f"Error generating embeddings batch: {e}")
            raise