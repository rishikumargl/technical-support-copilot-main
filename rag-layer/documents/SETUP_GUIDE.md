# Technical Support Copilot - Setup Guide

Complete setup guide for the full-stack RAG application.

## Prerequisites

- **Node.js** 16+ ([Download](https://nodejs.org))
- **PostgreSQL** 12+ ([Download](https://www.postgresql.org/download/))
- **npm** 8+ (comes with Node.js)
- **Git** for version control

## Step 1: PostgreSQL Setup

### Windows

1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Remember the password you set for `postgres` user
4. Accept default port 5432

### macOS

```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu)

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Enter password when prompted
# Then run:
CREATE DATABASE rag_assistant;
\q
```

---

## Step 2: Backend Setup

### Install Dependencies

```bash
cd backend
npm install
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=rag_assistant
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
ENABLE_CACHE=true
CACHE_TTL=3600
```

### Start Backend Server

```bash
# Development mode (auto-reload)
npm run dev

# Or production mode
npm start
```

You should see:
```
Server running at http://localhost:5000
API base URL: http://localhost:5000/api
```

### Verify Backend

```bash
# In another terminal, test the health endpoint
curl http://localhost:5000/health
```

Expected response:
```json
{"status":"ok","timestamp":"2024-06-03T..."}
```

---

## Step 3: Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Configure Environment

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_RERANKING=true
REACT_APP_ENABLE_CACHING=true
```

### Start Frontend Server

```bash
npm start
```

App opens at `http://localhost:3000`

---

## Step 4: Test the Application

### 1. Upload a Document

1. Go to http://localhost:3000
2. Click "Documents" in sidebar
3. Upload a sample PDF with metadata:
   - Department: `engineering`
   - Category: `troubleshooting`
   - Version: `1.0`

### 2. Add Chunks (Temporary)

For now, you need to manually add chunks to test queries. This will be done by the RAG team later.

In a PostgreSQL client:

```sql
-- After uploading a document, get its ID from the documents table
SELECT id FROM documents LIMIT 1;

-- Then insert sample chunks
INSERT INTO chunks (document_id, position, content, metadata)
VALUES (
  'your-document-id-here',
  1,
  'A CrashLoopBackOff indicates your container is crashing repeatedly. Check logs with: kubectl logs <pod> --previous',
  '{"type":"troubleshooting"}'::jsonb
);
```

### 3. Test Query

1. Go to Chat page
2. Ask: "How do I troubleshoot CrashLoopBackOff?"
3. You should see the source attributed

---

## Directory Structure

```
technical-support-copilot-main/
├── backend/                    # Node.js/Express API
│   ├── src/
│   │   ├── routes/            # API endpoints
│   │   ├── models/            # Database models
│   │   ├── db/                # Database initialization
│   │   └── index.js           # Main server file
│   ├── .env.example
│   ├── package.json
│   └── README.md
│
├── frontend/                   # React.js UI
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── api/               # API client
│   │   └── App.js             # Main app component
│   ├── .env
│   ├── package.json
│   └── README.md
│
└── SETUP_GUIDE.md             # This file
```

---

## Common Commands

### Backend

```bash
# Install dependencies
npm install

# Start development server (auto-reload)
npm run dev

# Start production server
npm start

# View logs
tail -f logs/error.log
```

### Frontend

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Database

```bash
# Connect to database
psql -U postgres -d rag_assistant

# View documents
SELECT id, name, chunk_count FROM documents;

# View chunks
SELECT id, content FROM chunks LIMIT 5;

# View responses
SELECT query, confidence_score FROM responses LIMIT 10;

# Quit
\q
```

---

## Troubleshooting

### PostgreSQL Connection Errors

**Error:** `connect ECONNREFUSED 127.0.0.1:5432`

**Solutions:**
1. Check PostgreSQL is running:
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Linux
   sudo systemctl status postgresql
   
   # Windows
   # Check Services app for PostgreSQL
   ```

2. Restart PostgreSQL:
   ```bash
   # macOS
   brew services restart postgresql@15
   
   # Linux
   sudo systemctl restart postgresql
   ```

### Database Doesn't Exist

**Error:** `database "rag_assistant" does not exist`

**Solution:**
```bash
psql -U postgres
CREATE DATABASE rag_assistant;
\q
```

### Port Already in Use

**Error:** `Error: listen EADDRINUSE :::5000`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill process (replace PID)
kill -9 <PID>
```

### CORS Errors in Frontend

**Error:** `Access to XMLHttpRequest has been blocked by CORS policy`

**Solutions:**
1. Check backend is running on port 5000
2. Verify CORS_ORIGIN in backend `.env` matches frontend origin
3. Clear browser cache (Ctrl+Shift+Delete)

### npm install Fails

**Solution:**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Git Workflow for Team

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: description of changes"

# Push to remote
git push origin feature/your-feature

# Create Pull Request on GitHub
# Wait for review and merge
```

### Running Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Backend: `http://localhost:5000`
Frontend: `http://localhost:3000`

---

## Next Steps

1. **Backend is Ready** ✅ - All API endpoints implemented
2. **RAG Integration** - RAG team will:
   - Create chunk ingestion service
   - Implement embedding generation
   - Add vector search capabilities
   - Integrate semantic chunking

3. **Testing** - Add sample documents and test queries

4. **Deployment** - Deploy to production when ready

---

## Environment Checklist

Before starting development, ensure:

- [ ] PostgreSQL is running
- [ ] Database `rag_assistant` exists
- [ ] Backend `.env` is configured
- [ ] Frontend `.env` is configured
- [ ] Port 5000 is available
- [ ] Port 3000 is available
- [ ] Node.js and npm are in PATH

---

## Support

- Backend docs: `backend/README.md`
- Frontend docs: `frontend/README.md`
- API testing: Use curl commands in README files
- Database: Use psql client for direct access

---

**You're all set! 🚀 Start with the troubleshooting guide if you hit any issues.**
