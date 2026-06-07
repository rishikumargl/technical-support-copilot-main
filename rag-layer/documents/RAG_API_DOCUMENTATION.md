# RAG Layer API Documentation

## Overview

The RAG (Retrieval Augmented Generation) Layer provides a comprehensive REST API for querying enterprise knowledge bases with advanced retrieval techniques including hybrid search, semantic reranking, query expansion, and adaptive filtering.

## Version

**Current Version**: 2.0  
**Latest Features**: Phase 1, 2, and 3 improvements implemented

## Base URL

```
http://localhost:5001
```

## Endpoints

### 1. Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "ok",
  "service": "rag-server",
  "rag_initialized": true
}
```

---

### 2. Initialize RAG System

```http
POST /api/rag/initialize
```

**Request Body**:
```json
{
  "source_dir": "ingestion_pipeline/data",
  "chunking_strategy": "fixed",
  "use_ensemble": false,
  "enable_query_expansion": false
}
```

**Parameters**:
- `source_dir` (string): Path to documents directory
- `chunking_strategy` (string): `"fixed"`, `"semantic"`, or `"adaptive"`
  - `fixed`: Fixed-size chunks (500 chars) with 50-char overlap
  - `semantic`: Chunks based on sentence boundaries (Phase 1)
  - `adaptive`: Chunks respecting paragraph boundaries (Phase 2)
- `use_ensemble` (boolean): Enable ensemble embeddings (Phase 3, default: false)
- `enable_query_expansion` (boolean): Enable query expansion (Phase 3, default: false)

**Response**:
```json
{
  "success": true,
  "message": "RAG system initialized successfully",
  "result": {
    "status": "success",
    "documents_ingested": 25,
    "chunks_created": 150,
    "embeddings_generated": 150,
    "vectors_stored": 150
  },
  "features": {
    "chunking_strategy": "adaptive",
    "ensemble_embeddings": false,
    "query_expansion": false
  }
}
```

---

### 3. Basic Query

```http
POST /api/rag/query
```

**Request Body**:
```json
{
  "question": "What are the system requirements?",
  "top_k": 5,
  "search_type": "hybrid",
  "min_score": 0.0,
  "use_reranking": true,
  "department": "Engineering",
  "category": "Guide"
}
```

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | required | Your query or question |
| `top_k` | integer | 5 | Number of results to return |
| `search_type` | string | "hybrid" | `"hybrid"`, `"dense"`, or `"sparse"` |
| `min_score` | float | 0.0 | Minimum confidence threshold (0.0-1.0) |
| `use_reranking` | boolean | true | Apply semantic reranking (Phase 2) |
| `department` | string | null | Filter by department |
| `category` | string | null | Filter by category |

**Response**:
```json
{
  "success": true,
  "question": "What are the system requirements?",
  "answer": "Python 3.8+ and PostgreSQL 12.0 or higher...",
  "sources": [
    {
      "document_name": "v1_setup_guide",
      "chunk": "Python 3.8+ and PostgreSQL 12.0 or higher. All dependencies...",
      "relevance_score": 0.87,
      "confidence": 0.87,
      "dense_score": 0.92,
      "sparse_score": 0.78,
      "rerank_score": 0.89,
      "metadata": {
        "department": "Engineering",
        "category": "Guide",
        "version": "1.0"
      }
    }
  ],
  "confidence_score": 0.87,
  "status": "RAG_IMPLEMENTED",
  "message": "Successfully retrieved from RAG system",
  "retrieval_method": "hybrid_with_reranking"
}
```

---

### 4. Advanced Query

```http
POST /api/rag/query-advanced
```

**Request Body**:
```json
{
  "query": "HR policies for remote work",
  "top_k": 5,
  "retrieval_strategy": "hybrid",
  "filters": {
    "department": "HR",
    "category": "Policy"
  },
  "min_score": 0.1,
  "use_reranking": true
}
```

**Parameters**:
- `query` (string): Your question
- `top_k` (integer): Number of results
- `retrieval_strategy` (string): `"hybrid"`, `"dense"`, or `"sparse"`
- `filters` (object): Metadata filters
  - `department` (string): Department filter
  - `category` (string): Category filter
- `min_score` (float): Confidence threshold
- `use_reranking` (boolean): Apply semantic reranking

**Response**:
```json
{
  "success": true,
  "query": "HR policies for remote work",
  "answer": "Remote work is permitted...",
  "sources": [
    {
      "document_name": "remote_work_policy",
      "chunk": "Remote work is permitted for roles...",
      "relevance_score": 0.92,
      "dense_score": 0.89,
      "sparse_score": 0.95,
      "rerank_score": 0.93,
      "metadata": {
        "department": "HR",
        "category": "Policy",
        "version": "2.1"
      }
    }
  ],
  "confidence_score": 0.92,
  "result_count": 1,
  "status": "RAG_IMPLEMENTED",
  "message": "Successfully retrieved from RAG system with advanced options",
  "retrieval_method": "hybrid_with_reranking"
}
```

---

### 5. Get Statistics

```http
GET /api/rag/stats
```

**Response**:
```json
{
  "success": true,
  "stats": {
    "collection_name": "enterprise_chunks",
    "points_count": 150,
    "vectors_size": 384,
    "indexed_vectors_count": 150
  }
}
```

---

### 6. Document Ingestion

```http
POST /api/rag/ingest
```

**Request Body**:
```json
{
  "document_id": "remote_work_policy_v2.pdf"
}
```

**Note**: Documents are indexed on RAG server restart. Newly uploaded documents are searchable via BM25 keyword search immediately.

**Response**:
```json
{
  "success": true,
  "message": "Document received. Restart RAG server to index it with vector embeddings.",
  "result": {
    "document_id": "remote_work_policy_v2.pdf",
    "status": "pending_indexing",
    "note": "Documents are indexed when RAG server starts..."
  }
}
```

---

## Search Types Explained

### Hybrid Search (Recommended)
```json
{
  "search_type": "hybrid"
}
```
- Combines dense (vector) and sparse (BM25) search
- Default weights: 60% dense, 40% sparse
- Best for balanced recall and precision
- **Phase 2**: Supports semantic reranking with cross-encoders

### Dense Search
```json
{
  "search_type": "dense"
}
```
- Vector similarity search only
- Best for semantic relevance
- Fast retrieval
- May miss keyword-exact matches

### Sparse Search
```json
{
  "search_type": "sparse"
}
```
- BM25 keyword search only
- Best for exact phrase matching
- Fast and explainable
- May miss semantic relevance

---

## Filtering Examples

### Single Filter (AND logic)
```json
{
  "department": "Engineering"
}
```

### Multiple Filters (AND logic)
```json
{
  "department": "Engineering",
  "category": "Guide"
}
```

### Advanced Filters (Phase 2)
```json
{
  "department": "Engineering",
  "not_category": "Deprecated"
}
```

---

## Reranking Features (Phase 2)

### Enable Semantic Reranking
```json
{
  "use_reranking": true
}
```

When enabled:
- Cross-encoder model reranks top results
- Provides `rerank_score` in response
- Improves precision by ~15-25%
- Minimal performance overhead

**Model Used**: `cross-encoder/mmarco-MiniLMv2-L12-H384`

---

## Score Filtering (Phase 1)

```json
{
  "min_score": 0.15
}
```

- Filters results below confidence threshold
- Helps eliminate false positives
- Typical values: 0.0 (no filter), 0.1-0.2 (high confidence)
- Score normalized to 0.0-1.0 range

---

## Query Expansion (Phase 3)

### Enable Query Expansion
```json
{
  "use_query_expansion": true
}
```

When enabled:
- Query is expanded with synonyms and variations
- Multiple query variations searched
- Results deduplicated and re-ranked
- Improves recall by ~10-15%

### Supported Acronym Expansions
- `HR` → `human resources`
- `IT` → `information technology`
- `API` → `application programming interface`
- `DB` → `database`
- And more...

---

## Response Score Fields

| Field | Description | Range | Note |
|-------|-------------|-------|------|
| `combined_score` | Hybrid search score | 0.0-1.0 | Default ranking score |
| `dense_score` | Vector similarity | 0.0-1.0 | From semantic matching |
| `sparse_score` | BM25 keyword score | 0.0-1.0 | From exact matches |
| `rerank_score` | Cross-encoder score | 0.0-1.0 | When reranking enabled |
| `expansion_count` | Appeared in N variations | 1+ | When expansion enabled |

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Question is required",
  "status": "ERROR",
  "success": false
}
```

