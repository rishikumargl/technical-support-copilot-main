"""
Interactive Question Answering System
Ask questions about the enterprise documents with HuggingFace inference!
"""
import json
from qdrant_setup import QdrantDB
from hybrid_search import HybridSearchEngine
from inference_service import InferenceService

print("\n" + "="*70)
print("ENTERPRISE RAG ASSISTANT - QUESTION ANSWERING SYSTEM")
print("="*70)
print("\nInitializing system...")

# Initialize
db = QdrantDB("./qdrant_storage")
search = HybridSearchEngine(db.client)
search.load_chunks_from_file("./output/ingestion_output_fixed.json")
search.seed_qdrant()
search.build_bm25_index()

# Initialize inference
inference = InferenceService()

print("[OK] System initialized and ready!")
print("\nDatabase Status:")
stats = db.get_collection_stats()
print(f"  - Collection: {stats['collection']}")
print(f"  - Total chunks: {stats['points_count']}")
print(f"  - Vector dimension: {stats['vector_size']}")

print("\n" + "="*70)
print("ASK YOUR QUESTIONS")
print("="*70)
print("\nUsage:")
print("  1. Type your question and press Enter")
print("  2. Use special commands:")
print("     - 'dept:Engineering' to filter by department")
print("     - 'cat:Policy' to filter by category")
print("     - 'top:10' to get top 10 results")
print("     - 'quit' to exit")
print("\nExamples:")
print("  - 'What are the system requirements?'")
print("  - 'What is the leave policy? dept:HR'")
print("  - 'deployment process cat:Guide top:5'")
print("\n" + "="*70)

def parse_query(input_text):
    """Parse user input to extract question, filters, and top_k"""
    parts = input_text.split()
    question_parts = []
    filters = {}
    top_k = 5

    for part in parts:
        if part.startswith("dept:"):
            filters["department"] = part.split(":")[1]
        elif part.startswith("cat:"):
            filters["category"] = part.split(":")[1]
        elif part.startswith("top:"):
            try:
                top_k = int(part.split(":")[1])
            except:
                pass
        else:
            question_parts.append(part)

    question = " ".join(question_parts)
    return question, filters, top_k

def display_results(results, question, filters, top_k, inference):
    """Display search results and generate AI response"""
    if not results:
        print("\n[NO RESULTS FOUND]")
        print("Cannot find a reliable answer in the corporate knowledge base.")
        return

    print(f"\n[FOUND {len(results)} RESULTS]")
    if filters:
        print(f"Filters applied: {filters}")
    print()

    for i, result in enumerate(results, 1):
        print(f"{i}. SOURCE: {result['document_name']} (v{result['version']})")
        print(f"   Category: {result['category']}")
        print(f"   Department: {result['department']}")
        print(f"   Confidence: {result['combined_score']:.1%}")
        print(f"\n   TEXT:")
        # Print first 200 chars of chunk
        text_preview = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
        print(f"   {text_preview}")
        print(f"\n   Score Breakdown:")
        print(f"     - Combined Score: {result['combined_score']:.3f}")
        print(f"     - Dense (Semantic): {result['dense_score']:.3f}")
        print(f"     - Sparse (Keyword): {result['sparse_score']:.3f}")
        print()

    # Generate AI response using HuggingFace inference
    print("[GENERATING ANSWER WITH AI...]")
    answer_result = inference.answer_with_sources(question, results)

    print("\n" + "="*70)
    print("AI RESPONSE:")
    print("="*70)
    print(answer_result['answer'])
    print(f"\nConfidence: {answer_result['confidence']:.1%}")
    print(f"Model: {answer_result['model']}")
    print("="*70)

# Main loop
try:
    while True:
        user_input = input("\nYOU: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\nGoodbye!")
            break

        # Parse the query
        question, filters, top_k = parse_query(user_input)

        if not question:
            print("Please enter a question.")
            continue

        print("\n[SEARCHING...]")

        # Search
        results = search.retrieve_relevant_chunks(
            query=question,
            filters=filters if filters else None,
            search_type="hybrid",
            top_k=top_k
        )

        # Display results and generate AI response
        display_results(results, question, filters, top_k, inference)

except KeyboardInterrupt:
    print("\n\nGoodbye!")
except Exception as e:
    print(f"\nError: {str(e)}")
    print("Please try again.")

print("="*70)
print("System shutdown.")
