# Technical Support Copilot - Enterprise RAG Assistant

Production-ready full-stack application for the Capstone Challenge: Build a Production-Ready Enterprise RAG Assistant.

## 🎯 Project Overview

This is a **Technical Support Copilot** - a professional-grade AI assistant that answers technical questions from enterprise documentation.

## 📦 Architecture

```
Frontend (React) ↔ REST API (Express.js) ↔ PostgreSQL
http://localhost:3000   http://localhost:5000/api
```

## 🚀 Quick Start

```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE rag_assistant;"

# 2. Backend
cd backend && npm install && cp .env.example .env
npm run dev

# 3. Frontend (new terminal)
cd frontend && npm install && npm start
```

**Backend**: http://localhost:5000 | **Frontend**: http://localhost:3000

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup
- **[BACKEND_COMPLETED.md](BACKEND_COMPLETED.md)** - Backend summary
- **[backend/README.md](backend/README.md)** - API docs
- **[backend/API_TESTING.md](backend/API_TESTING.md)** - Testing
- **[frontend/README.md](frontend/README.md)** - UI docs

## ✅ What's Complete

### Backend
- 17 REST API endpoints
- PostgreSQL database (5 tables)
- Document upload & management
- Query caching
- User feedback system
- Analytics framework
- Security & rate limiting

### Frontend
- Chat interface
- Document manager
- Analytics dashboard
- Configuration panel
- Source attribution

### RAG Module (Other Team)
- Embedding generation
- Vector search
- Semantic chunking
- Integration

## 🔌 API Endpoints

**Documents** (5), **Queries** (2), **Chunks** (2), **Feedback** (2), **System** (3), **Cache** (2), **Metadata** (1)

See [backend/README.md](backend/README.md) for details.

## 🛠️ Tech Stack

- **Backend**: Node.js, Express.js, PostgreSQL
- **Frontend**: React, Router, Axios, Recharts
- **Security**: Helmet.js, CORS, Rate Limiting
- **Caching**: In-memory LRU cache

## 📂 Structure

```
├── backend/        (API & database)
├── frontend/       (React UI)
├── SETUP_GUIDE.md
└── BACKEND_COMPLETED.md
```

## 🚦 Development

```bash
# Terminal 1
cd backend && npm run dev

# Terminal 2
cd frontend && npm start
```

## ⚙️ Configuration

### Backend (.env)
```env
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENABLE_ANALYTICS=true
```

## ✅ Status

🟢 **Production Ready**

Backend: Complete ✅ | Frontend: Complete ✅ | Database: Ready ✅ | RAG: Pending 🔄

---

**Start**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
