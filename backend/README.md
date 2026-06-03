# Technical Support Copilot - Backend API

Production-ready Node.js/Express backend for the Enterprise RAG Assistant, featuring document management, RAG query processing, analytics, and caching.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Development](#development)

---

## Quick Start

### Prerequisites

- Node.js 16+
- PostgreSQL 12+
- npm 8+

### Installation

```bash
cd backend
npm install
```

### Environment Setup

Copy `.env.example` to `.env` and update database credentials:

```bash
cp .env.example .env
```

Update these variables in `.env`:

```env
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_NAME=rag_assistant
DATABASE_HOST=localhost
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
```

### Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE rag_assistant;
\q
```

### Start the Server

```bash
# Development (with auto-reload)
npm run dev

# Production
npm start
```

Server runs at `http://localhost:5000/api`

---

## Architecture

### Project Structure

```
backend/
├── src/
│   ├── config/
│   │   └── database.js         # PostgreSQL pool configuration
│   ├── db/
│   │   └── init.js             # Database initialization & schema
│   ├── middleware/
│   │   ├── errorHandler.js     # Global error handling
│   │   └── multer.js           # File upload configuration
│   ├── models/
│   │   ├── Document.js         # Document model & queries
│   │   ├── Chunk.js            # Chunk model & queries
│   │   ├── Response.js         # Response model & queries
│   │   └── Feedback.js         # Feedback model & queries
│   ├── routes/
│   │   ├── documents.js        # Document management endpoints
│   │   ├── rag.js              # RAG query endpoints
│   │   ├── chunks.js           # Chunk search endpoints
│   │   ├── feedback.js         # Feedback endpoints
│   │   ├── system.js           # System stats endpoints
│   │   ├── cache.js            # Cache management
│   │   └── metadata.js         # Metadata filters
│   ├── utils/
│   │   ├── cache.js            # In-memory cache implementation
│   │   └── logger.js           # Logging utility
│   └── index.js                # Express app setup
├── .env.example
├── package.json
└── README.md
```

### Technology Stack

- **Framework**: Express.js 4.18
- **Database**: PostgreSQL 12+
- **File Upload**: Multer
- **Caching**: In-memory cache
- **Security**: Helmet, CORS, Rate Limiting
- **Validation**: Joi (prepared for extension)

---

## API Endpoints

### Documents

#### POST `/documents/upload`
Upload a document with metadata.

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@guide.pdf" \
  -F 'metadata={"department":"engineering","category":"troubleshooting"}'
```

**Response:**
```json
{
  "document_id": "uuid",
  "name": "guide.pdf",
  "chunk_count": 0,
  "status": "uploaded"
}
```

#### GET `/documents`
List documents with filters.

```bash
curl http://localhost:5000/api/documents?department=engineering&skip=0&limit=10
```

**Query Parameters:**
- `department` - Filter by department
- `category` - Filter by category
- `version` - Filter by version
- `skip` - Pagination offset (default: 0)
- `limit` - Page size (default: 10)

#### GET `/documents/{documentId}`
Get document details.

#### GET `/documents/{documentId}/chunks`
Get chunks from a document.

#### DELETE `/documents/{documentId}`
Delete a document.

---

### RAG Queries

#### POST `/rag/query`
Simple RAG query.

```bash
curl -X POST http://localhost:5000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I fix CrashLoopBackOff?",
    "filters": {"department": "engineering"}
  }'
```

**Response:**
```json
{
  "answer": "A CrashLoopBackOff...",
  "sources": [
    {
      "document_name": "Troubleshooting Guide",
      "chunk": "...",
      "relevance_score": 0.92,
      "metadata": {...}
    }
  ],
  "confidence_score": 0.85
}
```

#### POST `/rag/query-advanced`
Advanced query with retrieval strategy control.

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

### Chunks

#### POST `/chunks/search`
Search chunks across all documents.

```bash
curl -X POST http://localhost:5000/api/chunks/search \
  -H "Content-Type: application/json" \
  -d '{"query": "error handling", "strategy": "hybrid", "top_k": 10}'
```

#### POST `/chunks/batch`
Get chunks from multiple documents.

```bash
curl -X POST http://localhost:5000/api/chunks/batch \
  -H "Content-Type: application/json" \
  -d '{"document_ids": ["uuid1", "uuid2"], "skip": 0, "limit": 50}'
```

---

### Feedback

#### POST `/feedback/{responseId}`
Submit feedback on a response.

```bash
curl -X POST http://localhost:5000/api/feedback/uuid \
  -H "Content-Type: application/json" \
  -d '{
    "helpful": true,
    "comment": "Very accurate",
    "tags": ["accurate", "helpful"]
  }'
