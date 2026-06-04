# Integration Startup Guide

Complete guide to start the full Technical Support Copilot system with all integrations.

## 🎯 Overview

The system consists of 3 services that work together:
1. **RAG Server** (Python/Flask) - Port 5001 - Handles all vector search
2. **Backend** (Node.js/Express) - Port 5000 - REST API and business logic
3. **Frontend** (React) - Port 3000 - User interface

## 📋 Prerequisites

- Node.js 16+ (check: `node --version`)
- Python 3.8+ (check: `python --version` or `python3 --version`)
- PostgreSQL (check: `psql --version`)
- npm (check: `npm --version`)

## 🚀 Quick Start (5 Minutes)

### Terminal 1: RAG Server

```bash
cd rag-layer

# Install dependencies (first time only)
pip install -r requirements.txt

# Run RAG server
python rag_server.py
```

Expected output:
```
[INFO] Starting RAG Server on 0.0.0.0:5001
[INFO] Running on http://localhost:5001
```

### Terminal 2: Backend

```bash
cd backend

# Install dependencies (first time only)
npm install

# Start backend
npm run dev
```

Expected output:
```
[INFO] Server running at http://localhost:5000
[INFO] Database initialized successfully
```

### Terminal 3: Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm start
```

Expected output:
```
Compiled successfully!
You can now view rag-assistant in the browser.
  Local: http://localhost:3000
```

## ✅ Verify Integration

Once all three services are running:

### 1. Check RAG Server Health
```bash
curl http://localhost:5001/health
```

Should return:
```json
{
  "status": "ok",
  "service": "rag-server",
  "rag_initialized": true
}
```

### 2. Check Backend Health
```bash
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "ok",
  "timestamp": "2026-06-04T..."
}
```

### 3. Test RAG Query
```bash
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I fix a CrashLoopBackOff error?"}'
```

Should return:
```json
{
  "answer": "...",
  "sources": [...],
  "confidence_score": 0.92,
  "status": "RAG_IMPLEMENTED",
  "retrieval_time_ms": 125
}
```

### 4. Open Frontend
Navigate to: http://localhost:3000

Click on "Chat Interface" and ask a question to test the full integration.

## 📊 Service Dependency Flow

```
Frontend (React)
    ↓ HTTP calls
    ↓ /api/rag/query
Backend (Node.js)
    ↓ HTTP calls
    ↓ http://localhost:5001/api/rag/query
RAG Server (Python)
    ↓ Uses
Ingestion Pipeline → Embedding → Qdrant → Search
```

## 🔧 Configuration

### Backend (.env)
```env
PORT=5000
CORS_ORIGIN=http://localhost:3000
DB_HOST=localhost
DB_NAME=rag_assistant
DB_USER=postgres
DB_PASSWORD=postgres
RAG_SERVER_URL=http://localhost:5001
ENABLE_CACHE=true
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_RAG_SERVER=http://localhost:5001
```

### RAG Layer (.env)
```env
QDRANT_STORAGE=./qdrant_storage
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_SERVER_PORT=5001
RAG_SERVER_HOST=localhost
```

## 🎯 Testing the Integration

### Test 1: Simple Query
```bash
# In another terminal:
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are system requirements?",
    "top_k": 5
  }'
```

### Test 2: Advanced Query with Filters
```bash
curl -X POST http://localhost:5000/api/rag/query-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database setup",
    "retrieval_strategy": "hybrid",
    "top_k": 10,
    "filters": {
      "department": "Engineering"
    }
  }'
```

### Test 3: Get RAG Stats
```bash
curl http://localhost:5000/api/rag/stats
```

### Test 4: Frontend Chat
1. Go to http://localhost:3000
2. Click "Chat Interface"
3. Type a question
4. Verify response appears
5. Check that confidence scores are displayed
6. Click sources to expand

## 🐛 Troubleshooting

### RAG Server won't start
```bash
# Check Python installation
python --version

# Check Flask is installed
pip list | grep -i flask

# Try installing dependencies again
pip install -r rag-layer/requirements.txt

# Check port 5001 is free
lsof -i :5001  # macOS/Linux
netstat -ano | findstr :5001  # Windows
```

### Backend can't connect to RAG
```bash
# Check RAG server is running
curl http://localhost:5001/health

# Check RAG_SERVER_URL in backend .env
cat backend/.env | grep RAG_SERVER_URL

# Verify it says: http://localhost:5001
```

### Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:5000/health

# Check REACT_APP_API_URL in frontend .env
cat frontend/.env | grep REACT_APP_API_URL

# Verify it says: http://localhost:5000/api
```

### Database errors
```bash
# Check PostgreSQL is running
psql -U postgres

# Create database if missing
createdb rag_assistant

# Check connection
psql -U postgres -d rag_assistant -c "SELECT 1"
```

