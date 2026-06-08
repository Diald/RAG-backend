"""Sample ingestion script for populating the RAG system."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.document_processor import DocumentProcessor
from src.core.config import settings
from src.core.logging_config import setup_logging, get_logger

logger = get_logger(__name__)


def main():
    """Run ingestion pipeline."""
    setup_logging()

    logger.info(f"Starting ingestion with settings: {settings.environment}")

    processor = DocumentProcessor()

    # Ingest sample markdown
    sample_markdown = """
    # RAG System Documentation

    ## What is RAG?
    Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval
    with generative models to provide more accurate and contextual responses.

    ## How it works
    1. User submits a query
    2. The system retrieves relevant documents
    3. Retrieved documents are used as context for the LLM
    4. The LLM generates a response based on the context

    ## Benefits
    - More accurate responses
    - Reduced hallucinations
    - Up-to-date information
    - Source attribution
    """

    logger.info("Ingesting sample markdown...")
    result = processor.ingest_markdown(
        sample_markdown,
        metadata={"title": "RAG Documentation", "source": "sample"},
    )

    logger.info(f"Ingestion complete: {result}")

    # Try to ingest PDFs if directory exists
    pdf_dir = Path(__file__).parent / "data"
    if pdf_dir.exists():
        logger.info(f"Ingesting PDFs from {pdf_dir}...")
        pdf_result = processor.ingest_pdfs(pdf_dir)
        logger.info(f"PDF ingestion: {pdf_result}")


if __name__ == "__main__":
    main()
