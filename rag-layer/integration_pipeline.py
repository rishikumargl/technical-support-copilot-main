"""
Integration bridge connecting the ingestion pipeline with the RAG layer.
This module orchestrates the complete workflow: parse → chunk → embed → store → query.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional, Literal

# Setup paths for imports
sys.path.insert(0, str(Path(__file__).parent / "ingestion_pipeline" / "src"))

from ingestion_pipeline import IngestionPipeline
from embedding_service import EmbeddingService
from qdrant_setup import QdrantDB
from hybrid_search import HybridSearchEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGIntegrationPipeline:
    """
    Complete RAG pipeline: ingestion → embedding → vector storage → hybrid search.

    Integrates:
    - Ingestion pipeline (document parsing & chunking)
    - Embedding service (vector generation)
    - Qdrant database (vector storage)
    - Hybrid search engine (retrieval)
    """

    def __init__(
        self,
        source_dir: str = "documents",
        output_dir: str = "output",
        qdrant_storage: str = "./qdrant_storage",
        chunking_strategy: Literal["fixed", "semantic"] = "fixed",
        embedding_model: str = "all-MiniLM-L6-v2",
        hf_token: Optional[str] = None,
    ):
        """Initialize the complete RAG pipeline.

        Args:
            source_dir: Directory containing documents to ingest
            output_dir: Directory for pipeline outputs
            qdrant_storage: Path to Qdrant vector database storage
            chunking_strategy: "fixed" or "semantic"
            embedding_model: HuggingFace model name for embeddings
            hf_token: Optional Hugging Face API token
        """
        logger.info("="*70)
        logger.info("INITIALIZING RAG INTEGRATION PIPELINE")
        logger.info("="*70)

        self.source_dir = source_dir
        self.output_dir = output_dir
        self.qdrant_storage = qdrant_storage
        self.hf_token = hf_token

        # Initialize components
        logger.info("\n[1/4] Initializing ingestion pipeline...")
        self.ingestion = IngestionPipeline(
            source_dir=source_dir,
            output_dir=output_dir,
            chunking_strategy=chunking_strategy,
        )

        logger.info("[2/4] Initializing embedding service...")
        self.embedding_service = EmbeddingService(
            model_name=embedding_model,
            hf_token=hf_token,
        )

        logger.info("[3/4] Initializing Qdrant database...")
        self.db = QdrantDB(storage_path=qdrant_storage)
        self.db.create_collection()

        logger.info("[4/4] Initializing hybrid search engine...")
        self.search_engine = HybridSearchEngine(
            qdrant_client=self.db.client,
            collection_name=self.db.collection_name,
            hf_token=hf_token,
        )

        logger.info("\n✓ RAG Integration Pipeline initialized successfully\n")

    def run_full_pipeline(self) -> Dict:
        """
        Execute the complete pipeline: ingest → embed → store → index.

        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info("="*70)
        logger.info("RUNNING FULL RAG PIPELINE")
        logger.info("="*70)

        # Step 1: Ingest documents
        logger.info("\n[Step 1/5] Ingesting documents...")
        ingest_result = self.ingestion.run()

        if ingest_result["status"] != "success":
            logger.error("Ingestion failed")
            return {"status": "failed", "error": "Ingestion failed"}

        chunks = self._load_chunks_from_file(ingest_result["output_file"])
        if not chunks:
            logger.error("No chunks generated")
            return {"status": "failed", "error": "No chunks generated"}

        logger.info(f"✓ Ingested {ingest_result['documents']} documents into {ingest_result['chunks']} chunks")

        # Step 2: Load chunks into search engine
        logger.info("\n[Step 2/5] Loading chunks into search engine...")
        self.search_engine.load_chunks_from_file(ingest_result["output_file"])
        logger.info(f"✓ Loaded {len(self.search_engine.chunks_cache)} chunks")

        # Step 3: Embed chunks
        logger.info("\n[Step 3/5] Generating embeddings...")
        embedded_chunks = self.embedding_service.embed_chunks(chunks)
        logger.info(f"✓ Generated embeddings for {len(embedded_chunks)} chunks")

        # Step 4: Store in Qdrant
        logger.info("\n[Step 4/5] Storing embeddings in Qdrant...")
        points_count = self._seed_qdrant(embedded_chunks)
        logger.info(f"✓ Stored {points_count} vectors in Qdrant")

        # Step 5: Build search indices
        logger.info("\n[Step 5/5] Building search indices...")
        self.search_engine.build_bm25_index()
        logger.info("✓ Built BM25 index for hybrid search")

        # Get final statistics
        stats = self.db.get_collection_stats()

        logger.info("\n" + "="*70)
        logger.info("RAG PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*70)

        return {
            "status": "success",
            "documents_ingested": ingest_result["documents"],
            "chunks_created": ingest_result["chunks"],
            "embeddings_generated": len(embedded_chunks),
            "vectors_stored": points_count,
            "qdrant_stats": stats,
            "output_file": ingest_result["output_file"],
        }

    def query(
        self,
        question: str,
        department: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
        search_type: str = "hybrid",
        min_score: float = 0.0,
        use_reranking: bool = True,
    ) -> List[Dict]:
        """
        Query the knowledge base using hybrid search with optional reranking.

        Args:
            question: The question to ask
            department: Optional department filter (Engineering, HR, Operations, Support)
            category: Optional category filter (Policy, Ticket, Guide)
            top_k: Number of results to return
            search_type: "hybrid", "dense", or "sparse"
            min_score: Minimum confidence score threshold (0.0-1.0)
            use_reranking: If True, apply semantic reranking (Phase 2)

        Returns:
            List of relevant chunks with scores
        """
        logger.info(f"\nQUERY: {question}")
        if department or category:
            logger.info(f"FILTERS: department={department}, category={category}")
        if min_score > 0:
            logger.info(f"MIN_SCORE: {min_score}")

        filters = {}
        if department:
            filters["department"] = department
        if category:
            filters["category"] = category

        results = self.search_engine.retrieve_relevant_chunks(
            query=question,
            filters=filters if filters else None,
            search_type=search_type,
            top_k=top_k,
            min_score=min_score,
            use_reranking=use_reranking,
        )

        logger.info(f"RESULTS: Found {len(results)} relevant chunks\n")
        return results

    def _load_chunks_from_file(self, json_path: str) -> List[Dict]:
        """Load chunk data from ingestion pipeline output."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("chunks", [])
        except Exception as e:
            logger.error(f"Failed to load chunks: {e}")
            return []

    def _seed_qdrant(self, chunks: List[Dict]) -> int:
        """Store embedded chunks in Qdrant."""
        try:
            from qdrant_client.models import PointStruct

            points = []
            for idx, chunk in enumerate(chunks):
                payload = {
                    "chunk_id": chunk.get("chunk_id", f"chunk_{idx}"),
                    "document_name": chunk.get("document_name", "unknown"),
                    "department": chunk.get("department", ""),
                    "category": chunk.get("category", ""),
                    "version": chunk.get("version", ""),
                    "text": chunk.get("text", ""),
                    "strategy": chunk.get("strategy", "fixed"),
                    "start_pos": chunk.get("start_pos", 0),
                    "end_pos": chunk.get("end_pos", 0),
                }

                embedding = chunk.get("embedding", [])
                if isinstance(embedding, list):
                    embedding = embedding
                elif hasattr(embedding, 'tolist'):
                    embedding = embedding.tolist()

                points.append(PointStruct(
                    id=idx,
                    vector=embedding,
                    payload=payload,
                ))

            self.db.client.upsert(
                collection_name=self.db.collection_name,
                points=points,
            )
            return len(points)
        except Exception as e:
            logger.error(f"Failed to seed Qdrant: {e}")
            return 0

    def get_stats(self) -> Dict:
        """Get current pipeline statistics."""
        return self.db.get_collection_stats()


def create_rag_pipeline(
    source_dir: str = "documents",
    output_dir: str = "output",
    qdrant_storage: str = "./qdrant_storage",
    chunking_strategy: Literal["fixed", "semantic"] = "fixed",
) -> RAGIntegrationPipeline:
    """Factory function to create and initialize RAG pipeline."""
    return RAGIntegrationPipeline(
        source_dir=source_dir,
        output_dir=output_dir,
        qdrant_storage=qdrant_storage,
        chunking_strategy=chunking_strategy,
    )


if __name__ == "__main__":
    # Example usage
    pipeline = create_rag_pipeline(
        source_dir="ingestion_pipeline/data",
        output_dir="output",
        chunking_strategy="fixed",
    )

    # Run full pipeline
    result = pipeline.run_full_pipeline()
    print("\nPipeline Result:")
    print(json.dumps(result, indent=2, default=str))

    # Example query
    print("\n" + "="*70)
    print("EXAMPLE QUERY")
    print("="*70)
    results = pipeline.query(
        question="What are the system requirements?",
        top_k=3,
    )

    if results:
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['document_name']}")
            print(f"   Score: {result['combined_score']:.1%}")
            print(f"   {result['text'][:150]}...")