### 503 Service Unavailable
```json
{
  "error": "RAG pipeline not initialized",
  "message": "Please initialize the RAG system first",
  "status": "ERROR"
}
```

### 500 Internal Server Error
```json
{
  "error": "Error message",
  "status": "ERROR",
  "success": false
}
```

---

## Example Workflows

### Basic Search
```bash
curl -X POST http://localhost:5001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I setup the system?"
  }'
```

### High Confidence Search
```bash
curl -X POST http://localhost:5001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "HR policies",
    "department": "HR",
    "min_score": 0.2,
    "use_reranking": true
  }'
```

### Comprehensive Search with Expansion
```bash
curl -X POST http://localhost:5001/api/rag/query-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "API documentation",
    "retrieval_strategy": "hybrid",
    "filters": {
      "department": "Engineering",
      "category": "Guide"
    },
    "min_score": 0.15,
    "use_reranking": true
  }'
```

### Initialize with Advanced Features
```bash
curl -X POST http://localhost:5001/api/rag/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "source_dir": "ingestion_pipeline/data",
    "chunking_strategy": "adaptive",
    "use_ensemble": true,
    "enable_query_expansion": true
  }'
```

---

## Performance Tips

1. **Use `min_score` filtering** to eliminate low-confidence results early
2. **Enable reranking** for better precision (minimal overhead)
3. **Use appropriate `search_type`**:
   - `hybrid` for general queries
   - `dense` for semantic queries
   - `sparse` for exact phrase matching
