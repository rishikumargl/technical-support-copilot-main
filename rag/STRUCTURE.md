# RAG Module Structure

Complete directory structure and file organization for the RAG layer.

## Directory Tree

```
rag/
├── README.md                           # Main RAG documentation
├── STRUCTURE.md                        # This file
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── requirements.txt                    # Python dependencies
│
├── Core RAG Components
├─────────────────────────────────────
├── embedding_service.py               # OpenAI embedding wrapper
├── vector_db_init.py                  # Qdrant database setup
├── hybrid_search.py                   # Vector + keyword search
├── query_system.py                    # Query orchestration
├── ask_questions.py                   # Interactive interface
├── qdrant_setup.py                    # Qdrant configuration
│
├── Document Ingestion Pipeline
├─────────────────────────────────────
├── ingestion_pipeline.py              # Main pipeline orchestrator
├── document_parser.py                 # PDF/text parsing
├── chunking_strategies.py             # Fixed & semantic chunking
│
├── ingestion/                         # Ingestion module
│   ├── __init__.py
│   ├── setup.py
│   ├── README.md
│   ├── src/
│   │   ├── document_parser.py
│   │   ├── chunking_strategies.py
│   │   └── ingestion_pipeline.py
│   ├── examples/
│   │   └── basic_usage.py
│   ├── tests/
│   │   ├── test_pipeline.py
│   │   └── verify_pipeline.py
│   ├── config/
│   ├── data/
│   └── output/
│
├── Testing & Validation
├─────────────────────────────────────
├── test_simple.py                    # Basic functionality tests
├── test_vector_search.py             # Vector search tests
├── filtering_examples.py              # Metadata filtering examples
│
├── Documentation
├─────────────────────────────────────
├── FULL_SYSTEM_FLOW.md               # End-to-end system architecture
├── HALLUCINATION_CONTROL.md          # Anti-hallucination strategies
├── QUERY_TEST_LEAVE_POLICY.md        # Example queries & responses
└── examples/
    └── basic_usage.py                # Usage examples
```

## File Descriptions

### Core RAG Files

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `embedding_service.py` | OpenAI embedding API wrapper | ~3KB | ✅ Active |
| `vector_db_init.py` | Qdrant database initialization | ~4KB | ✅ Active |
| `hybrid_search.py` | Vector + BM25 keyword search | ~11KB | ✅ Active |
| `query_system.py` | Query processing & orchestration | ~3KB | ✅ Active |
| `ask_questions.py` | Interactive query interface | ~4KB | ✅ Active |
| `qdrant_setup.py` | Qdrant connection setup | ~4KB | ✅ Active |

### Document Ingestion Pipeline

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `ingestion_pipeline.py` | Main orchestrator | ~7KB | ✅ Active |
| `document_parser.py` | PDF & text file parsing | ~5KB | ✅ Active |
| `chunking_strategies.py` | Fixed & semantic chunking | ~8KB | ✅ Active |

### Testing Files

| File | Purpose | Tests | Status |
|------|---------|-------|--------|
| `test_simple.py` | Basic functionality | 5+ | ✅ Passing |
| `test_vector_search.py` | Vector search | 5+ | ✅ Passing |
| `filtering_examples.py` | Metadata filtering | Examples | ✅ Active |

### Documentation

| File | Topic | Pages | Status |
|------|-------|-------|--------|
| `FULL_SYSTEM_FLOW.md` | System architecture | 15+ | ✅ Complete |
| `HALLUCINATION_CONTROL.md` | Anti-hallucination | 12+ | ✅ Complete |
| `QUERY_TEST_LEAVE_POLICY.md` | Example queries | 4+ | ✅ Complete |

## Module Dependencies

```
embedding_service.py
├── openai
├── os
└── logging

vector_db_init.py
├── qdrant_client
└── os

hybrid_search.py
├── qdrant_client
├── bm25
└── numpy

query_system.py
├── openai
├── vector_db_init
├── hybrid_search
└── logging

ask_questions.py
├── query_system
└── json

ingestion_pipeline.py
├── document_parser
├── chunking_strategies
└── json
```

## Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key

# Vector Database
VECTOR_SIZE=1536
COLLECTION_NAME=documents
```

## Installation Order

1. **Install Python** (3.8+)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure environment**: Copy `.env.example` to `.env`
4. **Initialize Qdrant**: `python vector_db_init.py`
5. **Run tests**: `python test_simple.py`
6. **Start query system**: `python ask_questions.py`

## Data Flow

### Ingestion Flow
```
PDF/Text Files
    ↓
document_parser.py (Extract content & metadata)
    ↓
chunking_strategies.py (Create chunks)
    ↓
embedding_service.py (Generate embeddings)
    ↓
vector_db_init.py (Store in Qdrant)
```

### Query Flow
```
User Query
    ↓
query_system.py (Process & validate)
    ↓
hybrid_search.py (Vector + keyword search)
    ↓
LLM (GPT-4 response generation)
    ↓
ask_questions.py (Format & return response)
```

## Key Features by File

### embedding_service.py
- Batch embedding generation
- Rate limit handling
- Error recovery
- Caching support

### vector_db_init.py
- Collection creation
- Index configuration
- Connection management
- Schema validation

### hybrid_search.py
- Vector similarity search
- BM25 keyword search
- Result fusion & ranking
- Metadata filtering

### query_system.py
- Query validation
- Context assembly
- LLM integration
- Response formatting

### document_parser.py
- PDF extraction (pdfplumber)
- Text file reading
- Metadata validation
- Error handling

### chunking_strategies.py
- Fixed-size chunking (500 chars)
- Semantic chunking (sentence-aware)
- Overlap management
- Position tracking

## Configuration

### Qdrant Collection Schema
```json
{
  "name": "documents",
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "document_id": "text",
    "chunk_id": "text",
    "content": "text",
    "department": "text",
    "category": "text",
    "version": "text"
  }
}
```

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Embed 1 document | ~0.5s | OpenAI API |
| Index document | ~1s | Qdrant write |
| Vector search | <100ms | 10 results |
| Hybrid search | <200ms | Combined |
| LLM response | ~2-3s | GPT-4 |

## Maintenance

### Regular Tasks
- Monitor Qdrant disk usage
- Check OpenAI API usage
- Review error logs
- Test vector quality

### Updates
- Keep OpenAI SDK updated
- Monitor Qdrant releases
- Review prompt engineering

## Integration Points

### Backend API
- `POST /rag/query` → `query_system.py`
- `POST /rag/query-advanced` → `hybrid_search.py`
- `POST /chunks/search` → `hybrid_search.py`

### Database
- Documents → PostgreSQL
- Vectors → Qdrant
- Chunks → PostgreSQL + Qdrant

### Frontend
- Chat queries → Backend API → RAG
- Document upload → Backend → Ingestion → RAG

## Troubleshooting Guide

### Embedding Issues
- Check `embedding_service.py` logs
- Verify OpenAI API key
- Test with `test_simple.py`

### Vector Search Issues
- Check Qdrant connection
- Verify collection exists
- Run `test_vector_search.py`

### Query Issues
- Check `query_system.py` logs
- Verify metadata filters
- Test with example queries

## Status

✅ All RAG components organized and documented
✅ Clear file organization matching frontend/backend structure
✅ Complete integration points documented
✅ Ready for team development

---

Last Updated: June 4, 2024
