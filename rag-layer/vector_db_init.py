"""
Complete initialization script for vector database.
Loads Peer 1's chunks, embeds them, and seeds Qdrant.
"""
import json
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_setup import QdrantDB
from embedding_service import EmbeddingService
from hybrid_search import HybridSearchEngine

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def init_vector_database(
    ingestion_json_path: str = "./output/ingestion_output_fixed.json",
    qdrant_storage_path: str = "./qdrant_storage"
) -> dict:
    """
    Complete pipeline to initialize vector database:
    1. Set up Qdrant locally
    2. Load chunks from Peer 1
    3. Embed chunks
    4. Seed Qdrant
    5. Build BM25 index
    """

    result = {"status": "pending", "steps": []}

    # Step 1: Initialize Qdrant
    try:
        logger.info("Step 1: Initializing Qdrant database...")
        db = QdrantDB(qdrant_storage_path)
        db.create_collection()
        result["steps"].append({"step": "qdrant_init", "status": "success"})
        logger.info("[OK] Qdrant initialized")
    except Exception as e:
        logger.error(f"[FAIL] Qdrant init failed: {str(e)}")
        result["steps"].append({"step": "qdrant_init", "status": "error", "error": str(e)})
        return {"status": "error", "steps": result["steps"]}

    # Step 2: Load chunks from Peer 1
    try:
        logger.info("Step 2: Loading chunks from Peer 1 ingestion output...")
        if not Path(ingestion_json_path).exists():
            raise FileNotFoundError(f"Ingestion output not found: {ingestion_json_path}")

        with open(ingestion_json_path, 'r') as f:
            ingestion_data = json.load(f)

        chunks = ingestion_data.get("chunks", [])
        if not chunks:
            raise ValueError("No chunks found in ingestion output")

        logger.info(f"[OK] Loaded {len(chunks)} chunks")
        result["steps"].append({
            "step": "load_chunks",
            "status": "success",
            "chunks_count": len(chunks)
        })
    except Exception as e:
        logger.error(f"[FAIL] Load chunks failed: {str(e)}")
        result["steps"].append({"step": "load_chunks", "status": "error", "error": str(e)})
        return {"status": "error", "steps": result["steps"]}

    # Step 3: Initialize Hybrid Search (loads chunks, embeds, seeds Qdrant)
    try:
        logger.info("Step 3: Initializing hybrid search engine...")
        hf_token = os.environ.get("HF_TOKEN")
        search_engine = HybridSearchEngine(db.client, hf_token=hf_token)
        search_engine.chunks_cache = chunks

        logger.info("Step 4: Embedding chunks and seeding Qdrant...")
        points_seeded = search_engine.seed_qdrant()

        logger.info("Step 5: Building BM25 index...")
        search_engine.build_bm25_index()

        result["steps"].append({
            "step": "embedding_and_seeding",
            "status": "success",
            "points_seeded": points_seeded
        })
        result["steps"].append({
            "step": "bm25_index",
            "status": "success"
        })
        logger.info(f"[OK] Seeded {points_seeded} points into Qdrant")
        logger.info("[OK] BM25 index built")
    except Exception as e:
        logger.error(f"[FAIL] Hybrid search init failed: {str(e)}")
        result["steps"].append({
            "step": "hybrid_search_init",
            "status": "error",
            "error": str(e)
        })
        return {"status": "error", "steps": result["steps"]}

    # Step 6: Verify with test query
    try:
        logger.info("Step 6: Running verification queries...")
        test_queries = [
            "What are the system prerequisites?",
            "What is the remote work policy?",
            "How do I set up the engineering environment?"
        ]

        verification_results = []
        for test_query in test_queries:
            results = search_engine.retrieve_relevant_chunks(
                test_query,
                filters=None,
                search_type="hybrid",
                top_k=3
            )
            verification_results.append({
                "query": test_query,
                "results_count": len(results)
            })

        result["steps"].append({
            "step": "verification",
            "status": "success",
            "test_results": verification_results
        })
        logger.info("[OK] Verification queries successful")
    except Exception as e:
        logger.error(f"[FAIL] Verification failed: {str(e)}")
        result["steps"].append({
            "step": "verification",
            "status": "error",
            "error": str(e)
        })

    # Final status
    result["status"] = "success"
    stats = db.get_collection_stats()
    result["database_stats"] = stats

    return result


def print_results(result: dict):
    """Pretty print initialization results."""
    print("\n" + "="*60)
    print("VECTOR DATABASE INITIALIZATION RESULTS")
    print("="*60)

    print(f"\nStatus: {result['status'].upper()}")

    print("\nSteps:")
    for step in result.get("steps", []):
        status_mark = "[OK]" if step["status"] == "success" else "[FAILED]"
        print(f"  {status_mark} {step['step']}: {step['status']}")
        if step.get("chunks_count"):
            print(f"     -> Loaded {step['chunks_count']} chunks")
        if step.get("points_seeded"):
            print(f"     -> Seeded {step['points_seeded']} points")
        if step.get("error"):
            print(f"     -> Error: {step['error']}")

    if "database_stats" in result:
        stats = result["database_stats"]
        print(f"\nDatabase Stats:")
        print(f"  Collection: {stats.get('collection')}")
        print(f"  Points: {stats.get('points_count')}")
        print(f"  Vector Dimension: {stats.get('vector_size')}")
        print(f"  Storage: {stats.get('storage_path')}")

    print("\n" + "="*60)


if __name__ == "__main__":
    ingestion_path = sys.argv[1] if len(sys.argv) > 1 else "./output/ingestion_output_fixed.json"
    storage_path = sys.argv[2] if len(sys.argv) > 2 else "./qdrant_storage"

    result = init_vector_database(ingestion_path, storage_path)
    print_results(result)

    # Also save result to file
    with open("vector_db_init_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults saved to: vector_db_init_result.json")
