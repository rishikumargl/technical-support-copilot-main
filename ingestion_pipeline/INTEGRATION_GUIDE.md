# Integration Guide

## Quick Integration into Your Project

### Option 1: Import as a Package

```python
from ingestion_pipeline import IngestionPipeline

# Create pipeline
pipeline = IngestionPipeline(
    source_dir="your_documents",
    output_dir="your_output",
    chunking_strategy="fixed"
)

# Run
result = pipeline.run()
print(f"Processed {result['documents']} documents")
print(f"Created {result['chunks']} chunks")
```

### Option 2: Use Individual Components

```python
from ingestion_pipeline import DocumentParser, FixedSizeChunking

# Parse documents
parser = DocumentParser("documents_dir")
docs = parser.parse_directory()

# Chunk them
chunker = FixedSizeChunking(chunk_size=500, overlap=50)
for doc in docs:
    chunks = chunker.chunk(doc["text_content"], doc["document_name"])
```

## Folder Structure

```
ingestion_pipeline/
├── __init__.py                 # Package initialization
├── INTEGRATION_GUIDE.md        # This file
├── src/                        # Core implementation
│   ├── document_parser.py
│   ├── chunking_strategies.py
│   └── ingestion_pipeline.py
├── tests/                      # Test suite
│   ├── test_pipeline.py
│   └── verify_pipeline.py
├── docs/                       # Documentation
│   ├── README.md
│   ├── QUICK_START.md
│   ├── README_PIPELINE.md
│   ├── EXAMPLES.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── PROJECT_FILES.md
├── config/                     # Configuration
│   └── requirements.txt
├── data/                       # Sample input data
│   ├── Engineering/
│   └── HR/
├── output/                     # Generated outputs
│   ├── ingestion_output_fixed.json
│   └── ingestion_output_semantic.json
└── examples/                   # Example scripts
    └── (to be added)
```

## Installation

```bash
# Install from config/requirements.txt
pip install -r ingestion_pipeline/config/requirements.txt
```

## Basic Usage

### 1. Full Pipeline (Recommended)

```python
from ingestion_pipeline import IngestionPipeline

pipeline = IngestionPipeline(
    source_dir="documents",
    output_dir="chunks",
    chunking_strategy="fixed"  # or "semantic"
)

result = pipeline.run()
```

### 2. Step-by-Step

```python
from ingestion_pipeline import DocumentParser, FixedSizeChunking, ChunkingPipeline

# Step 1: Parse documents
parser = DocumentParser("documents")
documents = parser.parse_directory()

# Step 2: Apply chunking
pipeline = ChunkingPipeline(strategy="fixed")
chunks = pipeline.process_documents(documents)

# Step 3: Save results
pipeline.save_chunks_to_json(chunks, "output/chunks.json")
```

## Configuration

### Document Parser
```python
from ingestion_pipeline import DocumentParser

parser = DocumentParser("documents_dir")

# Valid departments (enforced)
# - Engineering
# - HR
# - Operations
# - Support

# Valid categories (enforced)
# - Policy
# - Ticket
# - Guide
```

### Fixed-Size Chunking
```python
from ingestion_pipeline import FixedSizeChunking

chunker = FixedSizeChunking(
    chunk_size=500,   # Characters per chunk
    overlap=50        # Character overlap
)
```

### Semantic Chunking
```python
from ingestion_pipeline import SemanticChunking

chunker = SemanticChunking(
    model_name="all-MiniLM-L6-v2",  # HuggingFace model
    target_size=500                   # Target chunk size
)
```

## Output Format

### JSON Structure
```json
{
  "pipeline_metadata": {
    "total_documents": 2,
    "total_chunks": 12,
    "chunking_strategy": "fixed",
    "avg_chunk_size": 450
  },
  "documents_summary": [
    {
      "document_name": "document_name",
      "department": "Engineering",
      "category": "Guide",
      "version": "1.0",
      "chunk_count": 6
    }
  ],
  "chunks": [
    {
      "chunk_id": "uuid-string",
      "document_name": "document_name",
      "department": "Engineering",
      "category": "Guide",
      "version": "1.0",
      "strategy": "fixed_size",
      "text": "chunk content",
      "start_pos": 0,
      "end_pos": 500,
      "size": 500
    }
  ]
}
```

