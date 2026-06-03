"""
Enterprise RAG Document Ingestion Pipeline

Complete document parsing and chunking system for RAG applications.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from document_parser import DocumentParser
from chunking_strategies import (
    FixedSizeChunking,
    SemanticChunking,
    ChunkingPipeline,
)
from ingestion_pipeline import IngestionPipeline

__version__ = "1.0.0"
__author__ = "Technical Support Copilot Team"
__all__ = [
    "DocumentParser",
    "FixedSizeChunking",
    "SemanticChunking",
    "ChunkingPipeline",
    "IngestionPipeline",
]
