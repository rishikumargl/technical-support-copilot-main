# Full Integration Guide - Frontend, Backend, and RAG Layer

Complete end-to-end integration of the Technical Support Copilot system.

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                            │
│  - ChatInterface component                                           │
│  - Document manager                                                  │
│  - Analytics dashboard                                               │
│                                                                       │
│  API Calls: /api/rag/query, /api/rag/query-advanced                 │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
                         HTTP/REST Requests
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND (Node.js/Express)                     │
│  - /api/rag/query                                                    │
│  - /api/rag/query-advanced                                           │
│  - /api/rag/initialize                                               │
│  - /api/rag/stats                                                    │
│  - /api/documents (document management)                              │
│  - /api/feedback (user feedback)                                     │
│                                                                       │
│  RAG Integration:                                                    │
│  - Calls RAG server (http://localhost:5001)                         │
│  - Fallback to keyword search if RAG unavailable                    │
│  - Caching support                                                   │
│  - Database logging                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
                    HTTP Calls to RAG Server
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   RAG SERVER (Python/Flask)                          │
│  - /api/rag/query                                                    │
│  - /api/rag/query-advanced                                           │
│  - /api/rag/initialize                                               │
│  - /api/rag/stats                                                    │
│  - /api/rag/ingest                                                   │
│                                                                       │
│  Bridges to RAG Pipeline:                                            │
│  - Calls integration_pipeline.py                                     │
│  - Uses RAGIntegrationPipeline class                                │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    RAG LAYER (Python)                                │
│  - Ingestion Pipeline                                                │
│  - Embedding Service                                                 │
│  - Qdrant Vector Database                                            │
│  - Hybrid Search Engine                                              │
│  - Query Interface                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js 16+ (for backend)
- Python 3.8+ (for RAG)
- PostgreSQL (for database)
- 8GB RAM minimum

### Step 1: Clone and Install Dependencies

```bash
# Backend dependencies
cd backend
npm install
cd ..

# Frontend dependencies
cd frontend
npm install
cd ..

# RAG layer dependencies
cd rag-layer
pip install -r requirements.txt
cd ..
```

### Step 2: Configure Environment Variables

**Backend (.env file)**
```env
# Backend
PORT=5000
HOST=localhost
CORS_ORIGIN=http://localhost:3000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_assistant
DB_USER=postgres
DB_PASSWORD=your_password

# RAG Server Integration
RAG_SERVER_URL=http://localhost:5001

# Cache
ENABLE_CACHE=true
CACHE_TTL=3600

# API Rate Limiting
API_RATE_LIMIT=100
API_RATE_LIMIT_WINDOW=900000
```

**Frontend (.env file)**
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_RAG_SERVER=http://localhost:5001
```

**RAG Layer (.env file)**
```env
# Python RAG Configuration
QDRANT_STORAGE=./qdrant_storage
EMBEDDING_MODEL=all-MiniLM-L6-v2
HF_TOKEN=  # Optional: Hugging Face token

# RAG Server
RAG_SERVER_PORT=5001
RAG_SERVER_HOST=0.0.0.0
```

### Step 3: Initialize RAG System

```bash
cd rag-layer

# Install dependencies
pip install -r requirements.txt

# Initialize and seed vector database
python integration_pipeline.py

# Start RAG server
python rag_server.py
```

The RAG server will:
1. Load documents from `rag-layer/ingestion_pipeline/data/`
2. Parse and chunk documents
3. Generate embeddings
4. Seed Qdrant database
5. Start Flask server on port 5001

### Step 4: Start Backend

```bash
cd backend

# Development
npm run dev

# Production
npm start
```

Backend will:
1. Initialize database
2. Set up routes
3. Listen on port 5000
4. Connect to RAG server

### Step 5: Start Frontend

```bash
cd frontend

# Development
npm start

# Production
npm run build
npm serve -s build
```

Frontend will:
1. Start on port 3000
2. Open browser automatically
3. Connect to backend API

## 📡 API Endpoints

### RAG Endpoints

#### Query RAG System
```
POST /api/rag/query
Content-Type: application/json

Request:
{
  "question": "How do I fix a CrashLoopBackOff error?",
  "top_k": 5,
  "search_type": "hybrid",
  "department": "Engineering",
  "category": "Guide"
}

Response:
{
  "success": true,
  "answer": "CrashLoopBackOff occurs when a pod...",
  "sources": [
    {
      "document_name": "troubleshooting_guide",
      "chunk": "...",
      "relevance_score": 0.92,
      "metadata": { ... }
    }
  ],
  "confidence_score": 0.92,
  "status": "RAG_IMPLEMENTED",
  "retrieval_time_ms": 125
}
```

#### Advanced Query
```
POST /api/rag/query-advanced
Content-Type: application/json

Request:
{
  "query": "database migration issues",
  "retrieval_strategy": "hybrid",  // "hybrid", "dense", "sparse"
  "top_k": 10,
  "similarity_threshold": 0.5,
  "filters": {
    "department": "Engineering",
    "category": "Guide"
  },
  "rerank": false
}
```

#### Initialize RAG
```
POST /api/rag/initialize

Request:
{
  "source_dir": "ingestion_pipeline/data",
  "chunking_strategy": "fixed"  // "fixed" or "semantic"
}
```

#### Get RAG Stats
```
GET /api/rag/stats

Response:
{
  "success": true,
  "stats": {
    "collection": "enterprise_chunks",
    "points_count": 1250,
    "vector_size": 384,
    "storage_path": "./qdrant_storage"
  }
}
```

### Document Endpoints

#### Upload Document
```
POST /api/documents/upload
Content-Type: multipart/form-data

Form Data:
- file: <file>
- metadata: {"department": "Engineering", "category": "Guide"}
```

#### Search Documents
```
POST /api/chunks/search
Content-Type: application/json

Request:
{
  "query": "error handling",
  "strategy": "hybrid",
  "top_k": 10
}
```

### Feedback Endpoints

#### Submit Feedback
```
POST /api/feedback/{responseId}
Content-Type: application/json

Request:
{
  "helpful": true,
  "comment": "Very helpful answer",
  "tags": ["accurate", "complete"]
}
```

## 🧪 Testing Integration

### Test 1: RAG Server Health
```bash
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "rag-server",
  "rag_initialized": true
}
```

### Test 2: Query Backend
```bash
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I fix a CrashLoopBackOff error?"
  }'