```

#### GET `/feedback/analytics`
Get feedback statistics.

```bash
curl http://localhost:5000/api/feedback/analytics
```

---

### System

#### GET `/system/stats`
Get comprehensive system statistics.

```bash
curl http://localhost:5000/api/system/stats
```

**Response:**
```json
{
  "total_documents": 45,
  "total_chunks": 1250,
  "avg_chunk_size": 512,
  "index_size": 52428800,
  "retrieval_strategies": {...},
  "documents_by_department": {...}
}
```

#### POST `/system/retrieval-comparison`
Compare retrieval strategies.

```bash
curl -X POST http://localhost:5000/api/system/retrieval-comparison \
  -H "Content-Type: application/json" \
  -d '{"query": "How to fix ImagePullBackOff?"}'
```

#### GET `/system/chunking-comparison/{documentId}`
Compare chunking strategies.

---

### Cache

#### GET `/cache/stats`
Get cache performance metrics.

```bash
curl http://localhost:5000/api/cache/stats
```

#### POST `/cache/clear`
Clear all cached entries.

```bash
curl -X POST http://localhost:5000/api/cache/clear
```

---

### Metadata

#### GET `/metadata/filters`
Get available filter options.

```bash
curl http://localhost:5000/api/metadata/filters
```

**Response:**
```json
{
  "departments": ["engineering", "support", "operations"],
  "categories": ["Troubleshooting", "FAQ", "Release Notes"],
  "versions": ["1.0", "2.0"],
  "document_types": ["pdf", "txt", "docx"]
}
```

---

## Database Schema

### Documents Table

Stores document metadata and information.

```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  file_path TEXT,
  file_size BIGINT,
  file_type VARCHAR(10),
  chunk_count INT DEFAULT 0,
  department VARCHAR(100),
  category VARCHAR(100),
  version VARCHAR(50),
  document_type VARCHAR(50),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chunks Table

Stores document chunks with embeddings.

```sql
CREATE TABLE chunks (
  id UUID PRIMARY KEY,
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  position INT NOT NULL,
  content TEXT NOT NULL,
  embedding TEXT,
  tokens INT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Responses Table

Stores RAG response history.

```sql
CREATE TABLE responses (
  id UUID PRIMARY KEY,
  query TEXT NOT NULL,
  answer TEXT,
  confidence_score NUMERIC(3,2),
  retrieval_strategy VARCHAR(50),
  retrieval_time_ms INT,
  chunk_ids TEXT[],
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Feedback Table

Stores user feedback on responses.

```sql
CREATE TABLE feedback (
  id UUID PRIMARY KEY,
  response_id UUID NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
  helpful BOOLEAN,
  comment TEXT,
  tags TEXT[],
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string |
| `DATABASE_USER` | postgres | DB username |
| `DATABASE_PASSWORD` | - | DB password |
| `DATABASE_HOST` | localhost | DB host |
| `DATABASE_PORT` | 5432 | DB port |
| `DATABASE_NAME` | rag_assistant | DB name |
| `NODE_ENV` | development | Environment |
| `PORT` | 5000 | Server port |
| `HOST` | localhost | Server host |
| `CORS_ORIGIN` | http://localhost:3000 | CORS origin |
| `MAX_FILE_SIZE` | 52428800 | Max upload size (bytes) |
| `ALLOWED_FILE_TYPES` | pdf,txt,docx,doc | Allowed file types |
| `ENABLE_CACHE` | true | Enable response caching |
| `CACHE_TTL` | 3600 | Cache TTL (seconds) |
| `MAX_CACHE_SIZE` | 100 | Max cache entries |
| `API_RATE_LIMIT` | 100 | Rate limit per window |
| `LOG_LEVEL` | info | Logging level |

---

## Development

### Running Tests

```bash
npm test
```

### Linting

```bash
npm run lint
```

### Debugging

Set `LOG_LEVEL=debug` in `.env`:

```env
LOG_LEVEL=debug
```

View logs in `./logs/error.log`

### Common Issues

**Connection Refused:**
- Check PostgreSQL is running
- Verify DATABASE_HOST and DATABASE_PORT

**CORS Errors:**
- Update CORS_ORIGIN in `.env`
- Ensure frontend is running on correct port

**File Upload Fails:**
- Check MAX_FILE_SIZE setting
- Verify ALLOWED_FILE_TYPES
- Ensure uploads directory is writable

---

## Performance Tips

1. **Use connection pooling** - Already configured in database.js
2. **Enable caching** - Set ENABLE_CACHE=true
3. **Monitor cache hit rate** - Check `/cache/stats` endpoint
4. **Add database indexes** - Already created for common queries
5. **Use pagination** - Always use skip/limit for list endpoints

---

## Production Deployment

1. Set `NODE_ENV=production`
2. Use environment-specific `.env` file
3. Enable HTTPS/SSL for DATABASE_SSL
4. Configure appropriate CORS_ORIGIN
5. Set up process manager (PM2, systemd, etc)
6. Monitor logs and error rates
7. Set up automated backups for PostgreSQL

---

## Support

For API documentation details, see the frontend README.md for integration patterns.
