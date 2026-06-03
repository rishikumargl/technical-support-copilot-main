"""
FastAPI HTTP Server for RAG Inference Service
Wraps the inference service to make it accessible via HTTP from Node.js backend
"""
import os
import logging
from typing import Optional, Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from inference_service import InferenceService
from hybrid_search import HybridSearchEngine
from qdrant_setup import QdrantDB
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="RAG Inference Service",
    description="HuggingFace Inference API for RAG",
    version="1.0.0"
)

# Initialize services (singleton pattern)
inference_service = None
search_engine = None


def initialize_services():
    """Initialize RAG services on startup"""
    global inference_service, search_engine

    try:
        logger.info("Initializing RAG services...")

        # Initialize inference service
        inference_service = InferenceService()
        logger.info("✓ InferenceService initialized")

        # Initialize search engine
        db = QdrantDB("./qdrant_storage")
        search_engine = HybridSearchEngine(db.client)

        # Try to load chunks if available
        try:
            search_engine.load_chunks_from_file("./output/ingestion_output_fixed.json")
            search_engine.seed_qdrant()
            search_engine.build_bm25_index()
            logger.info("✓ HybridSearchEngine initialized with chunks")
        except Exception as e:
            logger.warning(f"Could not load chunks: {str(e)}")
            logger.info("✓ HybridSearchEngine initialized (no chunks)")

    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    filters: Optional[Dict] = {}


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict] = []
    confidence: float = 0.0
    model: str = "meta-llama/Llama-3.1-8B-Instruct:novita"
    status: str = "OK"
    message: str = "Answer generated with HuggingFace inference"


# Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    initialize_services()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAG Inference API",
        "inference_ready": inference_service is not None,
        "search_ready": search_engine is not None,
    }


@app.post("/api/chat/query", response_model=QueryResponse)
async def chat_query(request: QueryRequest):
    """
    Process a chat query and return AI-generated answer with sources

    Args:
        query: The user's question
        filters: Optional filters (department, category, etc.)

    Returns:
        QueryResponse with answer, sources, and confidence
    """
    if not request.query or request.query.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        if search_engine is None:
            raise Exception("Search engine not initialized")

        logger.info(f"Processing query: {request.query[:50]}...")

        # Search for relevant chunks
        try:
            search_results = search_engine.retrieve_relevant_chunks(
                query=request.query,
                filters=request.filters or None,
                search_type="hybrid",
                top_k=5
            )
        except Exception as search_error:
            logger.warning(f"Search failed: {str(search_error)}")
            search_results = []

        # Generate answer with inference
        if inference_service and search_results:
            result = inference_service.answer_with_sources(
                query=request.query,
                search_results=search_results
            )

            return QueryResponse(
                answer=result['answer'],
                sources=result['sources'],
                confidence=result['confidence'],
                model=result['model'],
                status="OK",
                message="Answer generated with HuggingFace inference"
            )
        elif search_results:
            # Fallback: just return search results without AI generation
            return QueryResponse(
                answer=f"Found {len(search_results)} relevant documents. AI inference not available.",
                sources=search_results,
                confidence=0.5,
                status="FALLBACK",
                message="Returning search results without inference"
            )
        else:
            return QueryResponse(
                answer="No relevant information found in the knowledge base.",
                sources=[],
                confidence=0.0,
                status="NO_RESULTS",
                message="No relevant chunks found"
            )

    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/api/search")
async def search(request: QueryRequest):
    """
    Search for relevant chunks without generating an answer

    Args:
        query: The search query
        filters: Optional filters

    Returns:
        List of relevant chunks with metadata
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        if search_engine is None:
            raise Exception("Search engine not initialized")

        results = search_engine.retrieve_relevant_chunks(
            query=request.query,
            filters=request.filters or None,
            search_type="hybrid",
            top_k=10
        )

        return {
            "results": results,
            "count": len(results),
            "query": request.query
        }

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/api/status")
async def status():
    """Get service status"""
    return {
        "inference_ready": inference_service is not None,
        "search_ready": search_engine is not None,
        "model": "meta-llama/Llama-3.1-8B-Instruct:novita",
        "hf_token_configured": bool(os.environ.get("HF_TOKEN")),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("RAG_API_PORT", 8000))
    host = os.environ.get("RAG_API_HOST", "0.0.0.0")

    logger.info(f"Starting RAG API server on {host}:{port}")
    logger.info(f"Docs available at http://{host}:{port}/docs")

    uvicorn.run(app, host=host, port=port)
