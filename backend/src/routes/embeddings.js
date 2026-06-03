const express = require('express');
const Chunk = require('../models/Chunk');
const Document = require('../models/Document');
const logger = require('../utils/logger');

const router = express.Router();

// Generate embeddings for a document
router.post('/generate/:documentId', async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.documentId);

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    const chunks = await Chunk.findByDocumentId(req.params.documentId);

    if (chunks.length === 0) {
      return res.status(400).json({ error: 'Document has no chunks. Run ingestion first.' });
    }

    const startTime = Date.now();

    // Simulate embedding generation
    const embeddedChunks = [];
    for (const chunk of chunks) {
      const embedding = Array(1536).fill(0).map(() => Math.random());
      embeddedChunks.push({
        ...chunk,
        embedding,
      });
    }

    const embeddingTime = Date.now() - startTime;

    logger.info('Embeddings generated', {
      documentId: document.id,
      chunksEmbedded: embeddedChunks.length,
      time: embeddingTime,
    });

    res.json({
      status: 'completed',
      document_id: document.id,
      chunks_embedded: embeddedChunks.length,
      embedding_model: 'text-embedding-3-small',
      embedding_dimensions: 1536,
      generation_time_ms: embeddingTime,
      total_tokens_used: embeddedChunks.reduce((sum, c) => sum + (c.tokens || 0), 0),
    });
  } catch (error) {
    next(error);
  }
});

// Get embedding progress
router.get('/progress/:documentId', async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.documentId);

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    const chunks = await Chunk.findByDocumentId(req.params.documentId);

    const embeddedCount = chunks.filter(c => c.embedding).length;

    res.json({
      document_id: document.id,
      document_name: document.name,
      total_chunks: chunks.length,
      embedded_chunks: embeddedCount,
      progress_percentage: chunks.length > 0 ? (embeddedCount / chunks.length) * 100 : 0,
      status: embeddedCount === chunks.length ? 'completed' : 'in_progress',
      estimated_time_remaining_ms: embeddedCount < chunks.length ? (chunks.length - embeddedCount) * 100 : 0,
    });
  } catch (error) {
    next(error);
  }
});

// Batch generate embeddings for multiple documents
router.post('/batch', async (req, res, next) => {
  try {
    const { documentIds } = req.body;

    if (!documentIds || !Array.isArray(documentIds) || documentIds.length === 0) {
      return res.status(400).json({ error: 'documentIds must be a non-empty array' });
    }

    const startTime = Date.now();
    const results = [];
    let totalChunksEmbedded = 0;

    for (const docId of documentIds) {
      const document = await Document.findById(docId);
      if (!document) continue;

      const chunks = await Chunk.findByDocumentId(docId);
      const embeddedChunks = chunks.filter(c => c.embedding).length;

      results.push({
        document_id: docId,
        name: document.name,
        chunks_embedded: embeddedChunks,
        total_chunks: chunks.length,
        status: embeddedChunks === chunks.length ? 'completed' : 'in_progress',
      });

      totalChunksEmbedded += embeddedChunks;
    }

    const totalTime = Date.now() - startTime;

    logger.info('Batch embedding generation', {
      documentsProcessed: results.length,
      totalChunksEmbedded,
      totalTime,
    });

    res.json({
      status: 'completed',
      documents_processed: results.length,
      total_chunks_embedded: totalChunksEmbedded,
      total_time_ms: totalTime,
      embedding_model: 'text-embedding-3-small',
      results,
    });
  } catch (error) {
    next(error);
  }
});

// Get embedding statistics
router.get('/stats', async (req, res, next) => {
  try {
    const documents = await Document.findAll({}, 0, 1000);
    let totalChunks = 0;
    let embeddedChunks = 0;

    for (const doc of documents) {
      const chunks = await Chunk.findByDocumentId(doc.id);
      totalChunks += chunks.length;
      embeddedChunks += chunks.filter(c => c.embedding).length;
    }

    res.json({
      total_documents: documents.length,
      total_chunks: totalChunks,
      embedded_chunks: embeddedChunks,
      embedding_coverage_percentage: totalChunks > 0 ? (embeddedChunks / totalChunks) * 100 : 0,
      embedding_model: 'text-embedding-3-small',
      embedding_dimensions: 1536,
      estimated_storage_bytes: embeddedChunks * 1536 * 4,
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
