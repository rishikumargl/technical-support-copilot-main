#!/usr/bin/env python3
"""
Integration test suite for the complete RAG pipeline.
Tests all components working together.
"""

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported."""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Module Imports")
    logger.info("="*70)

    try:
        from integration_pipeline import RAGIntegrationPipeline, create_rag_pipeline
        logger.info("✓ integration_pipeline imports successful")

        from embedding_service import EmbeddingService, init_embedding_service
        logger.info("✓ embedding_service imports successful")

        from qdrant_setup import QdrantDB
        logger.info("✓ qdrant_setup imports successful")

        from hybrid_search import HybridSearchEngine
        logger.info("✓ hybrid_search imports successful")

        from query_system import ask, initialize
        logger.info("✓ query_system imports successful")

        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_rag_layer_imports():
    """Test that rag_layer package can be imported."""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: RAG Layer Package")
    logger.info("="*70)

    try:
        from rag_layer import (
            RAGIntegrationPipeline,
            create_rag_pipeline,
            EmbeddingService,
            init_embedding_service,
            QdrantDB,
            HybridSearchEngine,
            ask,
            initialize,
        )
        logger.info("✓ rag_layer package imports successful")
        logger.info(f"  - RAGIntegrationPipeline: {RAGIntegrationPipeline}")
        logger.info(f"  - EmbeddingService: {EmbeddingService}")
        logger.info(f"  - QdrantDB: {QdrantDB}")
        logger.info(f"  - ask function: {ask}")
        return True
    except Exception as e:
        logger.error(f"✗ Package import failed: {e}")
        return False


def test_ingestion_pipeline():
    """Test ingestion pipeline."""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Ingestion Pipeline")
    logger.info("="*70)

    try:
        from integration_pipeline import RAGIntegrationPipeline

        # Check data directory exists
        data_dir = Path("rag-layer/ingestion_pipeline/data")
        if not data_dir.exists():
            logger.warning(f"Data directory not found: {data_dir}")
            logger.info("Skipping ingestion pipeline test")
            return None

        logger.info(f"Using data directory: {data_dir}")

        # Try to list documents
        txt_files = list(data_dir.glob("**/*.txt"))
        pdf_files = list(data_dir.glob("**/*.pdf"))
        total_files = len(txt_files) + len(pdf_files)

        logger.info(f"Found {total_files} documents")
        if txt_files:
            logger.info(f"  - {len(txt_files)} .txt files")
        if pdf_files:
            logger.info(f"  - {len(pdf_files)} .pdf files")

        if total_files == 0:
            logger.warning("No documents found in data directory")
            return None

        logger.info("✓ Ingestion pipeline validation successful")
        return True
    except Exception as e:
        logger.error(f"✗ Ingestion pipeline test failed: {e}")
        return False


def test_embedding_service():
    """Test embedding service initialization."""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Embedding Service")
    logger.info("="*70)

    try:
        from embedding_service import EmbeddingService

        logger.info("Initializing embedding service...")
        logger.info("(This will download the model on first run ~150MB)")

        service = EmbeddingService(model_name="all-MiniLM-L6-v2")
        logger.info(f"✓ Model loaded with dimension: {service.dimension}")

        # Test single embedding
        test_text = "This is a test document about system setup."
        embedding = service.embed_text(test_text)
        logger.info(f"✓ Single embedding generated: shape {embedding.shape}")

        # Test batch embedding
        test_texts = [
            "System requirements",
            "Installation guide",
            "Configuration",
        ]
        embeddings = service.embed_batch(test_texts)
        logger.info(f"✓ Batch embeddings generated: {len(embeddings)} embeddings")

        return True
    except Exception as e:
        logger.error(f"✗ Embedding service test failed: {e}")
        return False


def test_qdrant_database():
    """Test Qdrant database setup."""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Qdrant Database")
    logger.info("="*70)

    try:
        from qdrant_setup import QdrantDB

        logger.info("Initializing Qdrant...")
        db = QdrantDB(storage_path="./qdrant_test_storage")

        logger.info("Creating collection...")
        db.create_collection()
        logger.info("✓ Collection created")

        stats = db.get_collection_stats()
        logger.info(f"✓ Database stats: {stats}")

        return True
    except Exception as e:
        logger.error(f"✗ Qdrant database test failed: {e}")
        return False


def test_configuration_loading():
    """Test loading configuration from .env if it exists."""
    logger.info("\n" + "="*70)
    logger.info("TEST 6: Configuration")
    logger.info("="*70)

    try:
        from pathlib import Path

        env_file = Path("rag-layer/.env")
        if env_file.exists():
            logger.info(f"✓ Found .env file at {env_file}")
            with open(env_file) as f:
                lines = f.readlines()
                logger.info(f"  {len(lines)} configuration entries found")
        else:
            logger.info(".env file not found (optional)")

        logger.info("✓ Configuration loading successful")
        return True
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_documentation():
    """Test that documentation files exist."""
    logger.info("\n" + "="*70)
    logger.info("TEST 7: Documentation")
    logger.info("="*70)

    docs = [
        ("INTEGRATION.md", "Integration guide"),
        ("ingestion_pipeline/README.md", "Ingestion pipeline docs"),
        ("ingestion_pipeline/INTEGRATION_GUIDE.md", "Pipeline integration guide"),
    ]

    found = 0
    for doc_file, desc in docs:
        doc_path = Path("rag-layer") / doc_file
        if doc_path.exists():
            logger.info(f"✓ {desc}: {doc_file}")
            found += 1
        else:
            logger.warning(f"✗ {desc} not found: {doc_file}")

    logger.info(f"Found {found}/{len(docs)} documentation files")
    return found > 0


def run_all_tests():
    """Run all integration tests."""
    logger.info("\n" + "="*70)
    logger.info("RAG LAYER INTEGRATION TEST SUITE")
    logger.info("="*70)

    tests = [
        ("Module Imports", test_imports),
        ("RAG Layer Package", test_rag_layer_imports),
        ("Ingestion Pipeline", test_ingestion_pipeline),
        ("Embedding Service", test_embedding_service),
        ("Qdrant Database", test_qdrant_database),
        ("Configuration", test_configuration_loading),
        ("Documentation", test_documentation),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    for test_name, result in results.items():
        status = "✓ PASS" if result is True else "✗ FAIL" if result is False else "⊘ SKIP"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0:
        logger.info("\n✓ All critical tests passed!")
        return True
    else:
        logger.error(f"\n✗ {failed} test(s) failed")
        return False


def print_quick_start():
    """Print quick start instructions."""
    print("\n" + "="*70)
    print("QUICK START GUIDE")
    print("="*70)

    print("""
1. Run the full pipeline:
   python rag-layer/integration_pipeline.py

2. Query the knowledge base:
   python rag-layer/query_system.py

3. Use in your code:
   from rag_layer import RAGIntegrationPipeline

   pipeline = RAGIntegrationPipeline()
   result = pipeline.run_full_pipeline()

   results = pipeline.query("Your question here?")

4. For more information:
   - See INTEGRATION.md for complete documentation
   - See ingestion_pipeline/README.md for pipeline details
   - Check examples/ for code samples
""")


if __name__ == "__main__":
    success = run_all_tests()
    print_quick_start()

    sys.exit(0 if success else 1)
