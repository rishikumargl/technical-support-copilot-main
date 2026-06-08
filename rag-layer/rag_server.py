#!/usr/bin/env python3
"""
RAG Server - HTTP API bridge for the RAG layer
Allows backend and frontend to communicate with RAG system via REST API
"""

import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global RAG pipeline instance
rag_pipeline = None

# Global state for document processing
document_processing_lock = threading.Lock()
is_processing_documents = False
last_processed_time = None
processing_complete_event = threading.Event()
processing_complete_event.set()  # Initially set (not processing)

# Import text processor for grammar and formatting
try:
    from text_processor import TextProcessor
    text_processor = TextProcessor()
    logger.info("Text processor initialized for grammar correction")
except (ImportError, Exception) as e:
    text_processor = None
    logger.warning(f"Text processor not available: {e} - responses may have formatting issues")


def process_new_documents_background():
    """Background task to process and index new documents without server restart."""
    global rag_pipeline, is_processing_documents, last_processed_time, processing_complete_event

    with document_processing_lock:
        if is_processing_documents:
            logger.info("Document processing already in progress...")
            return

        is_processing_documents = True
        processing_complete_event.clear()  # Mark as processing

    try:
        if rag_pipeline is None:
            logger.warning("RAG pipeline not initialized yet. Skipping document processing.")
            return

        source_dir = 'ingestion_pipeline/data'
        logger.info(f"Starting background document processing from {source_dir}")

        # Re-run the full pipeline to index documents
        try:
            result = rag_pipeline.run_full_pipeline()
            logger.info(f"Document processing completed successfully: {result}")
            last_processed_time = result
        except Exception as pipeline_error:
            logger.error(f"Error during pipeline re-run: {pipeline_error}", exc_info=True)

    except Exception as e:
        logger.error(f"Background document processing failed: {e}", exc_info=True)
    finally:
        is_processing_documents = False
        processing_complete_event.set()  # Mark as complete
        logger.info("Document processing task completed")


def trigger_document_processing():
    """Trigger background document processing in a separate thread."""
    try:
        # Start processing in background thread so we don't block the request
        processing_thread = threading.Thread(
            target=process_new_documents_background,
            daemon=True,
            name="DocumentProcessor"
        )
        processing_thread.start()
        logger.info("Document processing triggered in background")
        return True
    except Exception as e:
        logger.error(f"Failed to trigger document processing: {e}")
        return False


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'rag-server',
        'rag_initialized': rag_pipeline is not None,
    })


@app.route('/api/rag/query', methods=['POST'])
def query():
    """Query the RAG system with support for various search and filtering options"""
    try:
        data = request.json
        question = data.get('question')

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        if rag_pipeline is None:
            return jsonify({
                'error': 'RAG pipeline not initialized',
                'message': 'Please initialize the RAG system first'
            }), 503

        # Extract options with Phase 1, 2, and 3 improvements
        options = {
            'top_k': data.get('top_k', 5),
            'search_type': data.get('search_type', 'hybrid'),
            'department': data.get('department'),
            'category': data.get('category'),
            'min_score': data.get('min_score', 0.0),  # Phase 1: confidence filtering
            'use_reranking': data.get('use_reranking', True),  # Phase 2: semantic reranking
        }

        logger.info(f"Query: {question} | Options: {options}")

        # Query RAG
        results = rag_pipeline.query(question, **options)

        # Get score key (rerank or combined)
        score_key = 'rerank_score' if results and 'rerank_score' in results[0] else 'combined_score'

        # Process results through text processor for clean grammar and formatting
        processed_results = results
        answer_text = results[0]['text'] if results else 'No answer found'

        if text_processor:
            try:
                # Clean the answer text
                answer_text = text_processor.format_answer(answer_text)

                # Clean each source chunk
                processed_results = text_processor.process_response(results)
            except Exception as processor_error:
                logger.warning(f"Text processor error: {processor_error}. Using raw results.")
                # Fall back to raw results if processor fails
                processed_results = results

        # Format response
        sources = []
        try:
            for r in processed_results:
                chunk_text = r.get('text', '')[:200]
                try:
                    if text_processor:
                        chunk_text = text_processor.process_chunk(chunk_text)
                except Exception as e:
                    logger.warning(f"Chunk processing error: {e}")
                    # Use raw chunk text on error

                sources.append({
                    'document_name': r.get('document_name'),
                    'chunk': chunk_text,
                    'relevance_score': r.get(score_key, 0),
                    'confidence': r.get(score_key, 0),
                    'dense_score': r.get('dense_score'),
                    'sparse_score': r.get('sparse_score'),
                    'rerank_score': r.get('rerank_score'),
                    'metadata': {
                        'department': r.get('department'),
                        'category': r.get('category'),
                        'version': r.get('version'),
                    }
                })
        except Exception as e:
            logger.error(f"Error building sources: {e}")

        response = {
            'success': True,
            'question': question,
            'answer': answer_text,
            'sources': sources,
            'confidence_score': results[0].get(score_key, 0) if results else 0,
            'status': 'RAG_IMPLEMENTED',
            'message': 'Successfully retrieved from RAG system',
            'retrieval_method': f"{options['search_type']}_with_reranking" if options['use_reranking'] else options['search_type'],
            'grammar_corrected': text_processor is not None,
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR',
            'success': False,
        }), 500


