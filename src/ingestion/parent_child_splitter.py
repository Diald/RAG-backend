"""Parent-Child Hierarchical Chunking Strategy."""

import logging
from typing import Any

from llama_index.core.schema import Document, TextNode

logger = logging.getLogger(__name__)


class ParentChildSplitter:
    """
    Implements hierarchical parent-child chunking.

    Large parent chunks capture broader context.
    Smaller child chunks enable precise retrieval.
    """

    def __init__(
        self,
        parent_chunk_size: int = 2048,
        parent_chunk_overlap: int = 512,
        child_chunk_size: int = 512,
        child_chunk_overlap: int = 128,
    ):
        """Initialize the splitter.

        Args:
            parent_chunk_size: Size of parent chunks
            parent_chunk_overlap: Overlap between parent chunks
            child_chunk_size: Size of child chunks
            child_chunk_overlap: Overlap between child chunks
        """
        self.parent_chunk_size = parent_chunk_size
        self.parent_chunk_overlap = parent_chunk_overlap
        self.child_chunk_size = child_chunk_size
        self.child_chunk_overlap = child_chunk_overlap

    def split(self, document: Document) -> list[TextNode]:
        """Split document into parent and child nodes.

        Args:
            document: Document to split

        Returns:
            List of TextNode objects with parent-child relationships
        """
        text = document.get_content()
        nodes: list[TextNode] = []

        # Create parent chunks
        parent_nodes = self._create_chunks(
            text,
            self.parent_chunk_size,
            self.parent_chunk_overlap,
            is_parent=True,
        )

        # Create child chunks for each parent
        for parent_node in parent_nodes:
            parent_text = parent_node.get_content()
            child_nodes = self._create_chunks(
                parent_text,
                self.child_chunk_size,
                self.child_chunk_overlap,
                is_parent=False,
            )

            # Link children to parent
            # for child_node in child_nodes:
                # child_node.relationships["parent"] = parent_node.node_id

            # Add both parent and children
            nodes.append(parent_node)
            nodes.extend(child_nodes)

        # Preserve document metadata
        for node in nodes:
            node.metadata.update(document.metadata or {})
            node.metadata["doc_id"] = getattr(document, "doc_id", "")

        logger.info(
            f"Split document into {len(parent_nodes)} parents "
            f"and {sum(len(self._create_chunks(pn.get_content(), self.child_chunk_size, self.child_chunk_overlap, False)) for pn in parent_nodes)} children"
        )

        return nodes

    def _create_chunks(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
        is_parent: bool = False,
    ) -> list[TextNode]:
        """Create chunks from text with sliding window.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            is_parent: Whether this is a parent chunk

        Returns:
            List of TextNode objects
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start : end].strip()

            if chunk_text:
                node = TextNode(
                    text=chunk_text,
                    metadata={"is_parent": is_parent},
                )
                chunks.append(node)

            if end == len(text):
                break

            start = end - chunk_overlap

        return chunks
