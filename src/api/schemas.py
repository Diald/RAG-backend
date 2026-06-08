"""Pydantic schemas for API request/response validation."""

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for /query endpoint."""

    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    use_reranker: bool = Field(default=True, description="Whether to use reranking")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=1024, ge=100, le=4096, description="Max tokens to generate")


class RetrievedDocument(BaseModel):
    """Model for a retrieved document."""

    text: str = Field(..., description="Document text")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    node_id: str | None = Field(default=None, description="Node ID")
    score: float = Field(..., description="Retrieval score")
    source: str = Field(default="hybrid", description="Retrieval source")


class QueryResponse(BaseModel):
    """Response model for /query endpoint."""

    answer: str = Field(..., description="Generated answer")
    retrieved_documents: list[RetrievedDocument] = Field(
        ..., description="Source documents used"
    )
    model: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Approximate tokens used")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    qdrant_connected: bool = Field(..., description="Qdrant connection status")


class IngestDocumentsRequest(BaseModel):
    """Request for document ingestion endpoint."""

    pdf_directory: str | None = Field(default=None, description="Directory with PDFs")
    markdown_content: str | None = Field(default=None, description="Markdown text to ingest")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class IngestDocumentsResponse(BaseModel):
    """Response from document ingestion."""

    total_files: int = Field(..., description="Total files processed")
    total_documents: int = Field(..., description="Total documents ingested")
    total_chunks: int = Field(..., description="Total chunks created")
    message: str = Field(..., description="Status message")


class EvaluationResult(BaseModel):
    """Individual evaluation metric result."""

    metric: str = Field(..., description="Metric name")
    score: float = Field(..., description="Score (0-1)")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional details")


class EvaluationResponse(BaseModel):
    """Response from evaluation endpoint."""

    total_queries: int = Field(..., description="Total queries evaluated")
    results: list[EvaluationResult] = Field(..., description="Evaluation results")
    average_scores: dict[str, float] = Field(..., description="Average scores by metric")
