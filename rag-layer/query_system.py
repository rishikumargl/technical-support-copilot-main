"""
Query System - Ask questions directly
Import and use this to ask questions
"""
import json
from qdrant_setup import QdrantDB
from hybrid_search import HybridSearchEngine

# Global variable to store initialized system
_system = None

def initialize():
    """Initialize the system once"""
    global _system
    if _system is not None:
        return _system

    print("[INIT] Initializing system...")
    db = QdrantDB("./qdrant_storage")
    search = HybridSearchEngine(db.client)
    search.load_chunks_from_file("./output/ingestion_output_fixed.json")
    search.seed_qdrant()
    search.build_bm25_index()

    _system = {
        "db": db,
        "search": search
    }
    print("[OK] System ready!\n")
    return _system

def ask(question, department=None, category=None, top_k=5):
    """
    Ask a question to the knowledge base

    Args:
        question (str): Your question
        department (str): Filter by department (Engineering, HR, Operations, Support)
        category (str): Filter by category (Policy, Ticket, Guide)
        top_k (int): Number of results to return

    Returns:
        list: Results with sources and confidence scores
    """
    system = initialize()

    # Build filters
    filters = {}
    if department:
        filters["department"] = department
    if category:
        filters["category"] = category

    print(f"QUESTION: {question}")
    if filters:
        print(f"FILTERS: {filters}")
    print("\nSEARCHING...\n")

    # Search
    results = system["search"].retrieve_relevant_chunks(
        query=question,
        filters=filters if filters else None,
        search_type="hybrid",
        top_k=top_k
    )

    # Display results
    if not results:
        print("[NO ANSWER FOUND]")
        print("Cannot find a reliable answer in the corporate knowledge base.\n")
        return results

    print(f"[FOUND {len(results)} RESULTS]\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['document_name']} (v{result['version']})")
        print(f"   Category: {result['category']} | Department: {result['department']}")
        print(f"   Confidence: {result['combined_score']:.1%}")
        print(f"\n   {result['text'][:150]}...\n")
        print(f"   Scores: Combined={result['combined_score']:.3f}, Dense={result['dense_score']:.3f}, Sparse={result['sparse_score']:.3f}\n")
        print("-" * 70 + "\n")

    return results

if __name__ == "__main__":
    # Example usage
    print("="*70)
    print("ENTERPRISE RAG ASSISTANT - QUERY SYSTEM")
    print("="*70 + "\n")

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
