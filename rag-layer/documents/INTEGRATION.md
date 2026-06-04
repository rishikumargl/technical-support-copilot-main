# RAG Layer Integration Guide

Complete integration of the ingestion pipeline with the RAG query system. Developed by two different team members, now unified into a working system.

## 📋 Overview

The RAG layer now provides a **complete, end-to-end workflow**:

```
Documents
    ↓
Ingestion Pipeline (parsing + chunking)
    ↓
Embedding Service (vector generation)
    ↓
Qdrant Database (vector storage)
    ↓
Hybrid Search (dense + sparse retrieval)
    ↓
Query Results
```

## 🚀 Quick Start

### Method 1: Full Integration Pipeline (Recommended)

```python
from rag_layer import RAGIntegrationPipeline

# Create pipeline
pipeline = RAGIntegrationPipeline(
    source_dir="ingestion_pipeline/data",
    output_dir="output",
    chunking_strategy="fixed"
)

# Run complete workflow: ingest → embed → store → index
result = pipeline.run_full_pipeline()
print(f"Processed {result['documents_ingested']} documents")
print(f"Created {result['chunks_created']} chunks")
print(f"Stored {result['vectors_stored']} vectors")

# Query the knowledge base
results = pipeline.query("What are the system requirements?")
for r in results:
    print(f"- {r['document_name']}: {r['combined_score']:.1%}")
```

### Method 2: Step-by-Step with Components

```python
from rag_layer import (
    DocumentParser,
    FixedSizeChunking,
    EmbeddingService,
    QdrantDB,
    HybridSearchEngine,
)

# Step 1: Parse documents
parser = DocumentParser("documents")
docs = parser.parse_directory()

# Step 2: Chunk documents
chunker = FixedSizeChunking(chunk_size=500, overlap=50)
chunks = chunker.process_documents(docs)

# Step 3: Generate embeddings
embedding_svc = EmbeddingService()
chunks = embedding_svc.embed_chunks(chunks)

# Step 4: Store in vector DB
db = QdrantDB("./qdrant_storage")
db.create_collection()
# ... insert chunks into Qdrant

# Step 5: Search
search = HybridSearchEngine(db.client)
results = search.retrieve_relevant_chunks(query="your question")
```

### Method 3: Simple Query Interface

```python
from rag_layer import ask, initialize

# Initialize once
initialize()

# Ask questions
results = ask(
    "What is the remote work policy?",
    department="HR",
    category="Policy",
    top_k=5
)

for result in results:
    print(result['text'])
```

## 📁 Directory Structure

```
rag-layer/
├── __init__.py                    # Unified interface
├── integration_pipeline.py         # Bridge connecting all components
├── query_system.py                # Query interface
│
├── embedding_service.py           # Vector generation
├── qdrant_setup.py               # Vector database setup
├── hybrid_search.py              # Search implementation
│
├── ingestion_pipeline/            # Document ingestion
│   ├── __init__.py
│   ├── src/
│   │   ├── document_parser.py
│   │   ├── chunking_strategies.py
│   │   └── ingestion_pipeline.py
│   ├── tests/
│   ├── data/                      # Sample documents
│   └── output/                    # Generated chunks
│
├── INTEGRATION.md                # This file
└── FULL_SYSTEM_FLOW.md           # Architecture details
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the rag-layer directory:

```env
# Hugging Face API token (optional)
HF_TOKEN=your_token_here

# Qdrant configuration
QDRANT_STORAGE=./qdrant_storage

# Embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Ingestion configuration
SOURCE_DIR=ingestion_pipeline/data
OUTPUT_DIR=output
CHUNKING_STRATEGY=fixed  # or "semantic"
```

### Python Configuration

```python
from rag_layer import RAGIntegrationPipeline

pipeline = RAGIntegrationPipeline(
    # Ingestion
    source_dir="documents",
    output_dir="output",
    chunking_strategy="fixed",        # "fixed" or "semantic"
    
    # Embedding
    embedding_model="all-MiniLM-L6-v2",
    hf_token=None,                    # Optional
    
    # Database
    qdrant_storage="./qdrant_storage",
)
```

## 📊 Data Flow

### 1. Document Ingestion
- Reads `.txt` and `.pdf` files from source directory
- Extracts metadata (department, category, version)
- Validates against allowed values:
  - Departments: Engineering, HR, Operations, Support
  - Categories: Policy, Ticket, Guide

### 2. Document Parsing
- Parses text content from files
- Extracts and validates metadata from filename
- Format: `{category}_{department}_{version}.txt`

### 3. Chunking
- **Fixed-size**: 500 characters with 50 character overlap
- **Semantic**: Sentence-aware chunking using NLP

Each chunk includes:
- Unique UUID
- Text content
- Position tracking (start_pos, end_pos)
- Metadata (document_name, department, category, version)

### 4. Embedding
- Uses sentence-transformers (all-MiniLM-L6-v2 by default)
- Converts chunk text to 384-dimensional vectors
- Generates embeddings in batch for efficiency

### 5. Vector Storage
- Stores embeddings in Qdrant with metadata
- Supports filtering by department and category
- Uses cosine similarity for vector search

### 6. Hybrid Search
- **Dense search**: Vector similarity (all-MiniLM embeddings)
- **Sparse search**: BM25 lexical ranking
- **Hybrid**: Combines both scores
- **Filtering**: By department and/or category

## 🔍 Querying

### Basic Query

```python
from rag_layer import ask

