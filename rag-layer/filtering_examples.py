"""
Real-world examples of metadata filtering.
Copy and run to test different filtering scenarios.
"""
import json
from qdrant_setup import QdrantDB
from hybrid_search import HybridSearchEngine


def example_1_department_filtering():
    """Example 1: Filter by department (Engineering only)"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Department Filtering")
    print("="*60)

    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")

    # Query: Setup instructions
    query = "What are the system prerequisites?"

    print(f"\nQuery: '{query}'")
    print(f"Filter: department='Engineering'")

    results = search.retrieve_relevant_chunks(
        query=query,
        filters={"department": "Engineering"},
        search_type="hybrid",
        top_k=3
    )

    print(f"\nResults ({len(results)} chunks):")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. [{result['document_name']}]")
        print(f"     Department: {result['department']}")
        print(f"     Category: {result['category']}")
        print(f"     Score: {result['combined_score']:.3f}")
        print(f"     Text: {result['text'][:80]}...")


def example_2_category_filtering():
    """Example 2: Filter by category (Policies only)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Category Filtering")
    print("="*60)

    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")

    query = "What is the policy?"

    print(f"\nQuery: '{query}'")
    print(f"Filter: category='Policy'")

    results = search.retrieve_relevant_chunks(
        query=query,
        filters={"category": "Policy"},
        search_type="hybrid",
        top_k=3
    )

    print(f"\nResults ({len(results)} chunks):")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. [{result['document_name']}]")
        print(f"     Department: {result['department']}")
        print(f"     Category: {result['category']}")
        print(f"     Score: {result['combined_score']:.3f}")
        print(f"     Text: {result['text'][:80]}...")


def example_3_combined_filtering():
    """Example 3: Multiple filters (AND logic)"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Combined Filtering (AND logic)")
    print("="*60)

    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")

    query = "setup and policies"

    print(f"\nQuery: '{query}'")
    print(f"Filters:")
    print(f"  - department='Engineering'")
    print(f"  - category='Guide'")

    results = search.retrieve_relevant_chunks(
        query=query,
        filters={
            "department": "Engineering",
            "category": "Guide"
        },
        search_type="hybrid",
        top_k=3
    )

    print(f"\nResults ({len(results)} chunks):")
    if not results:
        print("  No results found matching ALL criteria")
    else:
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. [{result['document_name']}]")
            print(f"     Department: {result['department']}")
            print(f"     Category: {result['category']}")
            print(f"     Score: {result['combined_score']:.3f}")
            print(f"     Text: {result['text'][:80]}...")


def example_4_no_filtering():
    """Example 4: No filters (search across ALL documents)"""
    print("\n" + "="*60)
    print("EXAMPLE 4: No Filtering (Global Search)")
    print("="*60)

    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")

    query = "system requirements"

    print(f"\nQuery: '{query}'")
    print(f"Filters: None (search all documents)")

    results = search.retrieve_relevant_chunks(
        query=query,
        filters=None,  # ← No filtering
        search_type="hybrid",
        top_k=3
    )

    print(f"\nResults ({len(results)} chunks):")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. [{result['document_name']}]")
        print(f"     Department: {result['department']}")
        print(f"     Category: {result['category']}")
        print(f"     Score: {result['combined_score']:.3f}")
        print(f"     Text: {result['text'][:80]}...")


def example_5_role_based_access():
    """Example 5: Role-based access control (RBAC)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Role-Based Access Control (RBAC)")
    print("="*60)

    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")

    # Define role permissions
    ROLE_PERMISSIONS = {
        "engineer": {"department": "Engineering"},
        "hr_manager": {"department": "HR"},
        "operations": {"department": "Operations"},
        "support": {"department": "Support"}
    }

    # Test different users
    test_cases = [
        ("engineer", "How do I set up the environment?"),
        ("hr_manager", "What is the leave policy?"),
        ("engineer", "deployment process")
    ]

    for user_role, user_query in test_cases:
        filters = ROLE_PERMISSIONS[user_role]
        print(f"\n{'─'*60}")
        print(f"User Role: {user_role.upper()}")
        print(f"Query: '{user_query}'")
        print(f"Filter Applied: {filters}")

        results = search.retrieve_relevant_chunks(
            query=user_query,
            filters=filters,
            search_type="hybrid",
            top_k=2
        )

        print(f"Results: {len(results)} chunks found")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['document_name']} (dept: {result['department']})")


def example_6_version_filtering():
    """Example 6: Version-based filtering"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Version-Based Filtering")
    print("="*60)

    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")

    query = "setup guide"

    print(f"\nQuery: '{query}'")
    print(f"Filter: version='2' (only latest version)")

    results = search.retrieve_relevant_chunks(
        query=query,
        filters={"version": "2"},
        search_type="hybrid",
        top_k=3
    )

    print(f"\nResults ({len(results)} chunks):")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. [{result['document_name']} v{result['version']}]")
        print(f"     Department: {result['department']}")
        print(f"     Score: {result['combined_score']:.3f}")


def example_7_filter_comparison():
    """Example 7: Compare results with and without filters"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Filter Impact Comparison")
    print("="*60)

    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")

    query = "setup installation configuration"

    # Search without filters
    print(f"\nQuery: '{query}'")
    print(f"\n--- WITHOUT FILTERS ---")
    results_all = search.retrieve_relevant_chunks(
        query=query,
        filters=None,
        search_type="hybrid",
        top_k=5
    )
    print(f"Results: {len(results_all)} chunks")
    departments = set(r['department'] for r in results_all)
    print(f"Departments: {', '.join(departments)}")

    # Search with filter
    print(f"\n--- WITH FILTER (Engineering only) ---")
    results_filtered = search.retrieve_relevant_chunks(
        query=query,
        filters={"department": "Engineering"},
        search_type="hybrid",
        top_k=5
    )
    print(f"Results: {len(results_filtered)} chunks")
    departments_filtered = set(r['department'] for r in results_filtered)
    print(f"Departments: {', '.join(departments_filtered)}")

    print(f"\nFilter Impact:")
    print(f"  Before: {len(results_all)} results (all departments)")
    print(f"  After: {len(results_filtered)} results (Engineering only)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("METADATA FILTERING EXAMPLES")
    print("="*60)
    print("\nMake sure you've run: python vector_db_init.py")
    print("And have Peer 1's data in ./output/")

    try:
        # Run all examples
        example_1_department_filtering()
        example_2_category_filtering()
        example_3_combined_filtering()
        example_4_no_filtering()
        example_5_role_based_access()
        example_6_version_filtering()
        example_7_filter_comparison()

        print("\n" + "="*60)
        print("✓ All examples completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Have you run: python vector_db_init.py?")
        print("2. Is ./output/ingestion_output_fixed.json available?")
        print("3. Do you have ./qdrant_storage/ created?")
