"""
Test suite for vector search functionality.
Tests embedding service, Qdrant storage, and hybrid search.
"""
import unittest
import json
import tempfile
import shutil
from pathlib import Path
from qdrant_setup import QdrantDB
from embedding_service import EmbeddingService
from hybrid_search import HybridSearchEngine


class TestEmbeddingService(unittest.TestCase):
    """Test embedding service."""

    @classmethod
    def setUpClass(cls):
        cls.service = EmbeddingService()

    def test_embed_single_text(self):
        """Test embedding a single text."""
        text = "This is a test document about engineering setup."
        embedding = self.service.embed_text(text)
        self.assertEqual(embedding.shape[0], 384)

    def test_embed_batch(self):
        """Test batch embedding."""
        texts = [
            "Engineering setup guide",
            "HR remote work policy",
            "Operations incident response"
        ]
        embeddings = self.service.embed_batch(texts)
        self.assertEqual(len(embeddings), 3)
        self.assertEqual(embeddings[0].shape[0], 384)

    def test_embed_chunks(self):
        """Test embedding chunk objects."""
        chunks = [
            {"text": "First chunk", "chunk_id": "1"},
            {"text": "Second chunk", "chunk_id": "2"}
        ]
        result = self.service.embed_chunks(chunks)
        self.assertEqual(len(result), 2)
        self.assertIn("embedding", result[0])
        self.assertEqual(len(result[0]["embedding"]), 384)

    def test_similarity(self):
        """Test similarity calculation."""
        text1 = "engineering setup"
        text2 = "engineering setup"
        text3 = "hr policy"

        e1 = self.service.embed_text(text1)
        e2 = self.service.embed_text(text2)
        e3 = self.service.embed_text(text3)

        sim_same = self.service.similarity(e1, e2)
        sim_diff = self.service.similarity(e1, e3)

        self.assertGreater(sim_same, sim_diff)


class TestQdrantDB(unittest.TestCase):
    """Test Qdrant database operations."""

    def setUp(self):
        """Create temporary Qdrant storage for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db = QdrantDB(self.temp_dir)
        self.db.create_collection()

    def tearDown(self):
        """Clean up temporary storage."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_collection(self):
        """Test collection creation."""
        stats = self.db.get_collection_stats()
        self.assertEqual(stats["collection"], "enterprise_chunks")
        self.assertEqual(stats["vector_size"], 384)

    def test_collection_exists(self):
        """Test checking collection existence."""
        exists = self.db.client.collection_exists("enterprise_chunks")
        self.assertTrue(exists)

    def test_delete_collection(self):
        """Test collection deletion."""
        self.db.delete_collection()
        exists = self.db.client.collection_exists("enterprise_chunks")
        self.assertFalse(exists)


class TestHybridSearch(unittest.TestCase):
    """Test hybrid search functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data and search engine."""
        # Create sample chunks (simplified version of Peer 1 output)
        cls.sample_chunks = [
            {
                "chunk_id": "chunk_1",
                "document_name": "setup_guide",
                "department": "Engineering",
                "category": "Guide",
                "version": "1",
                "text": "System prerequisites include Python 3.8, PostgreSQL 12, and Node.js 16. You need at least 8GB RAM and 50GB disk space."
            },
            {
                "chunk_id": "chunk_2",
                "document_name": "setup_guide",
                "department": "Engineering",
                "category": "Guide",
                "version": "1",
                "text": "Installation steps: clone repository, install dependencies, initialize database, run tests, and configure environment variables."
            },
            {
                "chunk_id": "chunk_3",
                "document_name": "remote_policy",
                "department": "HR",
                "category": "Policy",
                "version": "2",
                "text": "Remote work policy: employees can work from home up to 3 days per week. Core hours are 10am to 3pm in company timezone."
            }
        ]

    def setUp(self):
        """Create temporary Qdrant for each test."""
        self.temp_dir = tempfile.mkdtemp()
        db = QdrantDB(self.temp_dir)
        db.create_collection()
        self.search_engine = HybridSearchEngine(db.client)
        self.search_engine.chunks_cache = self.sample_chunks
        self.search_engine.seed_qdrant()
        self.search_engine.build_bm25_index()

    def tearDown(self):
        """Clean up temporary storage."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bm25_ranking(self):
        """Test BM25 ranking."""
        results = self.search_engine.bm25_score("Python PostgreSQL installation", top_k=2)
        self.assertGreater(len(results), 0)

    def test_dense_search(self):
        """Test dense vector search."""
        results = self.search_engine.dense_search("system requirements", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("dense_score", results[0])

    def test_hybrid_search(self):
        """Test hybrid search."""
        results = self.search_engine.hybrid_search("what are system requirements", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("combined_score", results[0])
        self.assertIn("dense_score", results[0])
        self.assertIn("sparse_score", results[0])

    def test_department_filter(self):
        """Test metadata filtering by department."""
        results = self.search_engine.hybrid_search(
            "system requirements",
            filters={"department": "Engineering"},
            top_k=5
        )
        for result in results:
            self.assertEqual(result["department"], "Engineering")

    def test_category_filter(self):
        """Test metadata filtering by category."""
        results = self.search_engine.hybrid_search(
            "policy work remote",
            filters={"category": "Policy"},
            top_k=5
        )
        for result in results:
            self.assertEqual(result["category"], "Policy")

    def test_retrieve_relevant_chunks(self):
        """Test main retrieval function."""
        results = self.search_engine.retrieve_relevant_chunks(
            "setup Python environment",
            search_type="hybrid",
            top_k=3
        )
        self.assertGreater(len(results), 0)
        self.assertIn("chunk_id", results[0])
        self.assertIn("text", results[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
