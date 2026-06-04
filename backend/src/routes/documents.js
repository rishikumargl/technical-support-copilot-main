const express = require('express');
const upload = require('../middleware/multer');
const Document = require('../models/Document');
const Chunk = require('../models/Chunk');
const logger = require('../utils/logger');
const fs = require('fs');
const path = require('path');

const router = express.Router();

router.post('/upload', upload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const metadata = req.body.metadata ? JSON.parse(req.body.metadata) : {};
    const {
      name = req.file.originalname,
      department = '',
      category = '',
      version = '1.0',
      documentType = req.file.mimetype,
    } = metadata;

    const document = await Document.create({
      name,
      filePath: req.file.path,
      fileSize: req.file.size,
      fileType: req.file.originalname.split('.').pop(),
      metadata: {
        mimeType: req.file.mimetype,
        originalName: req.file.originalname,
        ...metadata,
      },
      department,
      category,
      version,
      documentType,
    });

    logger.info('Document uploaded', { documentId: document.id, fileName: name });

    // Note: Documents are indexed when RAG server starts.
    // Newly uploaded documents are searchable via BM25 keyword search immediately.
    // To enable vector search on new documents, restart the RAG server.
    logger.info('Document uploaded - will be indexed on RAG server restart', {
      documentId: document.id,
      fileName: name
    });

    res.status(201).json({
      document_id: document.id,
      name: document.name,
      chunk_count: 0,
      status: 'uploaded',
    });
  } catch (error) {
    if (req.file) {
      fs.unlink(req.file.path, (err) => {
        if (err) logger.error('Failed to delete uploaded file', { error: err.message });
      });
    }
    next(error);
  }
});

router.get('/', async (req, res, next) => {
  try {
    const skip = Math.max(0, parseInt(req.query.skip) || 0);
    const limit = Math.min(100, parseInt(req.query.limit) || 10);

    const filters = {
      department: req.query.department,
      category: req.query.category,
      version: req.query.version,
    };

    const documents = await Document.findAll(filters, skip, limit);
    const total = await Document.count(filters);

    res.json({
      documents: documents.map(doc => ({
        id: doc.id,
        name: doc.name,
        chunk_count: doc.chunk_count,
        size: doc.file_size,
        metadata: doc.metadata,
        uploaded_at: doc.created_at,
      })),
      total,
    });
  } catch (error) {
    next(error);
  }
});

router.get('/:documentId', async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.documentId);

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    res.json({
      id: document.id,
      name: document.name,
      chunk_count: document.chunk_count,
      size: document.file_size,
      metadata: document.metadata,
      uploaded_at: document.created_at,
    });
  } catch (error) {
    next(error);
  }
});

router.get('/:documentId/chunks', async (req, res, next) => {
  try {
    const skip = Math.max(0, parseInt(req.query.skip) || 0);
    const limit = Math.min(100, parseInt(req.query.limit) || 10);

    const chunks = await Chunk.findByDocumentIdPaginated(req.params.documentId, skip, limit);
    const total = await Chunk.countByDocumentId(req.params.documentId);

    res.json({
      chunks: chunks.map(chunk => ({
        chunk_id: chunk.id,
        content: chunk.content,
        position: chunk.position,
        embedding: chunk.embedding ? JSON.parse(chunk.embedding) : null,
        metadata: chunk.metadata,
      })),
      total,
    });
  } catch (error) {
    next(error);
  }
});

router.delete('/:documentId', async (req, res, next) => {
  try {
    const document = await Document.findById(req.params.documentId);

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    if (document.file_path && fs.existsSync(document.file_path)) {
      fs.unlink(document.file_path, (err) => {
        if (err) logger.error('Failed to delete file', { error: err.message });
      });
    }

    await Chunk.deleteByDocumentId(req.params.documentId);
    await Document.delete(req.params.documentId);

    logger.info('Document deleted', { documentId: req.params.documentId });

    res.json({
      status: 'deleted',
      document_id: req.params.documentId,
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
