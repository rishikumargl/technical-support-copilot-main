const express = require('express');
const axios = require('axios');
const Response = require('../models/Response');
const Chunk = require('../models/Chunk');
const cache = require('../utils/cache');
const logger = require('../utils/logger');

const router = express.Router();

// RAG server URL
const RAG_SERVER_URL = process.env.RAG_SERVER_URL || 'http://localhost:5001';

/**
 * Helper function to call RAG server
 */
async function queryRAGServer(endpoint, data) {
  try {
    const response = await axios.post(`${RAG_SERVER_URL}/api/rag${endpoint}`, data, {
      timeout: 30000,
    });
    return response.data;
  } catch (error) {
    logger.error(`RAG server error on ${endpoint}:`, error.message);
    // Fallback to keyword search if RAG server unavailable
    return null;
  }
}

router.post('/query', async (req, res, next) => {
  try {
    const { query, filters = {} } = req.body;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: 'Query cannot be empty' });
    }

    const cacheKey = `query:${query}:${JSON.stringify(filters)}`;
    const cached = cache.get(cacheKey);

    if (cached) {
      return res.json(cached);
    }

    const startTime = Date.now();

    // Try RAG server first
    const ragResult = await queryRAGServer('/query', {
      question: query,
      top_k: filters.topK || 5,
      search_type: filters.strategy || 'hybrid',
      department: filters.department,
      category: filters.category,
    });

    let response;
    let chunkIds = [];

    if (ragResult && ragResult.success) {
      // Use RAG result
      response = {
        answer: ragResult.answer || 'No answer available.',
        sources: ragResult.sources || [],
        confidence_score: ragResult.confidence_score || 0,
        status: 'RAG_IMPLEMENTED',
        message: 'Retrieved from RAG system with embeddings and hybrid search.',
        retrieval_time_ms: Date.now() - startTime,
      };
    } else {
      // Fallback to keyword search
      logger.warn('RAG server unavailable, falling back to keyword search');
      const chunks = await Chunk.search(query, 5);
      chunkIds = chunks.map(c => c.id);

      response = {
        answer: chunks.length > 0
          ? chunks.map(c => c.content).join('\n\n')
          : 'No relevant information found in the knowledge base.',
        sources: chunks.map(chunk => ({
          document_name: chunk.document_name,
          chunk: chunk.content.substring(0, 200),
          relevance_score: null,
          metadata: chunk.document_metadata,
        })),
        confidence_score: null,
        status: 'FALLBACK_KEYWORD_SEARCH',
        message: 'RAG server unavailable. Showing keyword search results.',
        retrieval_time_ms: Date.now() - startTime,
      };
    }

    // Save to database
    const dbResponse = await Response.create({
      query,
      answer: response.answer,
      confidenceScore: response.confidence_score,
      retrievalStrategy: response.status === 'RAG_IMPLEMENTED' ? 'hybrid' : 'keyword',
      retrievalTimeMs: response.retrieval_time_ms,
      chunkIds: chunkIds.length > 0 ? chunkIds : undefined,
    });

    cache.set(cacheKey, response);

    res.json(response);
  } catch (error) {
    next(error);
  }
});

router.post('/query-advanced', async (req, res, next) => {
  try {
    const {
      query,
      retrieval_strategy = 'hybrid',
      top_k = 5,
      similarity_threshold = 0.5,
      filters = {},
      rerank = false,
    } = req.body;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: 'Query cannot be empty' });
    }

    const cacheKey = `query-advanced:${query}:${retrieval_strategy}:${top_k}`;
    const cached = cache.get(cacheKey);

    if (cached && process.env.ENABLE_CACHE === 'true') {
      return res.json(cached);
    }

    const startTime = Date.now();

    // Try RAG server first
    const ragResult = await queryRAGServer('/query-advanced', {
      query,
      retrieval_strategy,
      top_k,
      similarity_threshold,
      filters,
      rerank,
    });

    let response;
    let chunkIds = [];

    if (ragResult && ragResult.success) {
      // Use RAG result
      const retrievalTime = Date.now() - startTime;
      response = {
        answer: ragResult.answer || 'No answer available.',
        sources: ragResult.sources || [],
        confidence_score: ragResult.confidence_score || 0,
        status: 'RAG_IMPLEMENTED',
        message: 'Retrieved from RAG system with advanced options.',
        retrieval_method: retrieval_strategy,
        rerank_applied: rerank,
        search_time_ms: retrievalTime,
      };
    } else {
      // Fallback to keyword search
      logger.warn('RAG server unavailable, falling back to keyword search');
      const chunks = await Chunk.search(query, top_k);
      chunkIds = chunks.map(c => c.id);
      const retrievalTime = Date.now() - startTime;

      response = {
        answer: chunks.length > 0
          ? chunks.map(c => c.content).join('\n\n')
          : 'No relevant information found in the knowledge base.',
        sources: chunks.map((chunk, idx) => ({
          document_name: chunk.document_name,
          chunk: chunk.content.substring(0, 300),
          relevance_score: null,
          metadata: chunk.document_metadata,
        })),
        confidence_score: null,
        status: 'FALLBACK_KEYWORD_SEARCH',
        message: 'RAG server unavailable. Showing keyword search results only.',
        retrieval_method: retrieval_strategy,
        rerank_applied: rerank,
        search_time_ms: retrievalTime,
      };
    }

    // Save to database
    const dbResponse = await Response.create({
      query,
      answer: response.answer,
      confidenceScore: response.confidence_score,
      retrievalStrategy: response.status === 'RAG_IMPLEMENTED' ? retrieval_strategy : 'keyword',
      retrievalTimeMs: response.search_time_ms,
      chunkIds: chunkIds.length > 0 ? chunkIds : undefined,
      metadata: { top_k, threshold: similarity_threshold, rerank },
    });

    if (process.env.ENABLE_CACHE === 'true') {
      cache.set(cacheKey, response);
    }

    res.json(response);
  } catch (error) {
    next(error);
  }
});

/**
 * Initialize RAG system
 */
router.post('/initialize', async (req, res, next) => {
  try {
    const data = req.body || {};

    logger.info('Initializing RAG system...');

    const ragResult = await queryRAGServer('/initialize', data);

    if (ragResult && ragResult.success) {
      res.json({
        success: true,
        message: 'RAG system initialized successfully',
        result: ragResult.result,
      });
    } else {
      res.status(500).json({
        success: false,
        error: ragResult?.error || 'Failed to initialize RAG',
      });
    }
  } catch (error) {
    next(error);
  }
});

/**
 * Get RAG statistics
 */
router.get('/stats', async (req, res, next) => {
  try {
    const ragResult = await queryRAGServer('/stats', {});

    if (ragResult && ragResult.success) {
      res.json({
        success: true,
        stats: ragResult.stats,
      });
    } else {
      res.status(500).json({
        success: false,
        error: ragResult?.error || 'Failed to get RAG stats',
      });
    }
  } catch (error) {
    next(error);
  }
});

module.exports = router;