@app.route('/api/rag/query-advanced', methods=['POST'])
def query_advanced():
    """Advanced query with comprehensive retrieval options"""
    try:
        data = request.json
        question = data.get('query')

        if not question:
            return jsonify({'error': 'Query is required'}), 400

        if rag_pipeline is None:
            return jsonify({
                'error': 'RAG pipeline not initialized',
                'message': 'Please initialize the RAG system first'
            }), 503

        # Extract all options including Phase 1, 2, 3 improvements
        filters_dict = data.get('filters', {})
        options = {
            'top_k': data.get('top_k', 5),
            'search_type': data.get('retrieval_strategy', 'hybrid'),
            'department': filters_dict.get('department'),
            'category': filters_dict.get('category'),
            'min_score': data.get('min_score', 0.0),
            'use_reranking': data.get('use_reranking', True),
        }

        logger.info(f"Advanced Query: {question} | Options: {options}")

        # Query RAG
        results = rag_pipeline.query(question, **options)

        # Get score key (rerank or combined)
        score_key = 'rerank_score' if results and 'rerank_score' in results[0] else 'combined_score'

        # Process results through text processor
        processed_results = results
        answer_text = results[0]['text'] if results else 'No answer found'

        if text_processor:
            try:
                answer_text = text_processor.format_answer(answer_text)
                processed_results = text_processor.process_response(results)
            except Exception as processor_error:
                logger.warning(f"Text processor error in advanced query: {processor_error}. Using raw results.")
                processed_results = results

        # Format response
        sources = []
        try:
            for r in processed_results:
                chunk_text = r.get('text', '')[:300]
                try:
                    if text_processor:
                        chunk_text = text_processor.process_chunk(chunk_text)
                except Exception as e:
                    logger.warning(f"Chunk processing error: {e}")

                sources.append({
                    'document_name': r.get('document_name'),
                    'chunk': chunk_text,
                    'relevance_score': r.get(score_key, 0),
                    'dense_score': r.get('dense_score'),
                    'sparse_score': r.get('sparse_score'),
                    'rerank_score': r.get('rerank_score'),
                    'metadata': {
                        'department': r.get('department'),
                        'category': r.get('category'),
                        'version': r.get('version'),
                    }
                })
        except Exception as e:
            logger.error(f"Error building sources: {e}")

        response = {
            'success': True,
            'query': question,
            'answer': answer_text,
            'sources': sources,
            'confidence_score': results[0].get(score_key, 0) if results else 0,
            'result_count': len(results),
            'status': 'RAG_IMPLEMENTED',
            'message': 'Successfully retrieved from RAG system with advanced options',
            'retrieval_method': f"{options['search_type']}_with_reranking" if options['use_reranking'] else options['search_type'],
            'grammar_corrected': text_processor is not None,
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Advanced query error: {e}")
        return jsonify({
            'error': str(e),
            'status': 'ERROR',
            'success': False,
        }), 500


@app.route('/api/rag/initialize', methods=['POST'])
def initialize():
    """Initialize the RAG system with optional Phase 2/3 features"""
    try:
        global rag_pipeline

        data = request.json or {}
        source_dir = data.get('source_dir', 'ingestion_pipeline/data')
        chunking_strategy = data.get('chunking_strategy', 'sentence_boundary')
        use_ensemble = data.get('use_ensemble', False)  # Phase 3
        enable_query_expansion = data.get('enable_query_expansion', False)  # Phase 3

        logger.info(f"Initializing RAG system from {source_dir}")
        logger.info(f"  Chunking strategy: {chunking_strategy}")
        logger.info(f"  Ensemble embeddings: {use_ensemble}")
        logger.info(f"  Query expansion: {enable_query_expansion}")

        # Import and initialize
        from integration_pipeline import RAGIntegrationPipeline

        rag_pipeline = RAGIntegrationPipeline(
            source_dir=source_dir,
            chunking_strategy=chunking_strategy,
        )

        # Phase 3: Setup ensemble if requested
        if use_ensemble:
            rag_pipeline.search_engine.setup_ensemble(use_ensemble=True)

        # Phase 3: Setup query expansion if requested
        if enable_query_expansion:
            rag_pipeline.search_engine.setup_query_expansion()

        # Run full pipeline
        result = rag_pipeline.run_full_pipeline()

        logger.info(f"RAG initialization complete: {result}")

        return jsonify({
            'success': True,
            'message': 'RAG system initialized successfully',
            'result': result,
            'features': {
                'chunking_strategy': chunking_strategy,
                'ensemble_embeddings': use_ensemble,
                'query_expansion': enable_query_expansion,
            }
        })

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
        }), 500


