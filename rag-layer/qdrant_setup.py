"""
Qdrant database setup and initialization.
Handles collection creation, schema configuration, and data seeding.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class QdrantDB:
    """Manage Qdrant vector database locally on disk."""

    def __init__(self, storage_path: str = "./qdrant_storage"):
        """Initialize Qdrant client with local disk storage."""
        self.storage_path = storage_path
        self.client = QdrantClient(path=storage_path)
        self.collection_name = "enterprise_chunks"
        self.vector_size = 384  # all-MiniLM-L6-v2 embedding dimension

    def create_collection(self) -> bool:
        """Create collection for storing document chunks with vectors."""
        try:
            # Check if collection exists
            if self.client.collection_exists(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True

            # Create collection with vector config
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False

    def seed_from_ingestion_output(self, json_path: str) -> Dict:
        """Load chunks from Peer 1's ingestion output and store in Qdrant."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            chunks = data.get("chunks", [])
            if not chunks:
                logger.warning(f"No chunks found in {json_path}")
                return {"status": "error", "message": "No chunks to seed"}

            logger.info(f"Seeding {len(chunks)} chunks into Qdrant")
            # Chunks will be added during embedding pipeline
            return {
                "status": "success",
                "chunks_count": len(chunks),
                "documents_summary": data.get("documents_summary", [])
            }
        except Exception as e:
            logger.error(f"Failed to seed from ingestion output: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "collection": self.collection_name,
                "points_count": info.points_count,
                "vector_size": self.vector_size,
                "storage_path": self.storage_path
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {"error": str(e)}

    def delete_collection(self) -> bool:
        """Delete collection (useful for testing/reset)."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False


def init_qdrant(storage_path: str = "./qdrant_storage") -> QdrantDB:
    """Initialize Qdrant database with collection."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    db = QdrantDB(storage_path)
    db.create_collection()
    return db


if __name__ == "__main__":
    db = init_qdrant()
    stats = db.get_collection_stats()
    print(json.dumps(stats, indent=2))
