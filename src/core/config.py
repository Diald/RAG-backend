"""Application configuration using Pydantic v2 Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    environment: Literal["development", "production", "testing"] = "development"
    debug: bool = False
    api_port: int = 8000
    api_workers: int = 4
    api_title: str = "RAG Backend API"
    api_version: str = "0.1.0"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Groq Configuration (optional)
    groq_api_key: str | None = None
    groq_model: str = "mixtral-8x7b-32768"

    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "rag_documents"

    # Vector Store Configuration
    vector_embedding_dim: int = 1536
    top_k_retrieval: int = 5
    reranker_top_k: int = 3
    chunk_size: int = 1024
    chunk_overlap: int = 128

    # Logging Configuration
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Evaluation Configuration
    eval_batch_size: int = 5
    eval_dataset_threshold: int = 10

    # CORS Configuration
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    def get_llm_provider(self) -> Literal["openai", "groq"]:
        """Determine which LLM provider to use."""
        return "groq" if self.groq_api_key else "openai"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export for convenience
settings = get_settings()
