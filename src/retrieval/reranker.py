"""Lightweight Reranker using BM25 and cosine similarity."""

import logging
from typing import Any

from rank_bm25 import BM25Okapi

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class LightweightReranker:
    """Rerank retrieved results using hybrid scoring."""

    def __init__(self):
        """Initialize reranker."""
        self.bm25_weight = 0.3
        self.vector_weight = 0.7

    def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """Rerank results using BM25 + vector score hybrid approach.

        Args:
            query: Original query text
            results: Retrieved results with 'text' and 'score' fields
            top_k: Number of top results to return

        Returns:
            Reranked results
        """
        if not results:
            return []

        top_k = top_k or settings.reranker_top_k

        # Extract texts for BM25
        texts = [result["text"] for result in results]
        query_tokens = query.lower().split()

        # Initialize BM25
        tokenized_texts = [text.lower().split() for text in texts]
        bm25 = BM25Okapi(tokenized_texts)
        bm25_scores = bm25.get_scores(query_tokens)

        # Normalize scores
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        max_vector = max(r.get("score", 0) for r in results) or 1

        # Hybrid reranking
        reranked = []
        for i, result in enumerate(results):
            bm25_norm = (bm25_scores[i] / max_bm25) if max_bm25 > 0 else 0
            vector_norm = (result.get("score", 0) / max_vector) if max_vector > 0 else 0

            hybrid_score = (
                self.bm25_weight * bm25_norm + self.vector_weight * vector_norm
            )

            reranked.append(
                {
                    **result,
                    "hybrid_score": hybrid_score,
                    "bm25_score": bm25_norm,
                    "vector_score": vector_norm,
                }
            )

        # Sort by hybrid score
        reranked.sort(key=lambda x: x["hybrid_score"], reverse=True)

        logger.debug(f"Reranked {len(reranked)} results, returning top {top_k}")
        return reranked[:top_k]
