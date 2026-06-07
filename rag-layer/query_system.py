"""
Query System - Ask questions directly
Import and use this to ask questions

This module provides a simple interface to the integrated RAG pipeline.
It can work with pre-computed embeddings or initialize the full pipeline.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from qdrant_setup import QdrantDB
from hybrid_search import HybridSearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store initialized system
_system = None


def initialize(
    qdrant_storage: str = "./qdrant_storage",
    ingestion_output: str = "./output/ingestion_output_fixed.json",
    use_integration_pipeline: bool = False,
):
    """
    Initialize the query system.

    Can work in two modes:
    1. Simple mode (default): Load pre-computed embeddings from ingestion output
    2. Integration mode: Use full pipeline with automatic ingestion & embedding

    Args:
        qdrant_storage: Path to Qdrant storage
        ingestion_output: Path to ingestion pipeline output JSON
        use_integration_pipeline: If True, use full integration pipeline

    Returns:
        Dictionary with initialized components
    """
    global _system
    if _system is not None:
        logger.info("System already initialized, returning cached instance")
        return _system

    logger.info("[INIT] Initializing query system...")

    if use_integration_pipeline:
        # Use full integration pipeline
        logger.info("Using full RAG integration pipeline...")
        try:
            from integration_pipeline import RAGIntegrationPipeline

            pipeline = RAGIntegrationPipeline(
                qdrant_storage=qdrant_storage,
            )
            result = pipeline.run_full_pipeline()

            if result["status"] != "success":
                logger.warning(f"Pipeline initialization warning: {result}")

            _system = {
                "pipeline": pipeline,
                "db": pipeline.db,
                "search": pipeline.search_engine,
                "mode": "integration",
            }
        except Exception as e:
            logger.error(f"Failed to initialize integration pipeline: {e}")
            logger.info("Falling back to simple mode...")
            _system = _initialize_simple_mode(qdrant_storage, ingestion_output)
    else:
        # Simple mode: work with pre-computed outputs
        _system = _initialize_simple_mode(qdrant_storage, ingestion_output)

    logger.info("[OK] System ready!\n")
    return _system


def _initialize_simple_mode(
    qdrant_storage: str = "./qdrant_storage",
    ingestion_output: str = "./output/ingestion_output_fixed.json",
) -> Dict:
    """Initialize in simple mode using pre-computed outputs."""
    logger.info("Initializing in simple mode...")

    db = QdrantDB(qdrant_storage)
    search = HybridSearchEngine(db.client)

    # Check if ingestion output exists
    if not Path(ingestion_output).exists():
        logger.warning(f"Ingestion output not found at {ingestion_output}")
        logger.info("Please run the ingestion pipeline first")
        return {
            "db": db,
            "search": search,
            "mode": "simple_uninitialized",
        }

    # Load pre-computed chunks
    search.load_chunks_from_file(ingestion_output)
    search.seed_qdrant()
    search.build_bm25_index()

    return {
        "db": db,
        "search": search,
        "mode": "simple",
    }

def ask(
    question: str,
    department: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
    search_type: str = "hybrid",
    print_results: bool = True,
    min_score: float = 0.0,
    use_reranking: bool = True,
    use_query_expansion: bool = False,
):
    """
    Ask a question to the knowledge base with advanced retrieval options.

    Args:
        question: Your question
        department: Filter by department (Engineering, HR, Operations, Support)
        category: Filter by category (Policy, Ticket, Guide)
        top_k: Number of results to return
        search_type: "hybrid", "dense", or "sparse"
        print_results: Whether to print results to console
        min_score: Minimum confidence score threshold (0.0-1.0)
        use_reranking: If True, apply semantic reranking (Phase 2)
        use_query_expansion: If True, expand query with variations (Phase 3)

    Returns:
        List of results with sources and confidence scores
    """
    system = initialize()

    # Check initialization status
    if system.get("mode") == "simple_uninitialized":
        logger.error("System not initialized. Please run ingestion pipeline first.")
        return []

    # Build filters
    filters = {}
    if department:
        filters["department"] = department
    if category:
        filters["category"] = category

    if print_results:
        print(f"QUESTION: {question}")
        if filters:
            print(f"FILTERS: {filters}")
        if min_score > 0:
            print(f"MIN_SCORE: {min_score}")
        print(f"OPTIONS: reranking={use_reranking}, expansion={use_query_expansion}")
        print("\nSEARCHING...\n")

    # Search with all Phase 1, 2, 3 options
    results = system["search"].retrieve_relevant_chunks(
        query=question,
        filters=filters if filters else None,
        search_type=search_type,
        top_k=top_k,
        min_score=min_score,
        use_reranking=use_reranking,
        use_query_expansion=use_query_expansion,
    )

    if print_results:
        # Display results
        if not results:
            print("[NO ANSWER FOUND]")
            print("Cannot find a reliable answer in the corporate knowledge base.\n")
            return results

        print(f"[FOUND {len(results)} RESULTS]\n")

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['document_name']} (v{result['version']})")
            print(f"   Category: {result['category']} | Department: {result['department']}")

            # Show most relevant score
            if 'rerank_score' in result:
                print(f"   Confidence (Reranked): {result['rerank_score']:.1%}")
            else:
                print(f"   Confidence (Hybrid): {result.get('combined_score', 0):.1%}")

            print(f"\n   {result['text'][:150]}...\n")

            # Show all available scores
            scores_str = f"Combined={result.get('combined_score', 0):.3f}"
            if result.get('dense_score') is not None:
                scores_str += f", Dense={result['dense_score']:.3f}"
            if result.get('sparse_score') is not None:
                scores_str += f", Sparse={result['sparse_score']:.3f}"
            if result.get('rerank_score') is not None:
                scores_str += f", Rerank={result['rerank_score']:.3f}"
            if result.get('expansion_count') is not None:
                scores_str += f", Expansion_count={result['expansion_count']}"

            print(f"   Scores: {scores_str}\n")
            print("-" * 70 + "\n")

    return results

if __name__ == "__main__":
    # Example usage
    print("="*70)
    print("ENTERPRISE RAG ASSISTANT - QUERY SYSTEM")
    print("="*70 + "\n")

    # Initialize system
    print("Initializing RAG system...\n")
    system = initialize(use_integration_pipeline=False)

    if system.get("mode") == "simple_uninitialized":
        print("\nPlease run the ingestion pipeline first:")
        print("  python integration_pipeline.py")
        print("\nOr use the full integration pipeline:")
        print("  from rag_layer import RAGIntegrationPipeline")
        print("  pipeline = RAGIntegrationPipeline()")
        print("  result = pipeline.run_full_pipeline()")
    else:
        # Test queries
        print("TEST 1: General question")
        ask("What are the system requirements?")

        print("\n" + "="*70 + "\n")
        print("TEST 2: Filtered by Engineering")
        ask("setup instructions", department="Engineering")

        print("\n" + "="*70 + "\n")
        print("TEST 3: Filtered by Policy category")
        ask("leave and remote work", category="Policy")

        print("\n" + "="*70 + "\n")
        print("TEST 4: No results scenario")
        ask("xyz123 nonsense randomtext")