@app.route('/api/rag/status', methods=['GET'])
def status():
    """Get current RAG system status including document processing state."""
    try:
        return jsonify({
            'success': True,
            'status': {
                'rag_initialized': rag_pipeline is not None,
                'processing_documents': is_processing_documents,
                'last_processed': last_processed_time,
                'service': 'rag-server'
            }
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
        }), 500


@app.route('/api/rag/reindex', methods=['POST'])
def reindex():
    """Manually trigger document reindexing and wait for completion."""
    try:
        if rag_pipeline is None:
            return jsonify({
                'error': 'RAG pipeline not initialized',
                'success': False,
            }), 503

        if is_processing_documents:
            return jsonify({
                'success': False,
                'error': 'Document processing already in progress. Please wait.',
                'status': 'already_processing'
            }), 409

        logger.info("Manual reindex triggered by user")
        processing_started = trigger_document_processing()

        if not processing_started:
            return jsonify({
                'success': False,
                'error': 'Failed to start reindexing',
                'status': 'indexing_failed'
            }), 500

        # Wait for reindexing to complete (with timeout of 5 minutes)
        logger.info("Waiting for documents to be reindexed...")
        processing_complete = processing_complete_event.wait(timeout=300)  # 5 minute timeout

        if processing_complete:
            logger.info("Document reindexing completed successfully")
            return jsonify({
                'success': True,
                'message': 'Documents have been reindexed and are searchable.',
                'status': 'reindex_complete'
            }), 200
        else:
            logger.warning("Document reindexing timed out after 5 minutes")
            return jsonify({
                'success': False,
                'error': 'Document reindexing timed out after 5 minutes',
                'status': 'timeout'
            }), 408

    except Exception as e:
        logger.error(f"Reindex error: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
        }), 500


@app.route('/api/rag/stats', methods=['GET'])
def stats():
    """Get RAG system statistics"""
    try:
        if rag_pipeline is None:
            return jsonify({
                'error': 'RAG pipeline not initialized',
                'success': False,
            }), 503

        stats = rag_pipeline.get_stats()

        return jsonify({
            'success': True,
            'stats': stats,
        })

    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
        }), 500


