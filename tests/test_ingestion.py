"""Tests for ingestion module."""

import pytest


class TestParentChildSplitter:
    """Test suite for ParentChildSplitter."""

    def test_splitter_initialization(self):
        """Test ParentChildSplitter initialization."""
        from src.ingestion.parent_child_splitter import ParentChildSplitter

        splitter = ParentChildSplitter(
            parent_chunk_size=2048,
            child_chunk_size=512,
        )
        assert splitter.parent_chunk_size == 2048
        assert splitter.child_chunk_size == 512

    def test_chunk_creation(self):
        """Test chunk creation."""
        from src.ingestion.parent_child_splitter import ParentChildSplitter
        from llama_index.schema import Document

        splitter = ParentChildSplitter(
            parent_chunk_size=100,
            child_chunk_size=50,
        )

        doc = Document(text="This is a test document. " * 20)
        chunks = splitter.split(doc)

        assert len(chunks) > 0
        # Should have both parent and child chunks
        parent_chunks = [c for c in chunks if c.metadata.get("is_parent")]
        child_chunks = [c for c in chunks if not c.metadata.get("is_parent")]
        assert len(parent_chunks) > 0
        assert len(child_chunks) > 0


class TestDocumentProcessor:
    """Test suite for DocumentProcessor."""

    def test_processor_initialization(self):
        """Test DocumentProcessor initialization."""
        from src.ingestion.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        assert processor is not None
        assert processor.qdrant_client is not None
