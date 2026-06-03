# RAG Module - Enterprise RAG Assistant

Production-ready Python implementation of the Retrieval-Augmented Generation (RAG) layer for the Technical Support Copilot.

## 🎯 Overview

This folder contains all RAG-related functionality including:
- Document ingestion pipeline
- Embedding generation
- Vector search implementation
- Semantic chunking strategies
- Query system with hallucination control
- Metadata filtering

## 📁 Structure

```
rag/
├── embedding_service.py        # OpenAI embedding generation
├── vector_db_init.py           # Qdrant vector database setup
├── hybrid_search.py            # Vector + keyword search
├── query_system.py             # Query orchestration
├── ask_questions.py            # Interactive query interface
├── qdrant_setup.py             # Qdrant configuration
│
├── examples/
│   └── basic_usage.py          # Example implementations
│
├── tests/
│   ├── test_simple.py          # Basic functionality tests
│   └── test_vector_search.py   # Vector search tests
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd rag
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Add your OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

### 3. Initialize Vector Database

```bash
python vector_db_init.py
```

### 4. Run Tests

```bash
python test_simple.py
python test_vector_search.py
```

## 🔌 Components

### Embedding Service (`embedding_service.py`)
Generates embeddings using OpenAI's API
- Handles text chunking
- Batch processing
- Error handling

### Vector Database (`vector_db_init.py`)
Sets up Qdrant for vector storage
- Collection creation
- Index configuration
- Connection management

### Hybrid Search (`hybrid_search.py`)
Combines vector and keyword search
- Vector similarity search
- BM25 keyword search
- Result ranking and fusion

### Query System (`query_system.py`)
Orchestrates the full query flow
- Query processing
- Retrieval
- LLM response generation
- Source attribution

## 🔗 Integration with Backend

The RAG module integrates with the backend API:

**API Flow:**
```
Frontend → Backend API → RAG Module → LLM → Response
```

**Backend Endpoints for RAG:**
- `POST /rag/query` - Simple query
- `POST /rag/query-advanced` - Advanced query with strategy control
- `POST /chunks/search` - Search chunks

## 📊 Technologies

- **Vector Database**: Qdrant (fast, easy to use)
- **Embeddings**: OpenAI API (text-embedding-3-small)
- **LLM**: OpenAI GPT (gpt-4-turbo or gpt-3.5-turbo)
- **Search**: Hybrid (vector + BM25)
- **Languages**: Python 3.8+

## 🧪 Testing

```bash
# Run all tests
python test_simple.py
python test_vector_search.py

# Test specific features
python -m pytest tests/ -v
```

## 📝 Features

### Implemented
- ✅ Embedding generation
- ✅ Vector search
- ✅ Hybrid search (vector + keyword)
- ✅ Query processing
- ✅ Source attribution
- ✅ Hallucination control
- ✅ Metadata filtering
- ✅ Error handling

### Documentation
- ✅ FULL_SYSTEM_FLOW.md - Complete system architecture
- ✅ HALLUCINATION_CONTROL.md - Anti-hallucination strategies
- ✅ QUERY_TEST_LEAVE_POLICY.md - Example queries and results

## 🔐 Security

- Environment variables for API keys (never commit credentials)
- Qdrant API key management
- Input validation
- Rate limiting ready

## 📈 Performance

- Vector search: < 100ms for typical queries
- Embedding generation: ~0.5s per document
- Batch processing support
- Caching ready

## 🤝 Integration Checklist

- [ ] Qdrant running and accessible
- [ ] OpenAI API key configured
- [ ] Backend API running
- [ ] Environment variables set
- [ ] Tests passing
- [ ] Embedding service tested
- [ ] Vector search working
- [ ] Query system operational
- [ ] Source attribution working
- [ ] Hallucination control active

## 📚 Further Reading

- **FULL_SYSTEM_FLOW.md** - How all components work together
- **HALLUCINATION_CONTROL.md** - Anti-hallucination strategies
- **vector_db_init.py** - Database setup details
- **hybrid_search.py** - Search algorithm details

## 🐛 Troubleshooting

**Embedding API errors?**
- Check OpenAI API key in `.env`
- Verify API key has access to embedding models
- Check rate limits

**Qdrant connection failed?**
- Ensure Qdrant is running: `docker ps`
- Check connection URL in config
- Verify API key if using cloud

**Search returning no results?**
- Check vector database is populated
- Verify metadata filters
- Check similarity threshold

## 📞 Support

For RAG-specific issues:
1. Check `HALLUCINATION_CONTROL.md` for common issues
2. Run `test_vector_search.py` to diagnose
3. Review `FULL_SYSTEM_FLOW.md` for architecture

## Status

🟢 **RAG Layer Ready** - All core components implemented and tested

Last Updated: June 4, 2024
