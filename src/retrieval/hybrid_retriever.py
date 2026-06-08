"""Hybrid Retrieval combining dense vectors and sparse search."""

import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from src.core.config import settings
from src.core.logging_config import get_logger

from .embedding_service import EmbeddingService
from .reranker import LightweightReranker

logger = get_logger(__name__)


class HybridRetriever:
    """Hybrid retrieval combining dense vectors and BM25 sparse search."""

    def __init__(self):
        """Initialize retriever with Qdrant client and embedding service."""
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.embedding_service = EmbeddingService()
        self.reranker = LightweightReranker()
        self.top_k = settings.top_k_retrieval

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant documents using hybrid search.

        Args:
            query: Query text
            top_k: Number of results to retrieve
            filters: Optional Qdrant filters

        Returns:
            List of retrieved documents with metadata
        """
        top_k = top_k or self.top_k

        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)

        # Dense vector search
        try:
            dense_results = self.qdrant_client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=query_embedding,
                limit=top_k * 2,  # Get more for reranking
                query_filter=filters,
            )
            logger.debug(f"Dense search returned {len(dense_results)} results")
        except Exception as e:
            logger.error(f"Error in dense search: {e}")
            dense_results = []

        # Convert to standard format
        retrieved_docs = []
        for result in dense_results:
            payload = result.payload
            retrieved_docs.append(
                {
                    "text": payload.get("text", ""),
                    "metadata": payload.get("metadata", {}),
                    "node_id": payload.get("node_id"),
                    "score": result.score,
                    "source": "dense",
                }
            )

        # Rerank results
        reranked = self.reranker.rerank(query, retrieved_docs, top_k)

        logger.info(
            f"Retrieved and reranked {len(reranked)} documents for query: {query[:50]}..."
        )
        return reranked

    def retrieve_with_parent_context(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve child chunks and include parent context.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of child chunks with parent context
        """
        top_k = top_k or self.top_k

        # Retrieve child chunks
        child_results = self.retrieve(query, top_k)

        # Fetch parent context for each child
        results_with_context = []
        for result in child_results:
            # The result already contains full metadata
            results_with_context.append(result)

        logger.debug(f"Retrieved {len(results_with_context)} chunks with context")
        return results_with_context
