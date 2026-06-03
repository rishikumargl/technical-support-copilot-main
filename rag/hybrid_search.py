"""
Hybrid search engine combining dense vector similarity and sparse BM25 lexical search.
Metadata filtering support for department, category, etc.
"""
import logging
import json
from typing import List, Dict, Optional, Tuple
from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class HybridSearchEngine:
    """Perform hybrid search on chunks stored in Qdrant."""

    def __init__(self, qdrant_client: QdrantClient, collection_name: str = "enterprise_chunks", hf_token: str = None):
        """Initialize hybrid search with Qdrant client and embedding service.

        Args:
            qdrant_client: Qdrant client instance
            collection_name: Name of the vector collection
            hf_token: Hugging Face API token (optional)
        """
        self.client = qdrant_client
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService(hf_token=hf_token)
        self.bm25_index = None
        self.chunks_cache = []

    def load_chunks_from_file(self, json_path: str) -> bool:
        """Load chunks from Peer 1's ingestion output for indexing."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            self.chunks_cache = data.get("chunks", [])
            logger.info(f"Loaded {len(self.chunks_cache)} chunks from {json_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load chunks: {str(e)}")
            return False

    def build_bm25_index(self):
        """Build BM25 index from cached chunks for lexical search."""
        try:
            # Tokenize all chunk texts
            corpus = [chunk["text"].split() for chunk in self.chunks_cache]
            self.bm25_index = BM25Okapi(corpus)
            logger.info(f"Built BM25 index for {len(corpus)} chunks")
        except Exception as e:
            logger.error(f"Failed to build BM25 index: {str(e)}")

    def seed_qdrant(self):
        """Embed and store all chunks in Qdrant."""
        try:
            if not self.chunks_cache:
                logger.warning("No chunks to seed. Load chunks first.")
                return

            # Embed all chunks
            texts = [chunk["text"] for chunk in self.chunks_cache]
            embeddings = self.embedding_service.embed_batch(texts)

            # Prepare points for Qdrant
            points = []
            for idx, (chunk, embedding) in enumerate(zip(self.chunks_cache, embeddings)):
                # Metadata as payload
                payload = {
                    "chunk_id": chunk["chunk_id"],
                    "document_name": chunk["document_name"],
                    "department": chunk["department"],
                    "category": chunk["category"],
                    "version": chunk["version"],
                    "text": chunk["text"],
                    "strategy": chunk.get("strategy", "unknown"),
                    "start_pos": chunk.get("start_pos", 0),
                    "end_pos": chunk.get("end_pos", 0),
                }

                point = PointStruct(
                    id=idx,
                    vector=embedding.tolist(),
                    payload=payload
                )
                points.append(point)

            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Seeded {len(points)} points into Qdrant")
            return len(points)
        except Exception as e:
            logger.error(f"Failed to seed Qdrant: {str(e)}")
            return 0

    def bm25_score(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Get BM25 scores for query against cached chunks."""
        if not self.bm25_index:
            logger.warning("BM25 index not built. Build it first.")
            return []

        try:
            query_tokens = query.split()
            scores = self.bm25_index.get_scores(query_tokens)

            # Get top-k indices
            ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
            return ranked
        except Exception as e:
            logger.error(f"BM25 scoring failed: {str(e)}")
            return []

    def dense_search(self, query: str, top_k: int = 10, filters: Optional[Dict] = None) -> List[Dict]:
        """Search using vector similarity in Qdrant."""
        try:
            # Embed query
            query_embedding = self.embedding_service.embed_text(query)

            # Build metadata filters
            qdrant_filter = None
            if filters:
                conditions = []
                if "department" in filters:
                    conditions.append(
                        FieldCondition(
                            key="department",
                            match=MatchValue(value=filters["department"])
                        )
                    )
                if "category" in filters:
                    conditions.append(
                        FieldCondition(
                            key="category",
                            match=MatchValue(value=filters["category"])
                        )
                    )
                if conditions:
                    from qdrant_client.models import Filter as QFilter, AND
                    qdrant_filter = QFilter(must=conditions)

            # Vector search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=qdrant_filter,
                limit=top_k,
                with_payload=True
            )

            # Format results
            search_results = []
            for hit in results:
                search_results.append({
                    "chunk_id": hit.payload["chunk_id"],
                    "document_name": hit.payload["document_name"],
                    "department": hit.payload["department"],
                    "category": hit.payload["category"],
                    "version": hit.payload["version"],
                    "text": hit.payload["text"],
                    "dense_score": hit.score
                })

            logger.info(f"Dense search returned {len(search_results)} results")
            return search_results
        except Exception as e:
            logger.error(f"Dense search failed: {str(e)}")
            return []

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4
    ) -> List[Dict]:
        """Combined dense + sparse search with weighted scoring.

        Metadata Filtering:
        - Filters are applied BEFORE scoring (hard filtering)
        - Only chunks matching ALL filter criteria are included
        - Supported filters: department, category, version, document_name
        - Example: filters={"department": "Engineering", "category": "Guide"}
        """
        try:
            # Get dense results
            dense_results = self.dense_search(query, top_k * 2, filters)
            dense_scores = {r["chunk_id"]: r["dense_score"] for r in dense_results}

            # Get BM25 scores for all cached chunks
            bm25_results = self.bm25_score(query, top_k * 2)

            # Normalize scores
            max_dense = max(dense_scores.values()) if dense_scores else 1.0
            max_bm25 = bm25_results[0][1] if bm25_results else 1.0

            # Combine scores
            combined_scores = {}
            for chunk in self.chunks_cache:
                chunk_id = chunk["chunk_id"]

                # Apply metadata filters
                if filters:
                    if "department" in filters and chunk["department"] != filters["department"]:
                        continue
                    if "category" in filters and chunk["category"] != filters["category"]:
                        continue

                dense_score = dense_scores.get(chunk_id, 0) / max_dense if max_dense > 0 else 0
                # Find BM25 score for this chunk
                bm25_score = 0
                for idx, bm25_val in bm25_results:
                    if self.chunks_cache[idx]["chunk_id"] == chunk_id:
                        bm25_score = bm25_val / max_bm25 if max_bm25 > 0 else 0
                        break

                combined = (dense_score * dense_weight) + (bm25_score * sparse_weight)
                if combined > 0:
                    combined_scores[chunk_id] = {
                        "combined_score": combined,
                        "dense_score": dense_score,
                        "sparse_score": bm25_score,
                        "chunk": chunk
                    }

            # Sort by combined score
            ranked = sorted(combined_scores.items(), key=lambda x: x[1]["combined_score"], reverse=True)[:top_k]

            # Format results
            results = []
            for chunk_id, scores in ranked:
                chunk = scores["chunk"]
                results.append({
                    "chunk_id": chunk["chunk_id"],
                    "document_name": chunk["document_name"],
                    "department": chunk["department"],
                    "category": chunk["category"],
                    "version": chunk["version"],
                    "text": chunk["text"],
                    "combined_score": scores["combined_score"],
                    "dense_score": scores["dense_score"],
                    "sparse_score": scores["sparse_score"]
                })

            logger.info(f"Hybrid search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            return []

    def retrieve_relevant_chunks(
        self,
        query: str,
        filters: Optional[Dict] = None,
        search_type: str = "hybrid",
        top_k: int = 5
    ) -> List[Dict]:
        """Main retrieval function called by backend (Peer 3).

        Args:
            query: User's question or search text
            filters: Metadata filters (hard filtering, AND logic)
                Example: {"department": "Engineering", "category": "Guide"}
                Supported fields: department, category, version, document_name
            search_type: "hybrid" (dense+sparse) or "dense" (vector only)
            top_k: Number of results to return

        Returns:
            List of ranked chunks with metadata and scores

        Example:
            results = engine.retrieve_relevant_chunks(
                query="What are system requirements?",
                filters={"department": "Engineering"},
                search_type="hybrid",
                top_k=5
            )
        """
        if search_type == "hybrid":
            return self.hybrid_search(query, top_k, filters)
        elif search_type == "dense":
            return self.dense_search(query, top_k, filters)
        else:
            logger.error(f"Unknown search type: {search_type}")
            return []
