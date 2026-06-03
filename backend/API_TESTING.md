# API Testing Guide

Quick reference for testing all backend endpoints using curl or Postman.

## Health Check

```bash
curl http://localhost:5000/health
```

Expected: `{"status":"ok","timestamp":"..."}`

---

## Document Management

### Upload Document

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@sample.pdf" \
  -F 'metadata={"department":"engineering","category":"troubleshooting","version":"1.0"}'
```

Response:
```json
{
  "document_id": "uuid-here",
  "name": "sample.pdf",
  "chunk_count": 0,
  "status": "uploaded"
}
```

Save the `document_id` for later tests.

### List Documents

```bash
curl http://localhost:5000/api/documents
```

With filters:
```bash
curl "http://localhost:5000/api/documents?department=engineering&category=troubleshooting&skip=0&limit=10"
```

### Get Document Details

```bash
curl http://localhost:5000/api/documents/{document_id}
```

### Get Document Chunks

```bash
curl http://localhost:5000/api/documents/{document_id}/chunks?skip=0&limit=10
```

### Delete Document

```bash
curl -X DELETE http://localhost:5000/api/documents/{document_id}
```

---

## RAG Queries

### Simple Query

```bash
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I fix CrashLoopBackOff?",
    "filters": {"department": "engineering"}
  }'
```

Expected response:
```json
{
  "answer": "...",
  "sources": [
    {
      "document_name": "...",
      "chunk": "...",
      "relevance_score": 0.92,
      "metadata": {...}
    }
  ],
  "confidence_score": 0.85
}
```

### Advanced Query

```bash
curl -X POST http://localhost:5000/api/rag/query-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What causes 502 Bad Gateway?",
    "retrieval_strategy": "hybrid",
    "top_k": 5,
    "similarity_threshold": 0.5,
    "filters": {"department": "support"},
    "rerank": true
  }'
```

---

## Chunk Operations

### Search Chunks

```bash
curl -X POST http://localhost:5000/api/chunks/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "error handling",
    "strategy": "hybrid",
    "top_k": 10
  }'
```

### Batch Get Chunks

```bash
curl -X POST http://localhost:5000/api/chunks/batch \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": ["uuid1", "uuid2"],
    "skip": 0,
    "limit": 50
  }'
```

---

## Feedback Management

### Submit Feedback

Get a response ID first from any RAG query. Response objects have an `id` field.

```bash
curl -X POST http://localhost:5000/api/feedback/{response_id} \
  -H "Content-Type: application/json" \
  -d '{
    "helpful": true,
    "comment": "Very accurate and helpful",
    "tags": ["accurate", "helpful", "clear"]
  }'
```

Response:
```json
{
  "id": "feedback-uuid",
  "response_id": "response-uuid",
  "helpful": true,
  "created_at": "..."
}
```

### Get Feedback Analytics

```bash
curl http://localhost:5000/api/feedback/analytics
```

With date filters:
```bash
curl "http://localhost:5000/api/feedback/analytics?startDate=2024-06-01&endDate=2024-06-30"
```

Expected response:
```json
{
  "helpful_count": 145,
  "unhelpful_count": 23,
  "total_feedback": 168,
  "helpful_percentage": "86.3",
  "unhelpful_percentage": "13.7",
  "most_common_tags": ["helpful", "clear", "accurate"],
  "ratings_by_strategy": {
    "vector": "0.82",
    "bm25": "0.75",
    "hybrid": "0.88"
  }
}
```

---

## System Statistics

### Get System Stats

```bash
curl http://localhost:5000/api/system/stats
```

Expected response:
```json
{
  "total_documents": 45,
  "total_chunks": 1250,
  "avg_chunk_size": 512,
  "index_size": 52428800,
  "avg_response_time": 234,
  "uptime_hours": 168.5,
  "retrieval_strategies": {
    "vector": {
      "accuracy": "0.92",
      "precision": "0.88",
      "avg_time": 145
    }
  },
  "documents_by_department": {
    "engineering": 20,
    "support": 15
  }
}
```

### Compare Retrieval Strategies

```bash
curl -X POST http://localhost:5000/api/system/retrieval-comparison \
  -H "Content-Type: application/json" \
  -d '{"query": "How to fix ImagePullBackOff?"}'
