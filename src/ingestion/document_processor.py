"""Document Processing Pipeline for RAG Ingestion."""

import logging
from pathlib import Path
from typing import Any

from llama_index.readers.file import PDFReader
from llama_index.core.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.core.config import settings
from src.core.logging_config import get_logger

from .parent_child_splitter import ParentChildSplitter

logger = get_logger(__name__)


class DocumentProcessor:
    """Handles document ingestion, chunking, and embedding upsert to Qdrant."""

    def __init__(self):
        """Initialize document processor with Qdrant client and splitter."""
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.splitter = ParentChildSplitter(
            parent_chunk_size=settings.chunk_size * 2,
            parent_chunk_overlap=settings.chunk_overlap,
            child_chunk_size=settings.chunk_size,
            child_chunk_overlap=settings.chunk_overlap,
        )
        self.pdf_reader = PDFReader()
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Ensure Qdrant collection exists, create if not."""
        try:
            self.qdrant_client.get_collection(settings.qdrant_collection_name)
            logger.info(f"Collection '{settings.qdrant_collection_name}' exists")
        except Exception:
            logger.info(f"Creating collection '{settings.qdrant_collection_name}'")
            self.qdrant_client.create_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=settings.vector_embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Collection created successfully")

    def ingest_pdfs(self, pdf_dir: str | Path) -> dict[str, Any]:
        """Ingest all PDFs from a directory.

        Args:
            pdf_dir: Directory containing PDF files

        Returns:
            Dictionary with ingestion statistics
        """
        pdf_path = Path(pdf_dir)
        pdf_files = list(pdf_path.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return {"total_files": 0, "total_documents": 0, "total_chunks": 0}

        total_documents = 0
        total_chunks = 0

        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            try:
                documents = self.pdf_reader.load_data(file=pdf_file)
                ingested = self._ingest_documents(documents)
                total_documents += len(documents)
                total_chunks += ingested["chunk_count"]
                logger.info(f"Ingested {pdf_file.name}: {ingested['chunk_count']} chunks")
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")

        logger.info(
            f"Ingestion complete: {total_documents} docs, {total_chunks} chunks"
        )
        return {
            "total_files": len(pdf_files),
            "total_documents": total_documents,
            "total_chunks": total_chunks,
        }

    def ingest_markdown(self, markdown_text: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Ingest markdown text as a document.

        Args:
            markdown_text: Markdown content
            metadata: Optional metadata dict

        Returns:
            Dictionary with ingestion statistics
        """
        doc = Document(text=markdown_text, metadata=metadata or {})
        ingested = self._ingest_documents([doc])
        logger.info(f"Ingested markdown: {ingested['chunk_count']} chunks")
        return ingested

    def _ingest_documents(self, documents: list[Document]) -> dict[str, Any]:
        """Process documents through splitting and upserting.

        Args:
            documents: List of documents to ingest

        Returns:
            Statistics about ingestion
        """
        all_nodes = []

        for doc in documents:
            nodes = self.splitter.split(doc)
            all_nodes.extend(nodes)

        # Import here to avoid circular dependency
        from src.retrieval.embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        embeddings = embedding_service.embed_texts(
            [node.get_content() for node in all_nodes]
        )

        # Prepare for upsert
        points = []
        for node, embedding in zip(all_nodes, embeddings):
            points.append(
                {
                    "id": hash(node.get_content()) % (2**63),
                    "vector": embedding,
                    "payload": {
                        "text": node.get_content(),
                        "metadata": node.metadata,
                        "node_id": node.node_id,
                    },
                }
            )

        # Upsert to Qdrant
        try:
            self.qdrant_client.upsert(
                collection_name=settings.qdrant_collection_name,
                points=points,
            )
            logger.info(f"Upserted {len(points)} points to Qdrant")
        except Exception as e:
            logger.error(f"Error upserting to Qdrant: {e}")
            raise

        return {"chunk_count": len(all_nodes)}