```

### Test 3: Frontend Integration
1. Open http://localhost:3000
2. Navigate to Chat Interface
3. Type a question
4. Verify response comes from RAG system
5. Check confidence scores and sources

### Test 4: End-to-End Flow
1. Upload document via frontend
2. Wait for ingestion
3. Query the system
4. Verify answer includes sources
5. Submit feedback
6. Check analytics

## 🔄 Data Flow Example

User asks: "What are the system requirements?"

```
1. FRONTEND
   - User types question
   - Clicks send
   - Calls API: POST /api/rag/query-advanced
   ↓

2. BACKEND
   - Receives request
   - Validates query
   - Checks cache
   - Calls RAG server: POST http://localhost:5001/api/rag/query
   ↓

3. RAG SERVER
   - Receives query
   - Calls integration_pipeline.query()
   ↓

4. RAG PIPELINE
   - Embeds question vector
   - Searches Qdrant (vector DB)
   - Performs BM25 search
   - Combines results (hybrid)
   - Scores and ranks
   ↓

5. RESULTS FLOW BACK
   - RAG Server returns results
   - Backend processes response
   - Caches result
   - Saves to database
   - Returns to frontend
   ↓

6. FRONTEND
   - Displays answer
   - Shows sources with scores
   - Enables feedback
```

## 🐛 Troubleshooting

### RAG Server Not Responding
```bash
# Check if RAG server is running
curl http://localhost:5001/health

# Check logs
tail -f rag-layer/logs/rag_server.log

