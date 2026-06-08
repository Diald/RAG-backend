"""Main FastAPI Application."""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging_config import setup_logging, get_logger

from .schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    RetrievedDocument,
    IngestDocumentsRequest,
    IngestDocumentsResponse,
    EvaluationResponse,
    EvaluationResult,
)
from .evaluation_service import EvaluationService

logger = get_logger(__name__)


# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 RAG Backend API Starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.get_llm_provider()}")
    yield
    logger.info("🛑 RAG Backend API Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Production-grade RAG backend with LlamaIndex and Qdrant",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Setup logging on startup
setup_logging()


# ============================================================================
# Health & Status Endpoints
# ============================================================================


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    from src.retrieval.hybrid_retriever import HybridRetriever

    try:
        retriever = HybridRetriever()
        qdrant_connected = True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        qdrant_connected = False

    return HealthResponse(
        status="healthy" if qdrant_connected else "degraded",
        version=settings.api_version,
        qdrant_connected=qdrant_connected,
    )


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "RAG Backend API",
        "version": settings.api_version,
        "docs": "/docs",
    }


# ============================================================================
# Query Endpoints
# ============================================================================


@app.post("/query", response_model=QueryResponse, tags=["query"])
async def query_rag(request: QueryRequest) -> QueryResponse:
    """Query the RAG system.

    Args:
        request: Query request with question and parameters

    Returns:
        QueryResponse with answer and source documents
    """
    try:
        from src.retrieval.hybrid_retriever import HybridRetriever
        from src.retrieval.llm_service import LLMService

        # Retrieve relevant documents
        retriever = HybridRetriever()
        retrieved = retriever.retrieve(request.query, top_k=request.top_k)

        if not retrieved:
            logger.warning(f"No documents retrieved for query: {request.query}")
            return QueryResponse(
                answer="No relevant documents found to answer your question.",
                retrieved_documents=[],
                model=settings.get_llm_provider(),
                tokens_used=0,
            )

        # Extract context
        context_docs = [doc["text"] for doc in retrieved]

        # Generate response
        llm = LLMService()
        answer = llm.generate(
            prompt=request.query,
            context=context_docs,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Convert retrieved docs to response format
        doc_responses = [
            RetrievedDocument(
                text=doc["text"],
                metadata=doc.get("metadata", {}),
                node_id=doc.get("node_id"),
                score=doc.get("score", 0.0),
                source=doc.get("source", "hybrid"),
            )
            for doc in retrieved
        ]

        # Estimate tokens (rough approximation)
        tokens_used = len(request.query.split()) + len(answer.split())

        logger.info(f"Query processed successfully. Retrieved {len(retrieved)} documents.")

        return QueryResponse(
            answer=answer,
            retrieved_documents=doc_responses,
            model=settings.get_llm_provider(),
            tokens_used=tokens_used,
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/query/stream", tags=["query"])
async def query_rag_stream(request: QueryRequest):
    """Stream a response from the RAG system.

    Args:
        request: Query request

    Yields:
        Response chunks as server-sent events
    """
    from fastapi.responses import StreamingResponse
    from src.retrieval.hybrid_retriever import HybridRetriever
    from src.retrieval.llm_service import LLMService

    async def generate():
        try:
            retriever = HybridRetriever()
            retrieved = retriever.retrieve(request.query, top_k=request.top_k)

            if not retrieved:
                yield "No relevant documents found.\n"
                return

            context_docs = [doc["text"] for doc in retrieved]
            llm = LLMService()

            for chunk in llm.stream_generate(
                prompt=request.query,
                context=context_docs,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error in streaming query: {e}")
            yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ============================================================================
# Ingestion Endpoints
# ============================================================================


@app.post("/ingest", response_model=IngestDocumentsResponse, tags=["ingestion"])
async def ingest_documents(
    request: IngestDocumentsRequest,
    background_tasks: BackgroundTasks,
) -> IngestDocumentsResponse:
    """Ingest documents into the RAG system.

    Args:
        request: Ingestion request with PDF directory or markdown content
        background_tasks: Background task manager

    Returns:
        IngestDocumentsResponse with ingestion statistics
    """
    try:
        from src.ingestion.document_processor import DocumentProcessor

        processor = DocumentProcessor()

        if request.pdf_directory:
            result = processor.ingest_pdfs(request.pdf_directory)
            return IngestDocumentsResponse(
                total_files=result["total_files"],
                total_documents=result["total_documents"],
                total_chunks=result["total_chunks"],
                message=f"Ingested {result['total_files']} PDF files successfully.",
            )

        elif request.markdown_content:
            result = processor.ingest_markdown(
                request.markdown_content,
                metadata=request.metadata,
            )
            return IngestDocumentsResponse(
                total_files=1,
                total_documents=1,
                total_chunks=result["chunk_count"],
                message="Ingested markdown content successfully.",
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Either pdf_directory or markdown_content must be provided.",
            )

    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


# ============================================================================
# Evaluation Endpoints
# ============================================================================


@app.post("/admin/evaluate", response_model=EvaluationResponse, tags=["admin"])
async def evaluate_rag() -> EvaluationResponse:
    """Run Ragas evaluation on the RAG system.

    Returns:
        EvaluationResponse with faithfulness and context precision scores
    """
    try:
        evaluator = EvaluationService()

        # Run synthetic evaluation
        eval_results = evaluator.synthetic_evaluation(
            sample_size=settings.eval_batch_size
        )

        # Format response
        results = [
            EvaluationResult(
                metric=metric,
                score=score,
                details={},
            )
            for metric, score in eval_results.get("scores", {}).items()
        ]

        average_scores = eval_results.get("scores", {})

        return EvaluationResponse(
            total_queries=eval_results.get("total_queries", 0),
            results=results,
            average_scores=average_scores,
        )

    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"Validation error: {exc}")
    return HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.api_port,
        workers=settings.api_workers,
    )
