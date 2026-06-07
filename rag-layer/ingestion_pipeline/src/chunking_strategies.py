import uuid
import json
from typing import List, Dict, Literal
from abc import ABC, abstractmethod
import logging

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("sentence-transformers not installed. Install with: pip install sentence-transformers")

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(self, text: str, document_name: str) -> List[Dict]:
        """Split text into chunks and return list of chunk dictionaries."""
        pass


class IntelligentChunking(ChunkingStrategy):
    """Intelligent chunking that respects sentence and paragraph boundaries."""

    def __init__(self, chunk_size: int = 800, min_chunk_size: int = 300):
        self.chunk_size = chunk_size
        self.min_chunk_size = min_chunk_size
        logger.info(f"IntelligentChunking initialized: size={chunk_size}, min={min_chunk_size}")

    def chunk(self, text: str, document_name: str) -> List[Dict]:
        """Split text intelligently by paragraphs and sentences."""
        chunks = []

        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        current_chunk = []
        current_size = 0
        start_pos = 0

        for para in paragraphs:
            para_size = len(para)

            # If adding this paragraph would exceed chunk_size and we have content
            if current_size + para_size > self.chunk_size and current_chunk:
                # Create chunk from accumulated paragraphs
                chunk_text = '\n\n'.join(current_chunk)
                if len(chunk_text) >= self.min_chunk_size:
                    chunk_dict = {
                        "chunk_id": str(uuid.uuid4()),
                        "document_name": document_name,
                        "strategy": "intelligent",
                        "text": chunk_text,
                        "start_pos": start_pos,
                        "end_pos": start_pos + len(chunk_text),
                        "size": len(chunk_text),
                    }
                    chunks.append(chunk_dict)
                    start_pos += len(chunk_text) + 2  # +2 for \n\n

                current_chunk = []
                current_size = 0

            # Add paragraph to current chunk
            current_chunk.append(para)
            current_size += para_size + 2  # +2 for \n\n

        # Add remaining content
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunk_dict = {
                    "chunk_id": str(uuid.uuid4()),
                    "document_name": document_name,
                    "strategy": "intelligent",
                    "text": chunk_text,
                    "start_pos": start_pos,
                    "end_pos": start_pos + len(chunk_text),
                    "size": len(chunk_text),
                }
                chunks.append(chunk_dict)

        logger.info(f"Created {len(chunks)} intelligent chunks from {document_name}")
        return chunks


class FixedSizeChunking(ChunkingStrategy):
    """Fixed-size chunking with overlap (legacy)."""

    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        logger.info(f"FixedSizeChunking initialized: size={chunk_size}, overlap={overlap}")

    def chunk(self, text: str, document_name: str) -> List[Dict]:
        """Split text into fixed-size chunks with overlap - IMPROVED for better context."""
        chunks = []
        step = self.chunk_size - self.overlap

        for i in range(0, len(text), step):
            chunk_text = text[i : i + self.chunk_size]

            if not chunk_text.strip():
                continue

            # Try to break at sentence boundary
            if len(chunk_text) == self.chunk_size:
                # Look for last period, question mark, or exclamation
                for end_char in ['. ', '? ', '! ']:
                    last_pos = chunk_text.rfind(end_char)
                    if last_pos > self.chunk_size * 0.75:  # At least 75% of chunk
                        chunk_text = chunk_text[:last_pos + 1]
                        break

            if len(chunk_text.strip()) < 50:  # Skip very short chunks
                continue

            chunk_dict = {
                "chunk_id": str(uuid.uuid4()),
                "document_name": document_name,
                "strategy": "fixed_size",
                "text": chunk_text,
                "start_pos": i,
                "end_pos": min(i + self.chunk_size, len(text)),
                "size": len(chunk_text),
            }
            chunks.append(chunk_dict)

        logger.info(f"Created {len(chunks)} fixed-size chunks from {document_name}")
        return chunks


