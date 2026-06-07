"""
Adaptive chunking strategy that respects semantic boundaries.
Groups text by paragraphs/sections while maintaining max chunk size.
"""
import uuid
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class AdaptiveChunking:
    """Chunk text by semantic units (paragraphs, sections) while respecting size limits."""

    def __init__(self, max_chunk_size: int = 500, prefer_whole_sections: bool = True):
        """Initialize adaptive chunking.

        Args:
            max_chunk_size: Maximum chunk size in characters
            prefer_whole_sections: If True, keeps sections together even if larger
        """
        self.max_chunk_size = max_chunk_size
        self.prefer_whole_sections = prefer_whole_sections
        logger.info(
            f"AdaptiveChunking initialized: size={max_chunk_size}, "
            f"prefer_sections={prefer_whole_sections}"
        )

    def chunk(self, text: str, document_name: str) -> List[Dict]:
        """Split text into adaptive chunks respecting semantic boundaries.

        Strategy:
        1. Split by double newlines (paragraphs)
        2. Group paragraphs into chunks of max_chunk_size
        3. Prefer keeping sections/paragraphs together
        """
        chunks = []

        # Split into paragraphs (separated by double newlines)
        paragraphs = self._split_into_paragraphs(text)

        current_chunk_paragraphs = []
        current_size = 0
        start_pos = 0

        for para in paragraphs:
            para_size = len(para)

            # If adding this paragraph exceeds max size and we have content
            if current_size + para_size > self.max_chunk_size and current_chunk_paragraphs:
                # Flush current chunk
                chunk_text = '\n\n'.join(current_chunk_paragraphs)
                if chunk_text.strip():
                    chunk_dict = {
                        "chunk_id": str(uuid.uuid4()),
                        "document_name": document_name,
                        "strategy": "adaptive",
                        "text": chunk_text,
                        "start_pos": start_pos,
                        "end_pos": start_pos + len(chunk_text),
                        "size": len(chunk_text),
                    }
                    chunks.append(chunk_dict)

                # Reset for next chunk
                current_chunk_paragraphs = []
                current_size = 0
                start_pos += len(chunk_text) + 2  # +2 for double newline

            # Add paragraph to current chunk
            current_chunk_paragraphs.append(para)
            current_size += para_size + 2  # +2 for joining newlines

        # Flush remaining content
        if current_chunk_paragraphs:
            chunk_text = '\n\n'.join(current_chunk_paragraphs)
            if chunk_text.strip():
                chunk_dict = {
                    "chunk_id": str(uuid.uuid4()),
                    "document_name": document_name,
                    "strategy": "adaptive",
                    "text": chunk_text,
                    "start_pos": start_pos,
                    "end_pos": start_pos + len(chunk_text),
                    "size": len(chunk_text),
                }
                chunks.append(chunk_dict)

        logger.info(f"Created {len(chunks)} adaptive chunks from {document_name}")
        return chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs (separated by double newlines or more)."""
        paragraphs = []

        # Split by double newline or more
        parts = text.split('\n\n')

        for part in parts:
            part = part.strip()
            if part:
                paragraphs.append(part)

        return paragraphs
