const express = require('express');
const Document = require('../models/Document');
const Chunk = require('../models/Chunk');
const logger = require('../utils/logger');

const router = express.Router();

// Trigger document ingestion (parse and chunk)
router.post('/process/:documentId', async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.documentId);

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    const {
      chunkingStrategy = 'semantic',
      chunkSize = 512,
      overlapSize = 128,
    } = req.body;

    // Simulate document processing
    const startTime = Date.now();

    // In production, this would call the Python ingestion pipeline
    // For now, we'll simulate chunking
    const simulatedChunks = Math.ceil(document.file_size / chunkSize);

    // Create sample chunks
    const chunks = [];
    for (let i = 0; i < Math.min(simulatedChunks, 10); i++) {
      chunks.push({
        documentId: document.id,
        position: i,
        content: `Sample chunk ${i + 1} from document ${document.name}. This represents extracted content from the document.`,
        tokens: Math.floor(Math.random() * 500) + 100,
        metadata: {
          strategy: chunkingStrategy,
          chunkSize: chunkSize,
        },
      });
    }

    // Save chunks to database
    for (const chunk of chunks) {
      await Chunk.create(chunk);
    }

    const processingTime = Date.now() - startTime;

    // Update document chunk count
    await Document.updateChunkCount(document.id, chunks.length);

    logger.info('Document ingestion completed', {
      documentId: document.id,
      chunksCreated: chunks.length,
      strategy: chunkingStrategy,
      time: processingTime,
    });

    res.json({
      status: 'completed',
      document_id: document.id,
      chunks_created: chunks.length,
      chunk_strategy: chunkingStrategy,
      chunk_size: chunkSize,
      overlap_size: overlapSize,
      processing_time_ms: processingTime,
      preview: chunks.slice(0, 3).map(c => ({
        position: c.position,
        content: c.content.substring(0, 100) + '...',
      })),
    });
  } catch (error) {
    next(error);
  }
});

// Get ingestion progress
router.get('/progress/:documentId', async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.documentId);

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    const chunks = await Chunk.findByDocumentId(req.params.documentId);

    res.json({
      document_id: document.id,
      document_name: document.name,
      status: chunks.length > 0 ? 'completed' : 'pending',
      progress: chunks.length > 0 ? 100 : 0,
      chunks_processed: chunks.length,
      file_size: document.file_size,
      metadata: document.metadata,
    });
  } catch (error) {
    next(error);
  }
});

// Batch ingestion - process multiple documents
router.post('/batch', async (req, res, next) => {
  try {
    const { documentIds, chunkingStrategy = 'semantic' } = req.body;

    if (!documentIds || !Array.isArray(documentIds) || documentIds.length === 0) {
      return res.status(400).json({ error: 'documentIds must be a non-empty array' });
    }

    const results = [];
    const startTime = Date.now();

    for (const docId of documentIds) {
      const document = await Document.findById(docId);
      if (!document) continue;

      const simulatedChunks = Math.ceil(document.file_size / 512);
      const chunkCount = Math.min(simulatedChunks, 10);

      // Create chunks
      for (let i = 0; i < chunkCount; i++) {
        await Chunk.create({
          documentId: docId,
          position: i,
          content: `Chunk ${i + 1} from ${document.name}`,
          metadata: { strategy: chunkingStrategy },
        });
      }

      await Document.updateChunkCount(docId, chunkCount);

      results.push({
        document_id: docId,
        name: document.name,
        chunks_created: chunkCount,
        status: 'completed',
      });
    }

    const totalTime = Date.now() - startTime;

    logger.info('Batch ingestion completed', {
      documentsProcessed: results.length,
      totalTime,
    });

    res.json({
      status: 'completed',
      documents_processed: results.length,
      total_time_ms: totalTime,
      results,
    });
  } catch (error) {
    next(error);
  }
});

// Get ingestion strategies comparison
router.get('/strategies/:documentId', async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.documentId);

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    res.json({
      document_id: document.id,
      file_size: document.file_size,
      strategies: {
        fixed_size: {
          name: 'Fixed-Size Chunking',
          description: 'Splits document into fixed-size chunks (512 chars default)',
          chunk_size: 512,
          overlap: 128,
          estimated_chunks: Math.ceil(document.file_size / 512),
          pros: ['Fast', 'Simple', 'Predictable'],
          cons: ['May break sentences', 'Lower quality'],
          quality_score: 0.82,
        },
        semantic: {
          name: 'Semantic Chunking',
          description: 'Respects sentence and paragraph boundaries',
          chunk_size: 512,
          overlap: 128,
          estimated_chunks: Math.ceil(document.file_size / 567),
          pros: ['Better quality', 'Respects boundaries', 'Coherent chunks'],
          cons: ['Slower', 'Variable chunk size'],
          quality_score: 0.91,
        },
      },
      recommendation: 'semantic',
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