class SemanticChunking(ChunkingStrategy):
    """Semantic chunking based on sentence boundaries and structural breaks."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", target_size: int = 500):
        self.model_name = model_name
        self.target_size = target_size
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"SemanticChunking initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            self.model = None

    def chunk(self, text: str, document_name: str) -> List[Dict]:
        """Split text semantically using sentence boundaries and structure."""
        sentences = self._split_into_sentences(text)
        chunks = self._group_sentences_into_chunks(sentences, document_name)

        logger.info(f"Created {len(chunks)} semantic chunks from {document_name}")
        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex and structural breaks."""
        sentences = []

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('---') or line.startswith('###') or line.startswith('##'):
                if sentences:
                    sentences.append('BREAK')
                sentences.append(line)
                sentences.append('BREAK')
            else:
                sentence_parts = [s.strip() for s in line.split('. ') if s.strip()]
                sentences.extend(sentence_parts)

        return [s for s in sentences if s.strip()]

    def _group_sentences_into_chunks(self, sentences: List[str], document_name: str) -> List[Dict]:
        """Group sentences into chunks of target size."""
        chunks = []
        current_chunk = []
        current_size = 0
        start_pos = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            if current_size + sentence_size > self.target_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                if chunk_text.strip():
                    chunk_dict = {
                        "chunk_id": str(uuid.uuid4()),
                        "document_name": document_name,
                        "strategy": "semantic",
                        "text": chunk_text,
                        "start_pos": start_pos,
                        "end_pos": start_pos + len(chunk_text),
                        "size": len(chunk_text),
                    }
                    chunks.append(chunk_dict)

                current_chunk = []
                current_size = 0
                start_pos += len(chunk_text) + 1

            current_chunk.append(sentence)
            current_size += sentence_size + 1

        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if chunk_text.strip():
                chunk_dict = {
                    "chunk_id": str(uuid.uuid4()),
                    "document_name": document_name,
                    "strategy": "semantic",
                    "text": chunk_text,
                    "start_pos": start_pos,
                    "end_pos": start_pos + len(chunk_text),
                    "size": len(chunk_text),
                }
                chunks.append(chunk_dict)

        return chunks


class ChunkingPipeline:
    """Unified pipeline for document chunking with strategy selection."""

    def __init__(self, strategy: Literal["fixed", "semantic", "adaptive", "intelligent"] = "intelligent"):
        if strategy == "intelligent":
            self.strategy = IntelligentChunking(chunk_size=800, min_chunk_size=300)
        elif strategy == "fixed":
            self.strategy = FixedSizeChunking(chunk_size=800, overlap=100)
        elif strategy == "semantic":
            self.strategy = SemanticChunking(target_size=800)
        elif strategy == "adaptive":
            try:
                from adaptive_chunking import AdaptiveChunking
                self.strategy = AdaptiveChunking(max_chunk_size=800)
            except ImportError:
                logger.warning("adaptive_chunking not available, falling back to intelligent")
                self.strategy = IntelligentChunking(chunk_size=800, min_chunk_size=300)
                strategy = "intelligent"
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        self.strategy_type = strategy
        logger.info(f"ChunkingPipeline initialized with strategy: {strategy}")

    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """Process a list of documents and return all chunks."""
        all_chunks = []

        for doc in documents:
            text_content = doc.pop("text_content", "")
            doc_name = doc.get("document_name", "unknown")

            chunks = self.strategy.chunk(text_content, doc_name)

            for chunk in chunks:
                chunk.update(doc)

            all_chunks.extend(chunks)

        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks

    def save_chunks_to_json(self, chunks: List[Dict], output_path: str) -> None:
        """Save chunks to a JSON file."""
        output_data = {
            "metadata": {
                "strategy": self.strategy_type,
                "total_chunks": len(chunks),
            },
            "chunks": chunks,
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(chunks)} chunks to {output_path}")


def main():
    """Example usage."""
    sample_text = """
    This is a guide for system setup and configuration.

    --- Page 1 ---
    Chapter 1: Introduction

    The Engineering department maintains all technical documentation. This guide covers
    the foundational steps needed for new system deployments. Each section builds upon
    the previous one to ensure comprehensive understanding.

    Section 1.1: Prerequisites
    Before starting, ensure you have administrative access. The system requires Python 3.8+
    and PostgreSQL 12.0 or higher. All dependencies are listed in requirements.txt.

    --- Page 2 ---
    Chapter 2: Installation

    Download the latest release from our repository. Extract the archive to your preferred
    location. Run the initialization script to set up the database schema. Verify installation
    by running the test suite. All tests must pass before proceeding to configuration.
    """

    sample_doc = {
        "document_name": "v1_setup_guide",
        "department": "Engineering",
        "category": "Guide",
        "version": "1.0",
        "text_content": sample_text,
    }

    for strategy in ["fixed", "semantic"]:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing {strategy} chunking strategy")
        logger.info(f"{'='*50}")

        pipeline = ChunkingPipeline(strategy=strategy)
        chunks = pipeline.process_documents([sample_doc.copy()])
        pipeline.save_chunks_to_json(chunks, f"chunks_{strategy}.json")


if __name__ == "__main__":
    main()
