# RAG Layer - Quick Start Guide

## ⚡ 30-Second Setup

```bash
# 1. Install dependencies
pip install -r rag-layer/requirements.txt

# 2. Run the pipeline
python rag-layer/integration_pipeline.py

# 3. Ask a question
python -c "from rag_layer import ask; ask('What are the system requirements?')"
```

## 📦 What You Get

- ✅ **Documents parsed** from `rag-layer/ingestion_pipeline/data/`
- ✅ **Chunks created** with metadata
- ✅ **Vectors generated** using sentence-transformers
- ✅ **Stored in Qdrant** vector database
- ✅ **Searchable** via hybrid search (dense + sparse)

## 🔍 Query Examples

### Python Code

```python
from rag_layer import RAGIntegrationPipeline

# Initialize
pipeline = RAGIntegrationPipeline()

# Run full pipeline
result = pipeline.run_full_pipeline()

# Query
results = pipeline.query("Your question here?")
for r in results:
    print(f"{r['document_name']}: {r['combined_score']:.1%}")
```

### Simple Interface

```python
from rag_layer import ask

results = ask(
    "What is the remote work policy?",
    department="HR",    # Optional
    category="Policy"   # Optional
)
```

### REST API (Backend Integration)

```python
from fastapi import FastAPI
from rag_layer import RAGIntegrationPipeline

app = FastAPI()
pipeline = RAGIntegrationPipeline()

@app.post("/api/search")
async def search(question: str):
    results = pipeline.query(question)
    return {"results": results}
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `integration_pipeline.py` | Main integration - connect all components |
| `__init__.py` | Package exports for easy imports |
| `query_system.py` | Simple query interface |
| `INTEGRATION.md` | Complete integration guide |
| `SETUP_AND_INTEGRATION.md` | Detailed setup instructions |
| `test_integration.py` | Test suite |

## 🏗️ Architecture

```
Documents → Ingestion → Chunks → Embedding → Storage → Search → Results
```

## 🚀 Common Tasks

### Task: Add more documents
1. Add `.txt` or `.pdf` files to `rag-layer/ingestion_pipeline/data/`
2. Run `python rag-layer/integration_pipeline.py` again

### Task: Change chunking strategy
```python
pipeline = RAGIntegrationPipeline(
    chunking_strategy="semantic"  # or "fixed"
)
```

### Task: Use different embedding model
```python
pipeline = RAGIntegrationPipeline(
    embedding_model="all-mpnet-base-v2"  # other models available
)
```

### Task: Filter by department
```python
results = pipeline.query(
    "setup guide",
    department="Engineering"
)
```

## ✅ Verify Everything Works

```bash
python rag-layer/test_integration.py
```

## 📚 Documentation

- **Quick start**: This file
- **Detailed setup**: `SETUP_AND_INTEGRATION.md`
- **Full integration**: `INTEGRATION.md`
- **Summary**: `INTEGRATION_SUMMARY.md`

## 🆘 Troubleshooting

**Q: "No documents found"**  
A: Add `.txt` or `.pdf` files to `rag-layer/ingestion_pipeline/data/`

**Q: "Module not found"**  
A: Run `pip install -r rag-layer/requirements.txt`

**Q: "Collection already exists"**  
A: Normal - database is reusing existing collection

**Q: "Slow on first run"**  
A: Normal - downloads 150MB embedding model first time

## 🔗 Integration Points

### For Backend API
```python
from rag_layer import RAGIntegrationPipeline

pipeline = RAGIntegrationPipeline()
results = pipeline.query(question)
```

### For Chatbot
```python
from rag_layer import ask

results = ask(question, print_results=False)
response = results[0]['text'] if results else "No answer found"
```

### For CLI Tool
```bash
python -c "
from rag_layer import ask
ask('Your question?')
"
```

## 📊 What Happens During run_full_pipeline()

1. **Parses documents** - Reads `.txt` and `.pdf` files
2. **Extracts metadata** - Gets department, category, version
3. **Creates chunks** - Splits documents (fixed or semantic)
4. **Generates embeddings** - Creates 384-dimensional vectors
5. **Stores in Qdrant** - Saves vectors with metadata
6. **Builds indices** - Creates BM25 index for hybrid search

**Total time**: ~1-2 minutes for sample documents (first run slower)

## 🎯 Status

| Component | Status |
|-----------|--------|
| Ingestion | ✅ Ready |
| Embedding | ✅ Ready |
| Storage | ✅ Ready |
| Search | ✅ Ready |
| Integration | ✅ Ready |
| Tests | ✅ Ready |

## 🚀 Next Step

Run this command:
```bash
python rag-layer/integration_pipeline.py
```

That's it! Your RAG system is now ready to use.

---

For more details, see:
- `INTEGRATION.md` - Full technical documentation
- `SETUP_AND_INTEGRATION.md` - Detailed setup guide
- `test_integration.py` - Example tests