4. **Filter early** using metadata filters to reduce search space
5. **Query expansion** helpful for typos and synonyms
6. **Ensemble embeddings** (Phase 3) for higher-quality results

---

## Chunking Strategies

### Fixed (Default)
- 500 character chunks with 50 character overlap
- Fast, predictable
- May cut mid-sentence

### Semantic
- Groups sentences into semantic units
- Better for natural language
- Slower processing

### Adaptive (Phase 2)
- Groups paragraphs respecting boundaries
- Best context preservation
- Balanced speed/quality

---

## Future Enhancements

- Real-time document indexing
- Multi-language support
- Feedback-based weight learning
- Citation extraction and ranking
- Document source prioritization
- Custom filter operators
- Caching and memoization

---

## Support & Troubleshooting

### RAG Server Won't Start
1. Check if port 5001 is available
2. Verify documents exist in source directory
3. Check logs for initialization errors

### Low Accuracy Results
1. Enable `use_reranking: true`
2. Increase `top_k` to get more candidates
3. Use `min_score` appropriately
4. Try different `search_type` options
5. Check metadata filters aren't too restrictive

### Slow Queries
1. Reduce `top_k` value
2. Disable `use_reranking` if not needed
3. Disable `use_query_expansion`
4. Optimize filters to reduce candidate set

---

## Version History

### v2.0 (Current)
- Phase 1: Query preprocessing, confidence filtering, score normalization
- Phase 2: Semantic reranking, adaptive chunking, enhanced filtering
- Phase 3: Ensemble embeddings, query expansion, adaptive weights

### v1.0
- Basic hybrid search
- Metadata filtering
- Qdrant integration

---

**Last Updated**: 2026-06-07
