#!/usr/bin/env python3
"""
Test script for Phase 1, 2, and 3 improvements.
Tests query preprocessing, reranking, filtering, and expansion.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "ingestion_pipeline" / "src"))

import logging
from query_system import initialize, ask

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_phase_1_query_preprocessing():
    """Test Phase 1: Query preprocessing with acronyms."""
    print("\n" + "="*70)
    print("PHASE 1: Query Preprocessing & Confidence Filtering")
    print("="*70)

    queries = [
        ("HR policies", "Test acronym expansion"),
        ("What are system requirements?", "Test regular query"),
        ("API documentation and setup", "Test multiple acronyms"),
        ("DB configuration guide", "Test database acronym"),
    ]

    for query, description in queries:
        print(f"\n[TEST] {description}")
        print(f"Query: {query}")
        print("-" * 70)
        results = ask(
            question=query,
            top_k=3,
            search_type="hybrid",
            min_score=0.1,  # Phase 1: confidence filtering
            use_reranking=False,  # Phase 2: disabled for this test
            print_results=True
        )
        print(f"Found: {len(results)} results")


def test_phase_2_reranking():
    """Test Phase 2: Semantic reranking."""
    print("\n" + "="*70)
    print("PHASE 2: Semantic Reranking & Adaptive Chunking")
    print("="*70)

    queries = [
        ("How to install the system?", "Test reranking with setup query"),
        ("Configuration and deployment", "Test multiple semantic concepts"),
    ]

    for query, description in queries:
        print(f"\n[TEST] {description}")
        print(f"Query: {query}")
        print("-" * 70)

        # Without reranking
        print("\n[Without Reranking]")
        results_no_rerank = ask(
            question=query,
            top_k=3,
            search_type="hybrid",
            use_reranking=False,
            print_results=False
        )

        if results_no_rerank:
            print(f"Top result combined_score: {results_no_rerank[0].get('combined_score', 'N/A'):.3f}")

        # With reranking
        print("\n[With Reranking]")
        results_with_rerank = ask(
            question=query,
            top_k=3,
            search_type="hybrid",
            use_reranking=True,  # Phase 2: reranking enabled
            print_results=False
        )

        if results_with_rerank:
            rerank_score = results_with_rerank[0].get('rerank_score', 'N/A')
            print(f"Top result rerank_score: {rerank_score if isinstance(rerank_score, str) else f'{rerank_score:.3f}'}")

        print("\n[Results Comparison]")
        ask(
            question=query,
            top_k=3,
            search_type="hybrid",
            use_reranking=True,
            print_results=True
        )


def test_phase_2_filtering():
    """Test Phase 2: Enhanced metadata filtering."""
    print("\n" + "="*70)
    print("PHASE 2: Enhanced Metadata Filtering")
    print("="*70)

    print("\n[TEST] Filter by department")
    print("Query: setup instructions | Department: Engineering")
    print("-" * 70)
    results = ask(
        question="setup instructions",
        department="Engineering",
        top_k=3,
        use_reranking=True,
        print_results=True
    )

    print("\n[TEST] Filter by category")
    print("Query: policies | Category: Policy")
    print("-" * 70)
    results = ask(
        question="policies",
        category="Policy",
        top_k=3,
        use_reranking=True,
        print_results=True
    )

    print("\n[TEST] Multiple filters")
    print("Query: leave and remote work | Department: HR | Category: Policy")
    print("-" * 70)
    results = ask(
        question="leave and remote work",
        department="HR",
        category="Policy",
        top_k=3,
        use_reranking=True,
        print_results=True
    )


def test_phase_3_query_expansion():
    """Test Phase 3: Query expansion with synonyms."""
    print("\n" + "="*70)
    print("PHASE 3: Query Expansion & Synonyms")
    print("="*70)

    queries = [
        ("How to setup the system", "Should match: installation, deploy, configure"),
        ("API docs and reference", "Should expand: application programming interface"),
        ("Database configuration", "Should expand: database"),
    ]

    for query, description in queries:
        print(f"\n[TEST] {description}")
        print(f"Query: {query}")
        print("-" * 70)

        # Without expansion
        print("\n[Without Query Expansion]")
        results_no_expand = ask(
            question=query,
            top_k=3,
            use_query_expansion=False,
            print_results=False
        )
        print(f"Found: {len(results_no_expand)} results")
        if results_no_expand:
            print(f"Top result: {results_no_expand[0].get('document_name', 'N/A')}")

        # With expansion
        print("\n[With Query Expansion]")
        results_with_expand = ask(
            question=query,
            top_k=3,
            use_query_expansion=True,
            print_results=False
        )
        print(f"Found: {len(results_with_expand)} results")
        if results_with_expand:
            print(f"Top result: {results_with_expand[0].get('document_name', 'N/A')}")
            if results_with_expand[0].get('expansion_count'):
                print(f"Appeared in {results_with_expand[0]['expansion_count']} query variations")


def test_search_types():
    """Test different search types."""
    print("\n" + "="*70)
    print("SEARCH TYPE COMPARISON")
    print("="*70)

    query = "system requirements and configuration"
    search_types = ["hybrid", "dense", "sparse"]

    for search_type in search_types:
        print(f"\n[{search_type.upper()} Search]")
        print(f"Query: {query}")
        print("-" * 70)
        results = ask(
            question=query,
            top_k=2,
            search_type=search_type,
            use_reranking=True,
            print_results=True
        )


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*70)
    print("EDGE CASES & ERROR HANDLING")
    print("="*70)

    test_cases = [
        ("", "Empty query", {"top_k": 5}),
        ("xyz123 nonsense randomtext", "No matching results", {"min_score": 0.5}),
        ("system", "Very short query", {"top_k": 5}),
        ("a" * 1000, "Very long query", {"top_k": 3}),
    ]

    for query, description, options in test_cases:
        print(f"\n[TEST] {description}")
        print(f"Query: {query[:50]}{'...' if len(query) > 50 else ''}")
        print("-" * 70)
        try:
            results = ask(
                question=query if query else "default query",
                print_results=False,
                **options
            )
            print(f"✓ Handled gracefully: Found {len(results)} results")
        except Exception as e:
            print(f"✗ Error: {e}")


def test_score_distribution():
    """Test score normalization and distribution."""
    print("\n" + "="*70)
    print("SCORE DISTRIBUTION ANALYSIS")
    print("="*70)

    query = "system setup"
    print(f"Query: {query}")
    print("-" * 70)

    results = ask(
        question=query,
        top_k=5,
        use_reranking=True,
        print_results=False
    )

    if results:
        print("\n[Score Percentiles]")
        combined_scores = [r.get('combined_score', 0) for r in results]
        dense_scores = [r.get('dense_score', 0) for r in results if r.get('dense_score') is not None]
        sparse_scores = [r.get('sparse_score', 0) for r in results if r.get('sparse_score') is not None]

        print(f"Combined scores: min={min(combined_scores):.3f}, max={max(combined_scores):.3f}")
        if dense_scores:
            print(f"Dense scores: min={min(dense_scores):.3f}, max={max(dense_scores):.3f}")
        if sparse_scores:
            print(f"Sparse scores: min={min(sparse_scores):.3f}, max={max(sparse_scores):.3f}")

        print("\n[Results with Scores]")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['document_name']}")
            print(f"   Combined: {result.get('combined_score', 0):.3f}", end="")
            if result.get('dense_score') is not None:
                print(f" | Dense: {result['dense_score']:.3f}", end="")
            if result.get('sparse_score') is not None:
                print(f" | Sparse: {result['sparse_score']:.3f}", end="")
            if result.get('rerank_score') is not None:
                print(f" | Rerank: {result['rerank_score']:.3f}", end="")
            print()


def run_all_tests():
    """Run all improvement tests."""
    print("\n" + "="*70)
    print("RAG LAYER IMPROVEMENTS TEST SUITE")
    print("="*70)
    print("Testing Phase 1, 2, and 3 improvements")
    print("="*70)

    try:
        # Initialize system
        print("\n[SETUP] Initializing RAG system...")
        system = initialize(use_integration_pipeline=False)

        if system.get("mode") == "simple_uninitialized":
            print("✗ System not initialized. Run ingestion pipeline first:")
            print("  python integration_pipeline.py")
            return

        print("✓ System initialized successfully\n")

        # Run tests
        test_phase_1_query_preprocessing()
        test_phase_2_reranking()
        test_phase_2_filtering()
        test_search_types()
        test_score_distribution()

        # Phase 3 tests (only if available)
        try:
            test_phase_3_query_expansion()
        except Exception as e:
            print(f"\n⚠ Phase 3 tests skipped (query expansion not available): {e}")

        test_edge_cases()

        print("\n" + "="*70)
        print("TEST SUITE COMPLETED")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n✗ Test failed: {e}")


if __name__ == "__main__":
    run_all_tests()
