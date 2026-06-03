# Quick Start Guide

## 5-Minute Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the pipeline (generates sample data automatically)
python ingestion_pipeline.py fixed

# 3. Check output
cat output/ingestion_output_fixed.json | python -m json.tool | head -50
```

## Core Files

| File | Purpose | Status |
|------|---------|--------|
| `document_parser.py` | Parse documents & extract metadata | ✅ Complete |
| `chunking_strategies.py` | Fixed-size & semantic chunking | ✅ Complete |
| `ingestion_pipeline.py` | Full pipeline orchestration | ✅ Complete |
| `test_pipeline.py` | 10 unit tests | ✅ All Pass |
| `requirements.txt` | Python dependencies | ✅ Complete |

## Two Chunking Strategies

### Fixed-Size Chunking (Faster)
```bash
python ingestion_pipeline.py fixed
```
- 500-character chunks with 50-char overlap
- Consistent, predictable output
- Best for: High-volume ingestion

### Semantic Chunking (Smarter)
```bash
python ingestion_pipeline.py semantic
```
- Respects sentence & section boundaries
- Preserves context
- Best for: Quality retrieval systems

## Schema Overview

### Input: Documents
```json
{
  "document_name": "v1_setup_guide",
  "department": "Engineering",
  "category": "Guide",
  "version": "1.0",
  "text_content": "..."
}
```

### Output: Chunks (with UUIDs)
```json
{
  "chunk_id": "8c3565dc-aa43-4264-8f3f-43bbfc12b69b",
  "document_name": "v1_setup_guide",
  "department": "Engineering",
  "category": "Guide",
  "version": "1.0",
  "strategy": "fixed_size",
  "text": "...",
  "start_pos": 0,
  "end_pos": 500,
  "size": 500
}
```

## Common Tasks

### Process All Documents
```python
from ingestion_pipeline import IngestionPipeline

pipeline = IngestionPipeline("data", "output", "fixed")
result = pipeline.run()
print(f"Created {result['chunks']} chunks")
```

### Use Custom Chunk Size
```python
from chunking_strategies import FixedSizeChunking

chunker = FixedSizeChunking(chunk_size=1000, overlap=100)
chunks = chunker.chunk(text, "doc_name")
```

### Load Output JSON
```python
import json

with open("output/ingestion_output_fixed.json") as f:
    data = json.load(f)
    chunks = data["chunks"]
    total = len(chunks)
```

### Filter by Department
```python
engineering_chunks = [
    c for c in chunks 
    if c['department'] == 'Engineering'
]
```

## Departments & Categories

**Valid Departments:**
- Engineering
- HR
- Operations
- Support

**Valid Categories:**
- Policy
- Ticket
- Guide

## File Organization

```
data/                          # Input documents
├── Engineering/
│   └── v1_setup_guide.txt
├── HR/
│   └── v2_remote_policy.txt
├── Operations/
└── Support/

output/                        # Generated chunks
├── ingestion_output_fixed.json
└── ingestion_output_semantic.json
```

## Testing

```bash
# Run all tests (10 tests, ~17 seconds)
python test_pipeline.py

# Run specific test
python -m unittest test_pipeline.TestDocumentParser.test_metadata_extraction_from_path
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No documents found | Check file extension (.pdf or .txt) and directory structure |
| Empty chunks | Verify PDF is readable and not encrypted |
| Slow performance | Use fixed-size chunking instead of semantic |
| Memory error | Process smaller batches or increase RAM |
| Import error | Run `pip install -r requirements.txt` |

## Performance

- **Fixed-size**: ~10ms per document
- **Semantic**: ~500ms per document (first run includes 150MB model download)
- **Memory**: 50MB (fixed) vs 400MB (semantic)

## Output Examples

### Statistics
```json
{
  "pipeline_metadata": {
    "total_documents": 2,
    "total_chunks": 6,
    "chunking_strategy": "fixed",
    "avg_chunk_size": 460
  }
}
```

### Document Summary
```json
{
  "document_name": "v1_setup_guide",
  "department": "Engineering",
  "category": "Guide",
  "version": "1",
  "chunk_count": 3
}
```

## Next Steps

1. ✅ Parse documents → `document_parser.py`
2. ✅ Generate chunks → `chunking_strategies.py`
3. ✅ Save to JSON → `ingestion_pipeline.py`
4. → Load into vector database (MongoDB, Pinecone, etc.)
5. → Integrate with RAG system

## API Quick Reference

```python
# Parse documents
from document_parser import DocumentParser
parser = DocumentParser("data")
docs = parser.parse_directory()

# Chunk with fixed strategy
from chunking_strategies import FixedSizeChunking
chunker = FixedSizeChunking(chunk_size=500, overlap=50)
chunks = chunker.chunk(text, "doc_name")

# Chunk with semantic strategy
from chunking_strategies import SemanticChunking
chunker = SemanticChunking(target_size=500)
chunks = chunker.chunk(text, "doc_name")

# Full pipeline
from ingestion_pipeline import IngestionPipeline
pipeline = IngestionPipeline("data", "output", "fixed")
result = pipeline.run()
```

## Documentation

- **README_PIPELINE.md** - Full technical documentation
- **EXAMPLES.md** - Complete usage examples
- **IMPLEMENTATION_SUMMARY.md** - Architecture & design decisions
- **QUICK_START.md** - This file

## Support

For issues:
1. Check the troubleshooting table above
2. Review EXAMPLES.md for usage patterns
3. Run tests to verify installation: `python test_pipeline.py`
4. Check logs in the console output

---

**Ready to go!** Run `python ingestion_pipeline.py fixed` to see it in action.