### "Cannot find documents"
```bash
# Check documents exist
ls -la rag-layer/ingestion_pipeline/data/

# Documents must be named: {category}_{department}_{version}.txt
# Example: troubleshooting_engineering_v1.txt

# Add sample documents if empty
cp rag-layer/ingestion_pipeline/data/HR/v2_remote_policy.txt \
   rag-layer/ingestion_pipeline/data/

# Re-initialize RAG
curl -X POST http://localhost:5000/api/rag/initialize
```

## 📈 Development Workflow

### Making Changes

**RAG Layer Changes:**
1. Edit files in `rag-layer/`
2. RAG server auto-reloads (Flask debug mode)
3. Or restart RAG server manually

**Backend Changes:**
1. Edit files in `backend/src/`
2. nodemon auto-reloads (if using `npm run dev`)
3. Or restart backend manually

**Frontend Changes:**
1. Edit files in `frontend/src/`
2. React hot-reload works automatically
3. Changes appear instantly in browser

### Debugging

**RAG Server:**
```bash
# Enable debug logging
# In rag_server.py, uncomment:
# logging.basicConfig(level=logging.DEBUG)
```

**Backend:**
```bash
# Check logs
cat backend/logs/app.log

# Enable request logging
# In backend/src/utils/logger.js, add debug: true
```

**Frontend:**
```bash
# Browser console (F12)
# Network tab shows API calls
# Check REACT_APP_API_URL in .env
```

## 📊 Architecture Summary

```
┌─────────────────────────────────────┐
│  Frontend (React)                   │
│  - ChatInterface                    │
│  - DocumentManager                  │
│  - Analytics                        │
│  Port: 3000                         │
└──────────────┬──────────────────────┘
               │ HTTP
               ↓
┌─────────────────────────────────────┐
│  Backend (Node.js/Express)          │
│  - /api/rag/query                   │
│  - /api/rag/query-advanced          │
│  - /api/documents/*                 │
│  - /api/feedback/*                  │
│  Port: 5000                         │
└──────────────┬──────────────────────┘
               │ HTTP
               ↓
┌─────────────────────────────────────┐
│  RAG Server (Python/Flask)          │
│  - /api/rag/query                   │
│  - /api/rag/query-advanced          │
│  - /api/rag/initialize              │
│  - /api/rag/stats                   │
│  Port: 5001                         │
└──────────────┬──────────────────────┘
               │ Uses
               ↓
┌─────────────────────────────────────┐
│  RAG Layer (Python)                 │
│  - Ingestion Pipeline               │
│  - Embedding Service                │
│  - Qdrant Vector DB                 │
│  - Hybrid Search                    │
└─────────────────────────────────────┘
```

## 🔍 Monitoring

### Check Service Status
```bash
# RAG Server
curl http://localhost:5001/health

# Backend
curl http://localhost:5000/health

# All at once
for port in 5001 5000 3000; do
  echo "Port $port:"
  curl -s http://localhost:$port/health || echo "DOWN"
done
```

### View Logs

**RAG Server:**
```bash
# Logs to console (watch in terminal)
# Or check: tail -f rag-layer/logs/rag_server.log
```

**Backend:**
```bash
# If running with nodemon:
# Logs to console (watch in terminal)

# Or check: tail -f backend/logs/app.log
```

**Frontend:**
```bash
# Browser console (F12 → Console tab)
# Or check: npm run build for production build
```

## ✅ Integration Checklist

Before considering the system ready:

- [ ] RAG Server running (port 5001)
- [ ] Backend running (port 5000)
- [ ] Frontend running (port 3000)
- [ ] All health checks pass
- [ ] Can query from frontend
- [ ] Response shows "RAG_IMPLEMENTED" status
- [ ] Sources are displayed
- [ ] Confidence scores are shown
- [ ] Feedback submission works
- [ ] No errors in any console/logs

## 📚 Documentation

- **FULL_INTEGRATION_GUIDE.md** - Complete integration guide
- **rag-layer/INTEGRATION.md** - RAG layer details
- **rag-layer/SETUP_AND_INTEGRATION.md** - RAG setup guide
- **backend/README.md** - Backend documentation
- **backend/API_TESTING.md** - API examples
- **frontend/README.md** - Frontend documentation

## 🆘 Getting Help

1. Check troubleshooting section above
2. Review logs in each terminal
3. Verify all services are running
4. Check .env files match the configuration
5. Review documentation files
6. Check port numbers (5001, 5000, 3000)

## 🎉 Success!

Once all services are running and integrated:

1. **Frontend** provides the user interface
2. **Backend** handles API requests and orchestration
3. **RAG Server** handles intelligent search
4. **RAG Layer** provides vector embeddings and hybrid search

The system is fully integrated and ready to use!

---

**Last Updated**: June 4, 2026  
**Status**: Production Ready