## Testing

```bash
# Run all tests
python -m pytest ingestion_pipeline/tests/test_pipeline.py -v

# Or with unittest
python ingestion_pipeline/tests/test_pipeline.py

# Verify outputs
python ingestion_pipeline/tests/verify_pipeline.py
```

## Integration with RAG Systems

### MongoDB Example
```python
import json
from pymongo import MongoClient

# Run pipeline
pipeline = IngestionPipeline("documents", "output", "fixed")
result = pipeline.run()

# Load JSON
with open(result['output_file']) as f:
    data = json.load(f)

# Insert into MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["rag_db"]
chunks_collection = db["chunks"]
chunks_collection.insert_many(data["chunks"])
```

### Pinecone Example
```python
import json
from pinecone import Pinecone

# Run pipeline and get chunks
pipeline = IngestionPipeline("documents", "output", "semantic")
result = pipeline.run()

with open(result['output_file']) as f:
    data = json.load(f)

# Initialize Pinecone
pc = Pinecone(api_key="your-key")
index = pc.Index("your-index")

# Upsert chunks (you'll need embeddings)
for chunk in data["chunks"]:
    # Generate embedding (use your embedding model)
    embedding = your_embedding_model(chunk["text"])
    
    index.upsert([(
        chunk["chunk_id"],
        embedding,
        {"text": chunk["text"], "metadata": {...}}
    )])
```

## Directory Organization

After integration, your project structure might look like:

```
your-project/
├── ingestion_pipeline/         # This module
│   ├── src/
│   ├── tests/
│   ├── docs/
│   ├── config/
│   ├── data/
│   └── output/
├── src/
│   └── your_code/
├── vector_db/                  # Vector database integration
├── rag_system/                 # RAG implementation
└── main.py
```

## Usage Examples

### Example 1: Process Documents
```python
from ingestion_pipeline import IngestionPipeline

pipeline = IngestionPipeline("documents", "chunks", "fixed")
result = pipeline.run()
```

### Example 2: Custom Chunking
```python
from ingestion_pipeline import DocumentParser, FixedSizeChunking

parser = DocumentParser("docs")
docs = parser.parse_directory()

chunker = FixedSizeChunking(chunk_size=1000, overlap=200)
for doc in docs:
    chunks = chunker.chunk(doc["text_content"], doc["document_name"])
```

### Example 3: Strategy Comparison
```python
from ingestion_pipeline import IngestionPipeline

for strategy in ["fixed", "semantic"]:
    pipeline = IngestionPipeline("docs", f"output_{strategy}", strategy)
    result = pipeline.run()
    print(f"{strategy}: {result['chunks']} chunks")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | Install deps: `pip install -r ingestion_pipeline/config/requirements.txt` |
| No documents found | Check data folder structure and file extensions (.pdf or .txt) |
| Slow semantic chunking | First run downloads 150MB model; subsequent runs are faster |
| Memory issues | Use fixed-size chunking or process smaller batches |

## Documentation

Detailed documentation is in the `docs/` folder:

- **docs/README.md** - Project overview
- **docs/QUICK_START.md** - 5-minute setup
- **docs/EXAMPLES.md** - 20+ code examples
- **docs/README_PIPELINE.md** - Technical reference
- **docs/IMPLEMENTATION_SUMMARY.md** - Architecture details

## Support

- Check **docs/QUICK_START.md** for common tasks
- See **docs/EXAMPLES.md** for code patterns
- Run tests with `python ingestion_pipeline/tests/test_pipeline.py`

---

**Ready to integrate!** Start with the basic usage examples above.
