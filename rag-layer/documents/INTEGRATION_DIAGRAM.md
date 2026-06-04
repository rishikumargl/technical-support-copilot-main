# Frontend-Backend Integration Diagram

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                            │
│                      Port 3000                                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ChatInterface.js                                        │  │
│  │  ========================                                │  │
│  │  User types question                                    │  │
│  │  onClick → handleQuery()                                │  │
│  │  Calls: queryRAGAdvanced(query, options)                │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │  ragApi.js                                               │  │
│  │  ========================                                │  │
│  │  queryRAGAdvanced(query, options) {                      │  │
│  │    client.post('/rag/query-advanced', {                 │  │
│  │      query,                                              │  │
│  │      retrieval_strategy: options.strategy,              │  │
│  │      top_k: options.topK,                               │  │
│  │      similarity_threshold: options.threshold,           │  │
│  │      filters: options.filters,                          │  │
│  │      rerank: options.rerank                             │  │
│  │    })                                                    │  │
│  │  }                                                       │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │  client.js (axios)                                       │  │
│  │  ========================                                │  │
│  │  API_BASE_URL = http://localhost:5000/api               │  │
│  │  Full URL: http://localhost:5000/api/rag/query-advanced │  │
│  │  Method: POST                                            │  │
│  │  Headers: { Content-Type: application/json }            │  │
│  │  Timeout: 30000ms                                        │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
└─────────────────┼───────────────────────────────────────────────┘
                  │
                  │ HTTP POST REQUEST
                  │ Content-Type: application/json
                  │ Body: { query, retrieval_strategy, top_k, ... }
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (Node.js)                           │
│                       Port 5000                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  index.js (Express Server)                              │  │
│  │  ========================                                │  │
│  │  app.use(cors({                                         │  │
│  │    origin: 'http://localhost:3000'  ✅ ALLOWS FRONTEND  │  │
│  │  }))                                                    │  │
│  │                                                         │  │
│  │  app.use('/api/rag', ragRouter)                        │  │
│  │  Routes incoming request to rag.js                     │  │
│  └──────────────┬──────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼──────────────────────────────────────────┐  │
│  │  routes/rag.js                                           │  │
│  │  ========================                                │  │
│  │  router.post('/query-advanced', async (req, res) => {   │  │
│  │    // Receives request                                  │  │
│  │    const {                                              │  │
│  │      query,              ✅ FROM FRONTEND               │  │
│  │      retrieval_strategy,                                │  │
│  │      top_k,                                             │  │
│  │      similarity_threshold,                              │  │
│  │      filters,                                           │  │
│  │      rerank                                             │  │
│  │    } = req.body;                                        │  │
│  │                                                         │  │
│  │    // Validate                                          │  │
│  │    if (!query) {                                        │  │
│  │      return res.status(400).json({error: '...'})       │  │
│  │    }                                                    │  │
│  │                                                         │  │
│  │    // Try RAG server                                    │  │
│  │    const ragResult = await queryRAGServer(              │  │
│  │      '/query-advanced', {                              │  │
│  │        query,                                           │  │
│  │        retrieval_strategy,                              │  │
│  │        top_k,                                           │  │
│  │        ...                                              │  │
│  │      }                                                  │  │
│  │    )                                                    │  │
│  │                                                         │  │
│  │    // Format response                                  │  │
│  │    const response = {                                   │  │
│  │      answer: ragResult.answer || '...',                │  │
│  │      sources: ragResult.sources || [],                 │  │
│  │      confidence_score: ragResult.confidence_score,     │  │
│  │      status: 'RAG_IMPLEMENTED',                         │  │
│  │      message: '...',                                    │  │
│  │      retrieval_time_ms: Date.now() - startTime        │  │
│  │    }                                                    │  │
│  │                                                         │  │
│  │    // Cache result                                      │  │
│  │    cache.set(cacheKey, response)                        │  │
│  │                                                         │  │
│  │    // Save to DB                                        │  │
│  │    await Response.create({...})                         │  │
│  │                                                         │  │
│  │    // Send back to frontend ✅                          │  │
│  │    res.json(response)                                   │  │
│  │  })                                                     │  │
│  └──────────────┬──────────────────────────────────────────┘  │
│                 │                                               │
└─────────────────┼───────────────────────────────────────────────┘
                  │
                  │ HTTP 200 RESPONSE
                  │ Content-Type: application/json
                  │ Body: { answer, sources, confidence_score, status, ... }
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                            │
│                      Port 3000                                  │
│                                                                 │
│  ┌──────────────┬───────────────────────────────────────────┐  │
│  │  ragApi.js (response handler)                            │  │
│  │  ========================                                │  │
│  │  Returns: response (full response object)                │  │
│  │  Extracts: answer, sources, confidence_score, status    │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │  ChatInterface.js (response display)                     │  │
│  │  ========================                                │  │
│  │  const response = await queryRAGAdvanced(...)            │  │
│  │                                                         │  │
│  │  const assistantMessage = {                             │  │
│  │    content: response.answer,        ✅ USED             │  │
│  │    sources: response.sources,       ✅ USED             │  │
│  │    confidence: response.confidence_score,  ✅ USED      │  │
│  │    status: response.status,         ✅ USED             │  │
│  │    message: response.message,       ✅ USED             │  │
│  │    strategy: filters.strategy                           │  │
│  │  }                                                      │  │
│  │                                                         │  │
│  │  setMessages((prev) => [...prev, assistantMessage])     │  │
│  │  // Renders new message with all data                   │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │  ChatMessage.js (display component)                      │  │
│  │  ========================                                │  │
│  │  Renders:                                               │  │
│  │  - Answer text                                          │  │
│  │  - Source documents                                     │  │
│  │  - Confidence score as percentage                       │  │
│  │  - Retrieval status                                     │  │
│  │  - Feedback buttons                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  User sees answer with sources and confidence score!           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Request-Response Mapping