```

### Compare Chunking Strategies

```bash
curl http://localhost:5000/api/system/chunking-comparison/{document_id}
```

---

## Cache Management

### Get Cache Stats

```bash
curl http://localhost:5000/api/cache/stats
```

Expected response:
```json
{
  "hit_rate": "0.73",
  "entry_count": 1250,
  "cache_size": 52428800,
  "eviction_count": 45,
  "avg_hit_time_ms": 2.1,
  "avg_miss_time_ms": 245
}
```

### Clear Cache

```bash
curl -X POST http://localhost:5000/api/cache/clear
```

Response:
```json
{
  "status": "cleared",
  "entries_removed": 1250
}
```

---

## Metadata

### Get Available Filters

```bash
curl http://localhost:5000/api/metadata/filters
```

Expected response:
```json
{
  "departments": ["engineering", "support", "operations", "hr"],
  "categories": ["Troubleshooting", "FAQ", "Release Notes"],
  "versions": ["1.0", "1.1", "2.0", "2.1"],
  "document_types": ["pdf", "txt", "docx"]
}
```

---

## Testing Workflow

### 1. Basic Flow

1. Health check
2. Upload a document
3. List documents
4. Get document details
5. Query (returns no results initially - chunks needed)
6. Check cache stats
7. Get metadata filters

### 2. Full Integration Flow

1. Upload document (get ID)
2. Manually insert chunks into PostgreSQL
3. Query the system
4. Submit feedback
5. View analytics
6. Compare strategies
7. Monitor cache performance

### 3. Load Testing

```bash
# Test multiple rapid queries
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/rag/query \
    -H "Content-Type: application/json" \
    -d '{"query":"test question","filters":{}}'
done

# Check cache hit rate improved
curl http://localhost:5000/api/cache/stats
```

---

## Postman Collection

Import this into Postman as a quick test suite:

```json
{
  "info": {
    "name": "RAG API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "List Documents",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/documents"
      }
    },
    {
      "name": "Simple Query",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/rag/query",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"query\":\"test\",\"filters\":{}}"
        }
      }
    },
    {
      "name": "System Stats",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/system/stats"
      }
    },
    {
      "name": "Cache Stats",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/cache/stats"
      }
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost:5000"}
  ]
}
```

---

## Error Testing

### 400 Bad Request

Missing required fields:
```bash
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected: `{"error":"Query cannot be empty"}`

### 404 Not Found

Invalid document:
```bash
curl http://localhost:5000/api/documents/invalid-id
```

### 413 Payload Too Large

Upload file > MAX_FILE_SIZE:
```bash
# Will be rejected by multer
```

---

## Performance Monitoring

### Measure Query Speed

```bash
time curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"test","filters":{}}'
```

### Monitor Cache Effectiveness

```bash
# First query (cache miss)
curl http://localhost:5000/api/cache/stats

# Run same query multiple times
for i in {1..5}; do
  curl -X POST http://localhost:5000/api/rag/query \
    -H "Content-Type: application/json" \
    -d '{"query":"test","filters":{}}'
done

# Check cache stats again (should show hits)
curl http://localhost:5000/api/cache/stats
```

---

## Common Issues

### Connection Refused
- Backend not running? `npm run dev`
- Wrong port? Check `.env` PORT setting

### Database Errors
- Database not created? `CREATE DATABASE rag_assistant;`
- Wrong credentials? Update `.env`

### CORS Errors
- Frontend not on localhost:3000? Update CORS_ORIGIN

### File Upload Fails
- File type not allowed? Check ALLOWED_FILE_TYPES
- File too large? Check MAX_FILE_SIZE

---

## Tips

1. Save document IDs from uploads for use in subsequent tests
2. Use Postman for complex requests with multiple fields
3. Check response_id from queries to test feedback endpoints
4. Monitor `/cache/stats` to validate caching is working
5. Use `/system/stats` to validate data consistency

---

**All endpoints tested and ready!** ✅
