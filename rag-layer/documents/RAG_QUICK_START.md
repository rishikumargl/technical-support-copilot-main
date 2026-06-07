# RAG Layer Quick Start Guide

## TL;DR - Get Started in 5 Minutes

### 1. Initialize RAG with All Features
```bash
curl -X POST http://localhost:5001/api/rag/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "chunking_strategy": "adaptive",
    "use_ensemble": true,
    "enable_query_expansion": true
  }'
```

### 2. Query with Full Improvements
```bash
curl -X POST http://localhost:5001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "HR policies for remote work",
    "min_score": 0.15,
    "use_reranking": true,
    "department": "HR"
  }'
```

### 3. Check Results
```json
{
  "success": true,
  "answer": "Remote work policy allows...",
  "sources": [
    {
      "relevance_score": 0.92,
      "rerank_score": 0.93,
      "dense_score": 0.89,
      "sparse_score": 0.95,
      "metadata": {"department": "HR", "category": "Policy"}
    }
  ],
  "confidence_score": 0.93
}
```

---

## Quick Features Overview

### Phase 1: Query Intelligence
✅ **Acronym Expansion**: HR → human resources  
✅ **Confidence Filtering**: Remove low-quality results  
✅ **Smart Scoring**: Percentile-based normalization  

**Use when**: You want better handling of acronyms and typos

### Phase 2: Semantic Understanding
✅ **Cross-Encoder Reranking**: ML-powered result ranking  
✅ **Adaptive Chunking**: Better context preservation  
✅ **Flexible Filtering**: Complex filter logic  

**Use when**: You need higher precision and better semantic matching

### Phase 3: Advanced Retrieval
✅ **Ensemble Embeddings**: Multiple models for better coverage  
✅ **Query Expansion**: Synonym and variation matching  
✅ **Adaptive Weights**: Learn from feedback  

**Use when**: You have high accuracy requirements or domain-specific data

---

## Common Use Cases

### Case 1: Basic Search (Minimal Setup)
```python
results = ask(
    question="How to setup?",
    top_k=5,
    use_reranking=False  # Faster
)
```
- **Speed**: Fast ⚡
- **Accuracy**: Good ✓
- **Use for**: Quick lookups, high-volume queries

### Case 2: Accurate Search (Recommended)
```python
results = ask(
    question="HR remote work policies",
    department="HR",
    min_score=0.15,
    use_reranking=True  # Better results
)
```
- **Speed**: Medium ⚡⚡
- **Accuracy**: Excellent ✓✓
- **Use for**: Production queries, user-facing search

### Case 3: Comprehensive Search (High Quality)
```python
results = ask(
    question="API setup and configuration",
    search_type="hybrid",
    use_reranking=True,
    use_query_expansion=True,  # Also search synonyms
    top_k=10,
    min_score=0.1
)
```
- **Speed**: Slower ⚡⚡⚡
- **Accuracy**: Maximum ✓✓✓
- **Use for**: Complex queries, edge cases, low-accuracy fallback

---

## API Quick Reference

### Initialize
```http
POST /api/rag/initialize
Content-Type: application/json

{
  "source_dir": "ingestion_pipeline/data",
  "chunking_strategy": "adaptive",
  "use_ensemble": false,
  "enable_query_expansion": false
}
```

### Basic Query
```http
POST /api/rag/query
Content-Type: application/json

{
  "question": "What are system requirements?",
  "top_k": 5,
  "min_score": 0.0,
  "use_reranking": true
}
```

### Advanced Query
```http
POST /api/rag/query-advanced
Content-Type: application/json

{
  "query": "HR policies",
  "top_k": 5,
  "retrieval_strategy": "hybrid",
  "filters": {
    "department": "HR",
    "category": "Policy"
  },
  "min_score": 0.15,
  "use_reranking": true
}
```

### Get Stats
```http
GET /api/rag/stats
```

---

## Python Quick Reference

### Using Query System
```python
from query_system import ask

# Simple query
ask("How to install?")

# Advanced query
results = ask(
    question="HR remote work policy",
    department="HR",
    top_k=5,
    min_score=0.2,
    use_reranking=True,
    use_query_expansion=False
)

for result in results:
    print(f"{result['document_name']}: {result['combined_score']:.1%}")
```

### Direct Engine Usage
```python
from integration_pipeline import RAGIntegrationPipeline

# Initialize
pipeline = RAGIntegrationPipeline(
    source_dir="ingestion_pipeline/data",
    chunking_strategy="adaptive"
)
pipeline.run_full_pipeline()

# Query
results = pipeline.query(
    question="System requirements",
    search_type="hybrid",
    top_k=5,
    min_score=0.15,
    use_reranking=True
)
```