### Frontend → Backend Request

```javascript
Frontend sends:
{
  "query": "How do I fix CrashLoopBackOff?",
  "retrieval_strategy": "hybrid",
  "top_k": 5,
  "similarity_threshold": 0.5,
  "filters": {
    "department": "Engineering"
  },
  "rerank": false
}

↓ HTTP POST to /api/rag/query-advanced

Backend receives as:
req.body = {
  query: "How do I fix CrashLoopBackOff?",
  retrieval_strategy: "hybrid",
  top_k: 5,
  similarity_threshold: 0.5,
  filters: { department: "Engineering" },
  rerank: false
}
```

### Backend → Frontend Response

```javascript
Backend sends:
{
  "answer": "CrashLoopBackOff is a Kubernetes pod status that...",
  "sources": [
    {
      "document_name": "troubleshooting_guide",
      "chunk": "CrashLoopBackOff occurs when a pod...",
      "relevance_score": 0.92,
      "metadata": {
        "department": "Engineering",
        "category": "Guide",
        "version": "1.0"
      }
    }
  ],
  "confidence_score": 0.92,
  "status": "RAG_IMPLEMENTED",
  "message": "Retrieved from RAG system with embeddings and hybrid search.",
  "retrieval_time_ms": 245
}

↓ HTTP 200 with JSON

Frontend receives as:
response = {
  answer: "CrashLoopBackOff is...",
  sources: [...],
  confidence_score: 0.92,
  status: "RAG_IMPLEMENTED",
  message: "Retrieved from RAG system...",
  retrieval_time_ms: 245
}

Creates assistantMessage:
{
  type: "assistant",
  content: response.answer,
  sources: response.sources,
  confidence: response.confidence_score,
  status: response.status,
  message: response.message,
  ...
}
```

---

## 🔐 CORS Integration

```
Frontend Origin:  http://localhost:3000
Backend Allows:   http://localhost:3000 ✅

Methods Allowed:
  - GET    ✅
  - POST   ✅ (Used for queries)
  - PUT    ✅
  - DELETE ✅
  - OPTIONS ✅

Headers Allowed:
  - Content-Type     ✅
  - Authorization    ✅
```

---

## 🎯 Integration Points Summary

