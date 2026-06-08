"""Quick query script for testing the RAG system."""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.schemas import QueryRequest
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.llm_service import LLMService
from src.core.logging_config import setup_logging, get_logger

logger = get_logger(__name__)


async def main():
    """Run a sample query against the RAG system."""
    setup_logging()

    query = "What is RAG?"

    logger.info(f"Running query: {query}")

    try:
        # Retrieve
        retriever = HybridRetriever()
        retrieved = retriever.retrieve(query, top_k=3)

        if not retrieved:
            logger.warning("No documents retrieved")
            return

        logger.info(f"Retrieved {len(retrieved)} documents")
        for i, doc in enumerate(retrieved):
            logger.info(f"Doc {i+1}: {doc['text'][:100]}...")

        # Generate response
        context = [doc["text"] for doc in retrieved]
        llm = LLMService()
        answer = llm.generate(
            prompt=query,
            context=context,
        )

        logger.info(f"Answer: {answer}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
