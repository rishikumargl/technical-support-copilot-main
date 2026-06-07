# Dynamic Document Processing - No Server Restart Required

## Overview

Documents are now automatically processed and indexed in the background without requiring server restart. Upload a document and it becomes searchable within 30-60 seconds.

---

## How It Works

### 1. **Upload Document**
```bash
curl -X POST http://localhost:5001/api/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"document_id": "my-document.pdf"}'
```

**Response** (Immediate):
```json
{
  "success": true,
  "message": "Document received and automatic indexing started.",
  "result": {
    "document_id": "my-document.pdf",
    "status": "indexing_in_progress",
    "note": "Document is being processed in background. It will be searchable within 30-60 seconds."
  }
}
```

### 2. **Check Processing Status**
```bash
curl -X GET http://localhost:5001/api/rag/status
```

**Response**:
```json
{
  "success": true,
  "status": {
    "rag_initialized": true,
    "processing_documents": true,
    "last_processed": {...},
    "service": "rag-server"
  }
}
```

### 3. **Query New Document** (After Processing Complete)
```bash
curl -X POST http://localhost:5001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is in the newly uploaded document?"}'
```

---

## New API Endpoints

### `/api/rag/ingest` (POST) - Upload Document
Triggers automatic background processing.

**Request**:
```json
{
  "document_id": "document-name.pdf"
}
```

**Response** (202 Accepted):
```json
{
  "success": true,
  "message": "Document received and automatic indexing started.",
  "result": {
    "document_id": "document-name.pdf",
    "status": "indexing_in_progress",
    "note": "Document will be searchable within 30-60 seconds."
  }
}
```

---

### `/api/rag/status` (GET) - Check System Status
Get current RAG system status including document processing state.

**Response**:
```json
{
  "success": true,
  "status": {
    "rag_initialized": true,
    "processing_documents": false,  // true if currently indexing
    "last_processed": "2026-06-08T00:15:30",
    "service": "rag-server"
  }
}
```

---

### `/api/rag/reindex` (POST) - Manual Reindexing
Manually trigger reindexing of all documents.

**Response**:
```json
{
  "success": true,
  "message": "Document reindexing started in background",
  "status": "indexing_in_progress"
}
```

---

## Processing Flow

```
User uploads document
        ↓
Server returns immediately (202 Accepted)
        ↓
Background thread starts processing
        ↓
Documents are parsed, chunked, embedded
        ↓
Vectors stored in Qdrant (in-memory)
        ↓
BM25 index rebuilt
        ↓
Document searchable (30-60 seconds later)
        ↓
User can query the new document
```

---

## Key Features

### ✅ No Server Restart Needed
- Upload document and it's automatically indexed
- No downtime required
- Other queries continue working during indexing

### ✅ Background Processing
- Processing happens in separate thread
- Server responds immediately (202 Accepted)
- User knows indexing is in progress

### ✅ Status Tracking
- Check processing status with `/api/rag/status`
- See when last reindex completed
- Know if currently processing

### ✅ Thread-Safe
- Locking mechanism prevents concurrent processing
- Only one indexing job at a time
- Safe under concurrent requests

---

## Workflow Example

### Step 1: Upload Document
```bash
curl -X POST http://localhost:5001/api/rag/ingest \
  -d '{"document_id": "policy-2026.pdf"}' \
  -H "Content-Type: application/json"

# Response: 202 Accepted - indexing started in background
```

### Step 2: Wait for Processing (Check Status)
```bash
# Immediately after upload:
curl -X GET http://localhost:5001/api/rag/status

# Response: "processing_documents": true

# Wait 30-60 seconds...

# Check again:
curl -X GET http://localhost:5001/api/rag/status

# Response: "processing_documents": false - Done!
```

### Step 3: Query New Document
```bash
curl -X POST http://localhost:5001/api/rag/query \
  -d '{"question": "What are the 2026 policies?"}' \
  -H "Content-Type: application/json"

# Returns results from newly uploaded document!
```

---

## Processing Time Estimates

| Task | Time |
|------|------|
| Document upload | <100ms |
| Parsing | 1-5 seconds |
| Chunking | 2-5 seconds |
| Embedding | 5-30 seconds (depends on doc size) |
| Vector storage | 2-5 seconds |
| BM25 indexing | 1-3 seconds |
| **Total** | **30-60 seconds** |

---

## Implementation Details

### Thread-Safe Processing
```python
# Global lock prevents concurrent processing
document_processing_lock = threading.Lock()
is_processing_documents = False

def process_new_documents_background():
    with document_processing_lock:
        if is_processing_documents:
            return  # Already processing
        is_processing_documents = True
    
    try:
        # Re-run full pipeline
        result = rag_pipeline.run_full_pipeline()
    finally:
        is_processing_documents = False
```

### Background Thread
```python
# Non-blocking background task
processing_thread = threading.Thread(
    target=process_new_documents_background,
    daemon=True,
    name="DocumentProcessor"
)
processing_thread.start()
```

---

## Error Handling

### Already Processing
```json
{
  "success": false,
  "error": "Document processing already in progress. Please wait.",
  "status": "already_processing"
}
```

### Pipeline Not Initialized
```json
{
  "success": false,
  "error": "RAG pipeline not initialized",
  "status": 503
}
```

### Processing Failed
```json
{
  "success": false,
  "error": "Failed to start document indexing",
  "status": "indexing_failed"
}
```

---

## Best Practices

1. **Check Status Before Querying**
   - After uploading, check `/api/rag/status`
   - Wait until `processing_documents` is `false`
   - Then query the new document

2. **Batch Uploads**
   - If uploading multiple documents, wait for one to finish before uploading next
   - Or manually call `/api/rag/reindex` after all uploads

3. **Monitor Processing**
   - Use `/api/rag/status` to track progress
   - Log processing times for optimization

4. **Manual Reindex**
   - Use `/api/rag/reindex` if documents on disk changed
   - Useful for testing or maintenance

---

## Code Changes

### Modified Files
- `rag_server.py` - Added background processing logic

### New Endpoints
- `POST /api/rag/ingest` - Updated to use background processing
- `GET /api/rag/status` - NEW: Check processing status
- `POST /api/rag/reindex` - NEW: Manual reindex trigger

### New Functions
- `process_new_documents_background()` - Background indexing task
- `trigger_document_processing()` - Start background thread

---

## Before & After

### Before (Old Way)
```
Upload document → Manual restart required → Indexing happens → Can query
Time: 2-5 minutes (manual restart)
```

### After (New Way)
```
Upload document → Automatic indexing starts → Can query after 30-60 seconds
Time: 30-60 seconds (automatic)
```

---

## Testing

### Test Document Upload & Auto-Processing
```bash
#!/bin/bash

# 1. Upload document
echo "Uploading document..."
curl -X POST http://localhost:5001/api/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test-doc.pdf"}'

# 2. Check initial status
echo "Checking status (should be processing)..."
curl -X GET http://localhost:5001/api/rag/status

# 3. Wait and check again
echo "Waiting 40 seconds..."
sleep 40

echo "Checking status again (should be done)..."
curl -X GET http://localhost:5001/api/rag/status

# 4. Query the document
echo "Querying new document..."
curl -X POST http://localhost:5001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is in the test document?"}'
```

---

## Summary

✅ **Documents process automatically in background**  
✅ **No server restart required**  
✅ **Searchable within 30-60 seconds**  
✅ **Status tracking available**  
✅ **Thread-safe implementation**  
✅ **User-friendly error messages**  

No more manual restarts - just upload and wait! 🚀
