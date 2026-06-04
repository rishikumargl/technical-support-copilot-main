# RAG Layer Setup and Integration Guide

Complete guide to setting up the integrated RAG system and connecting the ingestion pipeline with the query layer.

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd rag-layer
pip install -r requirements.txt
```

**What gets installed:**
- `qdrant-client` - Vector database
- `sentence-transformers` - Embedding models
- `numpy` - Numerical computing
- `rank-bm25` - BM25 search algorithm
- `pydantic` - Data validation
- `python-dotenv` - Environment configuration
- `pypdf` - PDF parsing

### Step 2: Run the Full Pipeline

```bash
# Option A: Using the integration pipeline (recommended)
python rag-layer/integration_pipeline.py

# Option B: Using query system (if you have pre-computed embeddings)
python rag-layer/query_system.py

# Option C: From Python code
python -c "
from rag_layer import RAGIntegrationPipeline
pipeline = RAGIntegrationPipeline(
    source_dir='rag-layer/ingestion_pipeline/data'
)
result = pipeline.run_full_pipeline()
print(f'Processed {result[\"documents_ingested\"]} documents')
"
```

### Step 3: Test a Query

```bash
python -c "
from rag_layer import ask
ask('What are the system requirements?')
"
```

## 📁 What Gets Created

After running the pipeline, you'll have:

```
rag-layer/
├── output/
│   ├── ingestion_output_fixed.json    # Parsed & chunked documents
│   └── ingestion_output_semantic.json # (If using semantic chunking)
│
├── qdrant_storage/                    # Vector database
│   └── collections/
│       └── enterprise_chunks/         # Stored embeddings
│
├── .env                               # (Optional) Configuration
└── logs/                              # (Optional) System logs
```

## 🔄 Integration Architecture

The RAG layer now integrates two independently developed components:

### Developer 1: Ingestion Pipeline
- **Files**: `ingestion_pipeline/` directory
- **Responsibility**: Document parsing & chunking
- **Output**: JSON with chunks ready for embedding
- **Key classes**: `DocumentParser`, `FixedSizeChunking`, `SemanticChunking`

### Developer 2: Query/Embedding Layer
- **Files**: `embedding_service.py`, `qdrant_setup.py`, `hybrid_search.py`
- **Responsibility**: Vector storage & retrieval
- **Input**: Chunks from ingestion pipeline
- **Key classes**: `EmbeddingService`, `QdrantDB`, `HybridSearchEngine`

### Integration Bridge
- **File**: `integration_pipeline.py` (NEW)
- **Responsibility**: Connects both components
- **Orchestrates**: Ingest → Embed → Store → Query
- **Main class**: `RAGIntegrationPipeline`

## 📊 Data Flow

```
1. Document Ingestion (Peer 1)
   └─> Reads .txt/.pdf files
   └─> Extracts metadata
   └─> Saves chunks to JSON

2. Embedding Service (Peer 2)
   └─> Loads JSON chunks
   └─> Generates vectors
   └─> Returns embedded chunks

3. Vector Storage (Peer 2)
   └─> Creates Qdrant collection
   └─> Stores vectors with metadata
   └─> Builds indices

4. Hybrid Search (Peer 2)
   └─> Accepts queries
   └─> Performs dense + sparse search
   └─> Returns ranked results

5. Query Interface
   └─> Simple ask() function
   └─> OR full RAGIntegrationPipeline API
```

## 🛠️ Component Integration Details

### Ingestion → Embedding Connection

**What the ingestion pipeline produces:**
```json
{
  "chunks": [
    {
      "chunk_id": "uuid",
      "document_name": "doc_name",
      "department": "Engineering",
      "category": "Guide",
      "text": "chunk content here...",
      "start_pos": 0,
      "end_pos": 500
    }
  ]
}
```

**Integration pipeline processes this by:**
1. Loading the JSON file
2. Extracting all chunks
3. Sending to EmbeddingService
4. Storing results in Qdrant
5. Building BM25 index

### Embedding → Qdrant Connection

**EmbeddingService converts chunks:**
```python
chunks = [
    {"text": "...", "chunk_id": "...", ...}
]