results = ask("What are the system requirements?")
```

### Filtered Query

```python
results = ask(
    "What is the leave policy?",
    department="HR",          # Optional
    category="Policy",        # Optional
    top_k=5,                 # Number of results
    search_type="hybrid"     # "hybrid", "dense", "sparse"
)
```

### Processing Results

```python
for result in results:
    print(f"Document: {result['document_name']}")
    print(f"Department: {result['department']}")
    print(f"Category: {result['category']}")
    print(f"Score: {result['combined_score']:.1%}")
    print(f"Text: {result['text']}\n")
```

### Result Fields

- `chunk_id`: Unique identifier
- `document_name`: Source document
- `department`: Engineering, HR, Operations, or Support
- `category`: Policy, Ticket, or Guide
- `version`: Document version
- `text`: Chunk content
- `combined_score`: Hybrid search score (0-1)
- `dense_score`: Vector similarity score
- `sparse_score`: BM25 ranking score
- `start_pos`: Character position in original document
- `end_pos`: Character position in original document

## 📝 Integration Points

### How the Two Implementations Connect

**Ingestion Pipeline** (Peer 1's Work)
- ✅ DocumentParser: Reads and parses files
- ✅ ChunkingStrategies: Splits documents into chunks
- ✅ IngestionPipeline: Orchestrates the workflow
- ✅ Output: JSON with chunks ready for embedding

**RAG Layer** (Peer 2's Work)
- ✅ EmbeddingService: Converts chunks to vectors
- ✅ QdrantDB: Stores vectors with metadata
- ✅ HybridSearchEngine: Searches across vectors and text
- ✅ QuerySystem: Provides simple query interface

**Integration Bridge**
- `integration_pipeline.py`: Connects all components
- Loads ingestion output
- Applies embeddings
- Seeds Qdrant database
- Builds search indices
- Provides unified query interface

## ✅ Testing

### Test the Integration

```bash
# Run full pipeline
python rag-layer/integration_pipeline.py

# Or from Python
python -c "
from rag_layer import RAGIntegrationPipeline
pipeline = RAGIntegrationPipeline(
    source_dir='rag-layer/ingestion_pipeline/data'
)
result = pipeline.run_full_pipeline()
print(result)
"
```

### Run Query Tests

```bash
# Simple interface test
python rag-layer/query_system.py

# Or from Python
from rag_layer import ask
ask('What are the system requirements?')
```

## 🐛 Troubleshooting

### Issue: "No documents found"
- Check that source directory contains `.txt` or `.pdf` files
- Verify filenames follow pattern: `{category}_{department}_{version}.txt`
- Ensure directory path is correct

### Issue: "Collection already exists"
- Normal message - means Qdrant database is reusing existing collection
- Delete `./qdrant_storage` to reset

### Issue: "Failed to load chunks"
- Verify ingestion output JSON exists at the path
- Run ingestion pipeline first if output missing
- Check JSON file is valid with `python -m json.tool output_file.json`

### Issue: "Import error"
- Install dependencies: `pip install -r requirements.txt`
- Ensure all paths are correct
- Verify Python version >= 3.8

### Issue: "Memory error during semantic chunking"
- First run downloads 150MB model (normal)
- For large documents, use fixed-size chunking instead
- Process documents in smaller batches

## 📚 Component APIs

### RAGIntegrationPipeline

```python
pipeline = RAGIntegrationPipeline(
    source_dir: str = "documents",
    output_dir: str = "output",
    qdrant_storage: str = "./qdrant_storage",
    chunking_strategy: str = "fixed",
    embedding_model: str = "all-MiniLM-L6-v2",
    hf_token: Optional[str] = None,
)

# Methods
pipeline.run_full_pipeline() -> Dict       # Run entire pipeline
pipeline.query(...) -> List[Dict]          # Query knowledge base
pipeline.get_stats() -> Dict               # Get database statistics
```

### Query Functions

```python
# Initialize system
from rag_layer import initialize
system = initialize(
    qdrant_storage="./qdrant_storage",
    ingestion_output="./output/ingestion_output_fixed.json",
    use_integration_pipeline=False
)

# Ask questions
from rag_layer import ask
results = ask(
    question: str,
    department: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
    search_type: str = "hybrid",
    print_results: bool = True
) -> List[Dict]
```

## 🔗 Connecting to Backend API

To integrate with the technical-support-copilot backend:

```python
# backend/routes/rag.py
from rag_layer import RAGIntegrationPipeline, ask

# Initialize pipeline once on startup
pipeline = RAGIntegrationPipeline()

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    results = pipeline.query(
        question=data['question'],
        department=data.get('department'),
        category=data.get('category'),
        top_k=data.get('top_k', 5)
    )
    return jsonify(results)

# Or use simple query interface
@app.route('/api/ask', methods=['POST'])
def ask_question():
    question = request.json['question']
    results = ask(question, print_results=False)
    return jsonify(results)
```

## 📖 Documentation

- [Ingestion Pipeline](ingestion_pipeline/README.md)
- [Full System Flow](FULL_SYSTEM_FLOW.md)
- [Hybrid Search Details](ingestion_pipeline/docs/README_PIPELINE.md)
- [Examples](ingestion_pipeline/docs/EXAMPLES.md)

## 🎯 Next Steps

1. ✅ Run the full pipeline once to seed Qdrant
2. ✅ Test queries using the simple interface
3. ✅ Integrate with backend API
4. ✅ Add documents to source directory
5. ✅ Monitor vector database statistics

---

**Status**: Production Ready  
**Last Updated**: June 4, 2026  
**Integration**: Complete and tested