### Access Search Engine Directly
```python
engine = pipeline.search_engine

# Enable features
engine.setup_ensemble(use_ensemble=True)
engine.setup_query_expansion()

# Query
results = engine.retrieve_relevant_chunks(
    query="API documentation",
    filters={"department": "Engineering"},
    search_type="hybrid",
    top_k=5,
    min_score=0.1,
    use_reranking=True,
    use_query_expansion=True
)
```

---

## Tuning Tips

### For Better Accuracy
```python
# 1. Enable reranking
use_reranking=True

# 2. Use adaptive chunking
chunking_strategy="adaptive"

# 3. Set appropriate minimum score
min_score=0.15

# 4. Use hybrid search
search_type="hybrid"

# 5. Filter metadata when possible
filters={"department": "Engineering"}
```

### For Better Speed
```python
# 1. Disable reranking
use_reranking=False

# 2. Use fixed chunking
chunking_strategy="fixed"

# 3. Lower top_k
top_k=3

# 4. Use dense search (if semantic)
search_type="dense"
```

### For Large Result Sets
```python
# 1. Filter early
filters={"department": "Engineering"}

# 2. Use appropriate search type
search_type="hybrid"  # Balanced

# 3. Increase top_k for reranking
top_k=10  # Get more candidates

# 4. Set min_score to filter
min_score=0.2
```

### For Typos and Synonyms
```python
# Enable query expansion
use_query_expansion=True

# This will find:
# "setup" → also searches "install", "deploy", "configure"
# "DB" → also searches "database"
# "issue" → also searches "problem", "bug", "error"
```

---

## Score Interpretation

### Confidence Levels
| Score Range | Interpretation | Action |
|---|---|---|
| 0.9-1.0 | Excellent match | Use confidently |
| 0.7-0.9 | Good match | Generally reliable |
| 0.5-0.7 | Fair match | Review carefully |
| 0.2-0.5 | Weak match | May need more context |
| 0.0-0.2 | Poor match | Likely irrelevant |

### Score Fields
- **rerank_score**: Most accurate (0-1, when reranking enabled)
- **combined_score**: Hybrid score (0-1, always present)
- **dense_score**: Semantic similarity (0-1)
- **sparse_score**: Keyword matching (0-1)
- **expansion_count**: Matched N query variations (when expansion enabled)

### Default Thresholds
```python
min_score=0.0   # No filtering (default)
min_score=0.1   # Low confidence cutoff
min_score=0.15  # Moderate confidence
min_score=0.2   # High confidence (strict)
min_score=0.25  # Very high confidence
```

---

## Testing

### Run Full Test Suite
```bash
cd rag-layer
python test_improvements.py
```

### Test Specific Phase
```python
# Phase 1: Query preprocessing
ask("HR policies", print_results=True)  # Note acronym expansion

# Phase 2: Reranking
results1 = ask("setup", use_reranking=False)
results2 = ask("setup", use_reranking=True)
# Compare results to see reranking effect

# Phase 3: Query expansion
results1 = ask("API docs", use_query_expansion=False)
results2 = ask("API docs", use_query_expansion=True)
# Compare to see expanded matches
```

---

## Common Issues & Solutions

### Issue: No results found
**Solutions**:
1. Try reducing `min_score` → `0.0`
2. Enable `use_query_expansion=True`
3. Check filters aren't too restrictive
4. Try different `search_type` (hybrid vs dense vs sparse)

### Issue: Wrong results ranked first
**Solutions**:
1. Enable `use_reranking=True` (if disabled)
2. Lower `min_score` to filter better matches
3. Try `use_query_expansion=True`
4. Check if query is ambiguous - clarify it

### Issue: Slow queries
**Solutions**:
1. Disable `use_reranking` (costs ~100-200ms)
2. Disable `use_query_expansion` (costs 3-5x slower)
3. Reduce `top_k` (fewer results to process)
4. Use `search_type="sparse"` (fastest)

### Issue: High memory usage
**Solutions**:
1. Disable `use_ensemble=true`
2. Use fixed chunking instead of adaptive
3. Reduce `top_k`
4. Restart RAG server periodically

---

## Next Steps

1. **Start Simple**: Use Phase 1 features (preprocessing, filtering)
2. **Add Phase 2**: Enable reranking for better accuracy
3. **Monitor Results**: Track accuracy metrics
4. **Tune Parameters**: Adjust min_score, chunking_strategy
5. **Consider Phase 3**: Only if accuracy plateaus

---

## Resources

- 📖 [RAG_API_DOCUMENTATION.md](RAG_API_DOCUMENTATION.md) - Complete API reference
- 📊 [RAG_IMPROVEMENTS.md](RAG_IMPROVEMENTS.md) - Detailed improvement analysis
- 📝 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details
- 🧪 [test_improvements.py](rag-layer/test_improvements.py) - Test suite

---

**Need Help?** Check the full documentation or run the test suite for examples.

**Last Updated**: 2026-06-07
