"""Ingestion module for document processing and embedding generation."""

from .document_processor import DocumentProcessor
from .parent_child_splitter import ParentChildSplitter

__all__ = ["DocumentProcessor", "ParentChildSplitter"]
