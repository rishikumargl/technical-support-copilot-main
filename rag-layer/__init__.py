"""
RAG Layer - Complete Retrieval Augmented Generation System

Integrates:
- Document ingestion pipeline
- Embedding service
- Vector database (Qdrant)
- Hybrid search engine

Quick start:
    from rag_layer import RAGIntegrationPipeline

    pipeline = RAGIntegrationPipeline(
        source_dir="documents",
        output_dir="output"
    )

    # Run complete pipeline
    result = pipeline.run_full_pipeline()

    # Query the knowledge base
    results = pipeline.query("What are the system requirements?")
"""

from integration_pipeline import (
    RAGIntegrationPipeline,
    create_rag_pipeline,
)
from embedding_service import EmbeddingService, init_embedding_service
from qdrant_setup import QdrantDB
from hybrid_search import HybridSearchEngine
from query_system import ask, initialize

__version__ = "1.0.0"
__author__ = "Technical Support Copilot Team"

__all__ = [
    # Main integration
    "RAGIntegrationPipeline",
    "create_rag_pipeline",
    # Components
    "EmbeddingService",
    "init_embedding_service",
    "QdrantDB",
    "HybridSearchEngine",
    # Query interface
    "ask",
    "initialize",
]