| # | Component | Request | Response | Status |
|---|-----------|---------|----------|--------|
| 1 | ChatInterface | Query string | Response object | ✅ Connected |
| 2 | ragApi.js | Formatted data | Axios response | ✅ Connected |
| 3 | axios client | POST request | JSON data | ✅ Connected |
| 4 | Network | HTTP request | HTTP response | ✅ Connected |
| 5 | Express CORS | Request origin | Allow headers | ✅ Connected |
| 6 | rag.js route | Parse body | Send JSON | ✅ Connected |
| 7 | RAG logic | Process data | Format response | ✅ Connected |
| 8 | Response handler | Parse JSON | Update state | ✅ Connected |
| 9 | ChatMessage | Display data | Render UI | ✅ Connected |

---

## ✅ Verification Checklist

### Frontend Side
- ✅ axios configured with correct baseURL
- ✅ POST requests to /rag/query-advanced
- ✅ Correct field names in request body
- ✅ Response fields properly extracted
- ✅ Error handling implemented
- ✅ Loading states managed
- ✅ Response displays rendered

### Backend Side
- ✅ CORS allows http://localhost:3000
- ✅ Route matches /api/rag/query-advanced
- ✅ Request body properly parsed
- ✅ Response contains all required fields
- ✅ Error handling with proper status codes
- ✅ Timeouts configured
- ✅ Caching implemented

### Network Level
- ✅ Port 3000 to 5000 communication
- ✅ Content-Type: application/json
- ✅ HTTP methods match
- ✅ Status codes 200/400/500 proper
- ✅ CORS headers correct
- ✅ No SSL/TLS issues (localhost)

---

## 🚀 Complete Flow Example

```
User Action:
  Click send on question "How do I fix CrashLoopBackOff?"
  
↓

Frontend (ChatInterface.js):
  query = "How do I fix CrashLoopBackOff?"
  filters.strategy = "hybrid"
  filters.topK = 5
  
↓

API Call (ragApi.js):
  queryRAGAdvanced("How do I fix CrashLoopBackOff?", {
    strategy: "hybrid",
    topK: 5,
    ...
  })
  
↓

HTTP Client (client.js):
  POST http://localhost:5000/api/rag/query-advanced
  Headers: { Content-Type: application/json }
  Body: {
    query: "How do I fix CrashLoopBackOff?",
    retrieval_strategy: "hybrid",
    top_k: 5,
    ...
  }
  
↓

Backend (index.js):
  CORS check: origin = http://localhost:3000 ✅ ALLOWED
  Route match: /api/rag → rag.js
  
↓

Backend (rag.js):
  Extract: query, retrieval_strategy, top_k, ...
  Validate: query not empty ✅
  Call RAG server for answer
  Format response
  Cache result
  Log to database
  
↓

HTTP Response (200 OK):
  {
    answer: "CrashLoopBackOff is...",
    sources: [...],
    confidence_score: 0.92,
    status: "RAG_IMPLEMENTED",
    message: "Retrieved from RAG system...",
    retrieval_time_ms: 245
  }
  
↓

Frontend (ragApi.js):
  response = parsed JSON
  return response.data
  
↓

Frontend (ChatInterface.js):
  response received successfully
  Create assistantMessage with:
    - content: response.answer
    - sources: response.sources
    - confidence: response.confidence_score
    - status: response.status
  
↓

Frontend (ChatMessage.js):
  Render message with:
    - Answer text in main area
    - Sources list below
    - Confidence percentage
    - Feedback buttons
  
↓

User sees:
  "CrashLoopBackOff is..."
  Sources: troubleshooting_guide (92% confidence)
  Feedback buttons: [👍] [👎]
```

---

## 🎉 Integration Result

✅ **Frontend and Backend are perfectly integrated!**

They work together seamlessly with:
- Clear API contract
- Proper data format agreement
- Error handling on both sides
- CORS properly configured
- No mismatches or conflicts

Both developers can continue working independently because the integration is solid!

---

**Last Verified:** June 4, 2026  
**Status:** ✅ FULLY INTEGRATED AND VERIFIED
