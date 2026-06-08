"""Tests for retrieval module."""

import pytest


class TestHybridRetriever:
    """Test suite for HybridRetriever."""

    def test_retriever_initialization(self):
        """Test HybridRetriever initialization."""
        from src.retrieval.hybrid_retriever import HybridRetriever

        retriever = HybridRetriever()
        assert retriever is not None
        assert retriever.top_k > 0

    def test_embedding_service_initialization(self):
        """Test EmbeddingService initialization."""
        from src.retrieval.embedding_service import EmbeddingService

        service = EmbeddingService()
        assert service is not None
        assert service.model is not None


class TestReranker:
    """Test suite for Reranker."""

    def test_reranker_initialization(self):
        """Test LightweightReranker initialization."""
        from src.retrieval.reranker import LightweightReranker

        reranker = LightweightReranker()
        assert reranker is not None

    def test_rerank_empty_results(self):
        """Test reranker with empty results."""
        from src.retrieval.reranker import LightweightReranker

        reranker = LightweightReranker()
        results = reranker.rerank("test query", [])
        assert results == []

    def test_rerank_results(self):
        """Test reranker with sample results."""
        from src.retrieval.reranker import LightweightReranker

        reranker = LightweightReranker()
        results = [
            {"text": "Python is great", "score": 0.9},
            {"text": "Java is fast", "score": 0.7},
        ]
        reranked = reranker.rerank("Python programming", results)
        assert len(reranked) <= 2
        assert "hybrid_score" in reranked[0]