# Returns:
chunks = [
    {
        "text": "...", 
        "chunk_id": "...",
        "embedding": [0.123, 0.456, ...],  # 384-dimensional vector
        ...
    }
]
```

**Qdrant stores with metadata:**
```python
PointStruct(
    id=0,
    vector=[0.123, 0.456, ...],  # 384 dimensions
    payload={
        "chunk_id": "uuid",
        "document_name": "doc_name",
        "department": "Engineering",
        "category": "Guide",
        "text": "chunk content..."
    }
)
```

### Search Engine Integration

**HybridSearchEngine combines:**
1. **Dense Search** (vector similarity)
   - Uses EmbeddingService to embed query
   - Searches Qdrant for nearest vectors
   - Returns cosine similarity scores

2. **Sparse Search** (BM25 ranking)
   - Uses BM25Okapi on chunk texts
   - Returns ranking scores

3. **Hybrid Scoring**
   - Combines both scores: 0.6*dense + 0.4*sparse
   - Returns ranked results

## 🔐 Dependencies Between Components

```
integration_pipeline.py
├── imports: IngestionPipeline (src/)
├── imports: EmbeddingService
├── imports: QdrantDB
├── imports: HybridSearchEngine
└── orchestrates all components

query_system.py
├── imports: QdrantDB
├── imports: HybridSearchEngine
└── provides simple ask() interface

__init__.py (NEW)
├── exports: RAGIntegrationPipeline
├── exports: EmbeddingService
├── exports: QdrantDB
├── exports: HybridSearchEngine
├── exports: ask()
└── exports: initialize()
```

## 📝 Configuration Options

### Environment Variables (.env)

```env
# Optional: Hugging Face API token
HF_TOKEN=your_token_here

# Database
QDRANT_STORAGE=./qdrant_storage

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Ingestion
SOURCE_DIR=ingestion_pipeline/data
OUTPUT_DIR=output
CHUNKING_STRATEGY=fixed  # or "semantic"
```

### Python Configuration

```python
from rag_layer import RAGIntegrationPipeline

# Full customization
pipeline = RAGIntegrationPipeline(
    # Ingestion settings
    source_dir="documents",
    output_dir="output",
    chunking_strategy="fixed",      # or "semantic"
    
    # Embedding settings
    embedding_model="all-MiniLM-L6-v2",
    hf_token=None,
    
    # Database settings
    qdrant_storage="./qdrant_storage",
)
```

## 🧪 Testing the Integration

### 1. Verify Imports

```bash
python -c "from rag_layer import RAGIntegrationPipeline; print('✓ Imports OK')"
```

### 2. Run Full Pipeline Test

```bash
python rag-layer/test_integration.py
```

### 3. Test with Sample Data

```python
from rag_layer import RAGIntegrationPipeline

pipeline = RAGIntegrationPipeline(
    source_dir="rag-layer/ingestion_pipeline/data"
)

# Run pipeline
result = pipeline.run_full_pipeline()
print(f"Documents: {result['documents_ingested']}")
print(f"Chunks: {result['chunks_created']}")
print(f"Vectors stored: {result['vectors_stored']}")

# Test query
results = pipeline.query("What are the system requirements?")
for r in results:
    print(f"- {r['document_name']}: {r['combined_score']:.1%}")
```

## 📚 Usage Examples

### Example 1: Full Pipeline

```python
from rag_layer import RAGIntegrationPipeline

pipeline = RAGIntegrationPipeline()
pipeline.run_full_pipeline()

results = pipeline.query("Your question here?")
```

### Example 2: Simple Query Interface

```python
from rag_layer import ask

results = ask(
    "What is the remote work policy?",
    department="HR",
    category="Policy"
)