@app.route('/api/rag/ingest', methods=['POST'])
def ingest():
    """Document ingestion endpoint - processes documents in background and waits for completion.
    Response is sent only after documents are indexed and searchable."""
    try:
        data = request.json or {}
        document_id = data.get('document_id')

        if not document_id:
            return jsonify({
                'error': 'document_id is required',
                'success': False,
            }), 400

        logger.info(f"Document {document_id} uploaded. Starting background indexing...")

        # Trigger background document processing
        processing_started = trigger_document_processing()

        if not processing_started:
            return jsonify({
                'success': False,
                'error': 'Failed to start document indexing',
                'result': {
                    'document_id': document_id,
                    'status': 'indexing_failed'
                },
            }), 500

        # Wait for document processing to complete (with timeout of 5 minutes)
        logger.info(f"Waiting for document {document_id} to be indexed...")
        processing_complete = processing_complete_event.wait(timeout=300)  # 5 minute timeout

        if processing_complete:
            logger.info(f"Document {document_id} indexed successfully and is now searchable")
            return jsonify({
                'success': True,
                'message': 'Document has been processed and is now searchable.',
                'result': {
                    'document_id': document_id,
                    'status': 'indexed_and_searchable',
                    'note': 'Document is ready for queries.'
                },
            }), 201
        else:
            logger.warning(f"Document {document_id} processing timed out after 5 minutes")
            return jsonify({
                'success': False,
                'error': 'Document processing timed out after 5 minutes',
                'result': {
                    'document_id': document_id,
                    'status': 'timeout'
                },
            }), 408

    except Exception as e:
        logger.error(f"Ingest error: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
        }), 500


@app.errorhandler(404)
def not_found(e):
    """404 handler"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """500 handler"""
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


def initialize_on_startup():
    """Initialize RAG system on server startup"""
    global rag_pipeline
    try:
        logger.info("Auto-initializing RAG system on startup...")
        from integration_pipeline import RAGIntegrationPipeline
        from pathlib import Path
        import shutil

        source_dir = os.environ.get('RAG_SOURCE_DIR', 'ingestion_pipeline/data')

        # Create source_dir if it doesn't exist
        Path(source_dir).mkdir(parents=True, exist_ok=True)

        # Merge uploaded documents from backend/uploads/ into ingestion_pipeline/data/
        # Try multiple path variations to find backend/uploads
        possible_paths = [
            Path('../backend/uploads'),  # From rag-layer/
            Path('../../backend/uploads'),  # If running from subdirectory
            Path(__file__).parent.parent / 'backend' / 'uploads',  # Absolute from script location
        ]

        backend_uploads_dir = None
        for path in possible_paths:
            if path.exists() and path.is_dir():
                backend_uploads_dir = path
                logger.info(f"Found backend uploads directory: {backend_uploads_dir.absolute()}")
                break

        if backend_uploads_dir:
            try:
                logger.info(f"Scanning uploads directory: {backend_uploads_dir}")
                for doc_file in backend_uploads_dir.glob('*'):
                    if doc_file.is_file() and doc_file.suffix.lower() in ['.pdf', '.txt', '.docx']:
                        dest = Path(source_dir) / doc_file.name
                        if not dest.exists():
                            logger.info(f"Copying {doc_file.name} to ingestion pipeline")
                            shutil.copy2(doc_file, dest)
                        else:
                            logger.info(f"Document {doc_file.name} already exists in ingestion pipeline")
            except Exception as copy_error:
                logger.warning(f"Error copying documents from backend uploads: {copy_error}")
        else:
            logger.warning(f"Backend uploads directory not found. Tried: {[str(p) for p in possible_paths]}")

        rag_pipeline = RAGIntegrationPipeline(source_dir=source_dir)
        result = rag_pipeline.run_full_pipeline()
        logger.info(f"RAG initialization successful: {result}")
    except Exception as e:
        logger.error(f"RAG auto-initialization failed: {e}", exc_info=True)
        logger.warning(f"System will require manual initialization via /api/rag/initialize endpoint")


if __name__ == '__main__':
    port = int(os.environ.get('RAG_SERVER_PORT', 5001))
    host = os.environ.get('RAG_SERVER_HOST', '0.0.0.0')

    logger.info(f"Starting RAG Server on {host}:{port}")

    # Auto-initialize RAG system
    initialize_on_startup()

    app.run(host=host, port=port, debug=False)
