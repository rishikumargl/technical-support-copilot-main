"""
Embedding service for converting text chunks to vectors.
Uses sentence-transformers all-MiniLM-L6-v2 for local, fast embeddings.
"""
import logging
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings for text chunks using local transformer model."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", hf_token: str = None):
        """Initialize embedding model (downloads on first use).

        Args:
            model_name: Model identifier (e.g., "all-MiniLM-L6-v2")
            hf_token: Not used (kept for backward compatibility)
        """
        logger.info(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")

    def embed_text(self, text: str) -> np.ndarray:
        """Convert single text to embedding vector."""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed text: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Convert multiple texts to embeddings (batch mode for efficiency)."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to embed batch: {str(e)}")
            raise

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Embed text from list of chunk dictionaries."""
        try:
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embed_batch(texts)

            # Add embedding to each chunk
            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding.tolist()

            logger.info(f"Embedded {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to embed chunks: {str(e)}")
            raise

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        return float(np.dot(embedding1, embedding2) /
                    (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))


def init_embedding_service(model_name: str = "all-MiniLM-L6-v2", hf_token: str = None) -> EmbeddingService:
    """Initialize and return embedding service.

    Args:
        model_name: Model to load (default: all-MiniLM-L6-v2)
        hf_token: Not used (kept for backward compatibility)
    """
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    return EmbeddingService(model_name, hf_token)