for result in results:
    print(result['text'])
```

### Example 3: Step-by-Step Processing

```python
from rag_layer import (
    DocumentParser,
    FixedSizeChunking,
    EmbeddingService,
    QdrantDB
)

# Parse
parser = DocumentParser("documents")
docs = parser.parse_directory()

# Chunk
chunker = FixedSizeChunking()
chunks = chunker.process_documents(docs)

# Embed
embedder = EmbeddingService()
chunks = embedder.embed_chunks(chunks)

# Store
db = QdrantDB()
db.create_collection()
# ... store chunks
```

## 🔗 Backend Integration Example

To integrate with your FastAPI/Flask backend:

```python
# backend/rag_routes.py
from fastapi import APIRouter
from rag_layer import RAGIntegrationPipeline

router = APIRouter(prefix="/api/rag", tags=["rag"])

# Initialize once at startup
pipeline = RAGIntegrationPipeline()

@router.post("/search")
async def search(question: str, department: str = None):
    results = pipeline.query(
        question=question,
        department=department,
        top_k=5
    )
    return {
        "question": question,
        "results": results
    }

@router.post("/ask")
async def ask(question: str):
    from rag_layer import ask as ask_kb
    results = ask_kb(question, print_results=False)
    return {"results": results}
```

## 🐛 Troubleshooting

### Error: "No module named 'rag_layer'"

**Solution:**
```bash
# Ensure you're in the right directory
cd project-root
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/rag-layer"
```

### Error: "pypdf not installed"

**Solution:**
```bash
pip install -r rag-layer/requirements.txt
```

### Error: "Collection already exists"

**Solution:** Normal message. It means the database is reusing the existing collection.
```bash
# To reset: Delete the storage directory
rm -rf qdrant_storage/
# Then run pipeline again
```

### Error: "No documents found"

**Causes:**
- Source directory is empty
- Files don't match expected naming pattern
- Wrong file types (only .txt and .pdf are supported)

**Solution:**
```python
from pathlib import Path
docs = Path("documents")
files = list(docs.glob("**/*.txt")) + list(docs.glob("**/*.pdf"))
print(f"Found {len(files)} files")
```

### Slow embedding generation

**Note:** First run downloads ~150MB model, subsequent runs are fast.

**To speed up:**
- Use fixed-size chunking instead of semantic
- Process smaller batches
- Use GPU (see sentence-transformers docs)

## 📖 Documentation Files

- **INTEGRATION.md** - Complete integration guide
- **SETUP_AND_INTEGRATION.md** - This file
- **ingestion_pipeline/README.md** - Ingestion pipeline docs
- **ingestion_pipeline/INTEGRATION_GUIDE.md** - Pipeline integration details
- **FULL_SYSTEM_FLOW.md** - Architecture overview

## ✅ Integration Checklist

- ✅ Ingestion pipeline configured
- ✅ Embedding service initialized
- ✅ Qdrant database setup
- ✅ Hybrid search engine created
- ✅ Query interface exposed
- ✅ Integration bridge implemented
- ✅ Package exports defined
- ✅ Documentation written
- ✅ Tests created
- ✅ Example code provided

## 🎯 Next Steps

1. **Install dependencies**: `pip install -r rag-layer/requirements.txt`
2. **Run full pipeline**: `python rag-layer/integration_pipeline.py`
3. **Test queries**: `python rag-layer/query_system.py`
4. **Integrate with backend**: Use examples from Backend Integration section
5. **Monitor performance**: Check `get_stats()` method
6. **Add your documents**: Place them in source directory

## 📞 Support

- Check documentation files for detailed information
- Review test files for example usage
- See examples/ directory for code patterns
- Run tests: `python rag-layer/test_integration.py`

---

**Status**: Integration Complete  
**Version**: 1.0.0  
**Last Updated**: June 4, 2026  
**Components Integrated**: 2 independent implementations, 1 bridge layer
