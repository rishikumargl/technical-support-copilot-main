"""
Unit tests for the ingestion pipeline.
"""

import json
import tempfile
from pathlib import Path
import unittest

from document_parser import DocumentParser
from chunking_strategies import FixedSizeChunking, SemanticChunking, ChunkingPipeline


class TestDocumentParser(unittest.TestCase):
    """Test document parsing functionality."""

    def test_metadata_extraction_from_path(self):
        """Test metadata extraction from file paths."""
        parser = DocumentParser(".")

        test_path = Path("data/Engineering/v1_setup_guide.pdf")
        metadata = parser._extract_metadata_from_path(test_path)

        self.assertEqual(metadata["document_name"], "v1_setup_guide")
        self.assertEqual(metadata["department"], "Engineering")
        self.assertIn(metadata["category"], ["Unknown", "Guide"])
        self.assertEqual(metadata["version"], "1")

    def test_department_extraction(self):
        """Test department extraction from path parts."""
        parser = DocumentParser(".")

        parts = ("data", "Engineering", "v1_setup_guide.pdf")
        dept = parser._extract_department(parts)
        self.assertEqual(dept, "Engineering")

        parts = ("data", "HR", "policy.pdf")
        dept = parser._extract_department(parts)
        self.assertEqual(dept, "HR")


class TestFixedSizeChunking(unittest.TestCase):
    """Test fixed-size chunking strategy."""

    def setUp(self):
        self.chunker = FixedSizeChunking(chunk_size=100, overlap=20)

    def test_chunk_size(self):
        """Test that chunks are approximately correct size."""
        text = "A" * 500
        chunks = self.chunker.chunk(text, "test_doc")

        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk["text"]), 100)
            self.assertIn("chunk_id", chunk)
            self.assertEqual(chunk["document_name"], "test_doc")
            self.assertEqual(chunk["strategy"], "fixed_size")

    def test_overlap(self):
        """Test that chunks have proper overlap."""
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 10
        chunks = self.chunker.chunk(text, "test_doc")

        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0]["start_pos"], 0)

        for i in range(1, len(chunks)):
            prev_end = chunks[i-1]["end_pos"]
            curr_start = chunks[i]["start_pos"]
            self.assertGreater(prev_end, curr_start)

    def test_empty_text(self):
        """Test handling of empty or whitespace-only text."""
        chunks = self.chunker.chunk("", "test_doc")
        self.assertEqual(len(chunks), 0)

        chunks = self.chunker.chunk("   \n\n   ", "test_doc")
        self.assertEqual(len(chunks), 0)


class TestSemanticChunking(unittest.TestCase):
    """Test semantic chunking strategy."""

    def setUp(self):
        self.chunker = SemanticChunking(target_size=100)

    def test_semantic_chunks(self):
        """Test that semantic chunks are created."""
        text = "This is a test. This is another sentence. And another one here."
        chunks = self.chunker.chunk(text, "test_doc")

        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertIn("chunk_id", chunk)
            self.assertEqual(chunk["document_name"], "test_doc")
            self.assertEqual(chunk["strategy"], "semantic")
            self.assertGreater(len(chunk["text"]), 0)

    def test_structural_breaks(self):
        """Test that structural breaks are recognized."""
        text = """
        Introduction paragraph.

        --- Page 1 ---

        New section content.
        Another line here.
        """
        chunks = self.chunker.chunk(text, "test_doc")
        self.assertGreater(len(chunks), 0)


class TestChunkingPipeline(unittest.TestCase):
    """Test the complete chunking pipeline."""

    def test_fixed_strategy_pipeline(self):
        """Test pipeline with fixed strategy."""
        pipeline = ChunkingPipeline(strategy="fixed")

        documents = [
            {
                "document_name": "doc1",
                "department": "Engineering",
                "category": "Guide",
                "version": "1.0",
                "text_content": "A" * 1000,
            }
        ]

        chunks = pipeline.process_documents(documents)

        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(chunk["department"], "Engineering")
            self.assertEqual(chunk["document_name"], "doc1")

    def test_semantic_strategy_pipeline(self):
        """Test pipeline with semantic strategy."""
        pipeline = ChunkingPipeline(strategy="semantic")

        documents = [
            {
                "document_name": "doc1",
                "department": "HR",
                "category": "Policy",
                "version": "2.0",
                "text_content": "First sentence. Second sentence. Third sentence.",
            }
        ]

        chunks = pipeline.process_documents(documents)

        self.assertGreater(len(chunks), 0)
        self.assertEqual(len(chunks), len([c for c in chunks if c["version"] == "2.0"]))

    def test_json_output(self):
        """Test saving chunks to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = ChunkingPipeline(strategy="fixed")

            chunks = [
                {
                    "chunk_id": "test-1",
                    "text": "Sample text",
                    "document_name": "doc1",
                    "strategy": "fixed_size",
                    "size": 11,
                }
            ]

            output_path = Path(tmpdir) / "test_output.json"
            pipeline.save_chunks_to_json(chunks, str(output_path))

            self.assertTrue(output_path.exists())

            with open(output_path) as f:
                data = json.load(f)

            self.assertIn("metadata", data)
            self.assertIn("chunks", data)
            self.assertEqual(len(data["chunks"]), 1)


if __name__ == "__main__":
    unittest.main()
