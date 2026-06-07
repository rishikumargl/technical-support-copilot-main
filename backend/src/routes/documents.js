const express = require('express');
const axios = require('axios');
const upload = require('../middleware/multer');
const Document = require('../models/Document');
const Chunk = require('../models/Chunk');
const logger = require('../utils/logger');
const fs = require('fs');
const path = require('path');

const router = express.Router();

// RAG server URL
const RAG_SERVER_URL = process.env.RAG_SERVER_URL || 'http://localhost:5001';

// RAG ingestion data directory
const RAG_DATA_DIR = process.env.RAG_DATA_DIR || path.join(__dirname, '../../..', 'rag-layer', 'ingestion_pipeline', 'data');

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

    // Copy file to RAG ingestion directory
    const ragFileName = `${document.id}_${name}`;
    const ragFilePath = path.join(RAG_DATA_DIR, ragFileName);

    try {
      // Ensure RAG data directory exists
      if (!fs.existsSync(RAG_DATA_DIR)) {
        fs.mkdirSync(RAG_DATA_DIR, { recursive: true });
        logger.info('Created RAG data directory', { dir: RAG_DATA_DIR });
      }

      // Copy file to RAG ingestion directory
      await new Promise((resolve, reject) => {
        fs.copyFile(req.file.path, ragFilePath, (err) => {
          if (err) reject(err);
          else resolve();
        });
      });

      logger.info('Document copied to RAG ingestion directory', {
        originalPath: req.file.path,
        ragPath: ragFilePath,
        fileName: name
      });
    } catch (copyError) {
      logger.error('Failed to copy document to RAG directory', {
        error: copyError.message,
        ragFilePath
      });
      // Continue anyway - try to index from backend uploads
    }

    // Trigger automatic RAG server indexing
    const indexingTimeout = setTimeout(() => {
      logger.warn('Document indexing in RAG server is taking longer than expected');
    }, 35000); // Warn if takes more than 35 seconds

    try {
      logger.info('Triggering RAG server to index document', { fileName: name, ragFileName });

      const ragResponse = await axios.post(
        `${RAG_SERVER_URL}/api/rag/ingest`,
        { document_id: ragFileName },
        { timeout: 300000 } // 5 minute timeout to match RAG server
      );

      clearTimeout(indexingTimeout);

      if (ragResponse.data && ragResponse.data.success) {
        logger.info('Document indexed successfully in RAG server', { ragFileName, fileName: name });

        res.status(201).json({
          document_id: document.id,
          name: document.name,
          chunk_count: 0,
          status: 'indexed_and_searchable',
          message: 'Document uploaded and indexed. Now available for search.',
          rag_status: ragResponse.data.result?.status || 'indexed',
        });
      } else {
        logger.warn('RAG server indexing failed', {
          ragFileName,
          error: ragResponse.data?.error || 'Unknown error'
        });

        res.status(201).json({
          document_id: document.id,
          name: document.name,
          chunk_count: 0,
          status: 'uploaded_but_not_indexed',
          message: 'Document uploaded but RAG indexing failed. Available via keyword search only.',
          rag_error: ragResponse.data?.error,
        });
      }
    } catch (ragError) {
      clearTimeout(indexingTimeout);
      logger.error('Failed to contact RAG server for indexing', {
        ragFileName,
        error: ragError.message
      });

      // Still accept the upload even if RAG indexing fails
      res.status(201).json({
        document_id: document.id,
        name: document.name,
        chunk_count: 0,
        status: 'uploaded_no_rag',
        message: 'Document uploaded but RAG server unavailable. Use keyword search or restart RAG server.',
        rag_error: ragError.message,
      });
    }
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