# Restart RAG server
cd rag-layer
python rag_server.py
```

### Backend Can't Connect to RAG
```bash
# Check RAG_SERVER_URL in .env
echo $RAG_SERVER_URL

# Test connection
curl -X POST http://localhost:5001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}'

# Fallback will use keyword search if RAG unavailable
```

### Frontend Can't Connect to Backend
```bash
# Check REACT_APP_API_URL in .env
echo $REACT_APP_API_URL

# Check CORS settings in backend
# Default: http://localhost:3000

# Check backend is running
curl http://localhost:5000/health
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -d rag_assistant

# Create database if not exists
createdb rag_assistant

# Initialize schema
cd backend
npm run migrate
```

### Documents Not Found
```bash
# Check data directory
ls -la rag-layer/ingestion_pipeline/data/

# Files must be named: {category}_{department}_{version}.txt
# Example: troubleshooting_engineering_v1.txt
```

## 📈 Performance Optimization

### Caching
```env
# Enable query caching
ENABLE_CACHE=true
CACHE_TTL=3600  # 1 hour

# Clear cache
curl -X POST http://localhost:5000/api/cache/clear
```

### Vector Database Optimization
```python
# Use fixed-size chunking (faster)
pipeline = RAGIntegrationPipeline(chunking_strategy="fixed")

# Increase top_k selectively
# Default: 5, Max: 20
```

### API Rate Limiting
```env
API_RATE_LIMIT=100  # requests
API_RATE_LIMIT_WINDOW=900000  # 15 minutes
```

## 🔐 Security

1. **Input Validation**: All queries validated before processing
2. **Rate Limiting**: Configured on backend
3. **CORS**: Only allow frontend origin
4. **Error Handling**: Sensitive errors not exposed
5. **Logging**: All queries logged for audit
6. **Database**: Query responses stored for analytics

## 📊 Monitoring

### Check System Stats
```bash
curl http://localhost:5000/api/system/stats
```

### View Feedback Analytics
```bash
curl http://localhost:5000/api/feedback/analytics
```

### Monitor Cache Performance
```bash
curl http://localhost:5000/api/cache/stats
```

## 🚀 Deployment

### Development
```bash
# Terminal 1: RAG Server
cd rag-layer && python rag_server.py

# Terminal 2: Backend
cd backend && npm run dev

# Terminal 3: Frontend
cd frontend && npm start
```

### Production
```bash
# Build frontend
cd frontend
npm run build

# Start backend with PM2
pm2 start backend/src/index.js --name rag-backend

# Start RAG server with PM2
pm2 start rag-layer/rag_server.py --name rag-server --interpreter python3

# View logs
pm2 logs
```

### Docker (Optional)
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rag_assistant
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  rag-server:
    build: ./rag-layer
    ports:
      - "5001:5001"
    environment:
      FLASK_ENV: production

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - rag-server

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## 📚 Documentation Files

- **This file**: Full integration guide
- `backend/README.md`: Backend API documentation
- `frontend/README.md`: Frontend component guide
- `rag-layer/INTEGRATION.md`: RAG integration guide
- `rag-layer/SETUP_AND_INTEGRATION.md`: RAG setup guide

## ✅ Integration Checklist

- [ ] RAG layer requirements installed
- [ ] RAG server running on port 5001
- [ ] Backend running on port 5000
- [ ] Frontend running on port 3000
- [ ] Database initialized
- [ ] Documents uploaded
- [ ] Test query works
- [ ] Response shows RAG_IMPLEMENTED status
- [ ] Sources displayed correctly
- [ ] Feedback submission works
- [ ] Cache working
- [ ] Analytics visible

## 🎯 Next Steps

1. Start all three services (see Development section)
2. Upload test documents
3. Run test queries
4. Verify end-to-end flow
5. Check logs for any issues
6. Deploy to production

---

**Version**: 1.0.0  
**Last Updated**: June 4, 2026  
**Status**: Production Ready
