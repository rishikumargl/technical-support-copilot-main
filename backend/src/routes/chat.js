const express = require('express');
const axios = require('axios');
const Response = require('../models/Response');
const Chunk = require('../models/Chunk');
const cache = require('../utils/cache');
const logger = require('../utils/logger');

const router = express.Router();

// RAG service URL (Python RAG module)
const RAG_SERVICE_URL = process.env.RAG_SERVICE_URL || 'http://localhost:8000';

/**
 * POST /api/chat/query
 * Query the RAG system with HuggingFace inference
 * Returns: { answer, sources, confidence, model }
 */
router.post('/query', async (req, res, next) => {
  try {
    const { query, filters = {}, use_cache = true } = req.body;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: 'Query cannot be empty' });
    }

    // Check cache
    const cacheKey = `chat:${query}:${JSON.stringify(filters)}`;
    if (use_cache) {
      const cached = cache.get(cacheKey);
      if (cached) {
        logger.info(`Cache hit for query: ${query.substring(0, 50)}`);
        return res.json(cached);
      }
    }

    const startTime = Date.now();

    try {
      // Try to get response from RAG service with HuggingFace inference
      logger.info(`Calling RAG service for query: ${query.substring(0, 50)}`);

      const ragResponse = await axios.post(`${RAG_SERVICE_URL}/api/chat/query`, {
        query,
        filters,
      }, {
        timeout: 30000, // 30 second timeout
      });

      const retrievalTime = Date.now() - startTime;

      const response = {
        answer: ragResponse.data.answer || 'No answer generated',
        sources: ragResponse.data.sources || [],
        confidence: ragResponse.data.confidence || 0,
        model: ragResponse.data.model || 'huggingface-inference',
        retrieval_time_ms: retrievalTime,
        status: 'OK',
        message: 'Answer generated with HuggingFace inference',
      };

      // Store in database
      try {
        await Response.create({
          query,
          answer: response.answer,
          confidenceScore: response.confidence,
          retrievalStrategy: 'huggingface-rag',
          retrievalTimeMs: retrievalTime,
          chunkIds: [],
          metadata: {
            sources: response.sources,
            model: response.model,
          },
        });
      } catch (dbError) {
        logger.error('Failed to store response in database', dbError);
        // Don't fail the request if DB storage fails
      }

      // Cache the response
      cache.set(cacheKey, response);

      res.json(response);
    } catch (ragError) {
      logger.warn(`RAG service error: ${ragError.message}, falling back to keyword search`);

      // Fallback: keyword search without AI generation
      const chunks = await Chunk.search(query, 5);
      const retrievalTime = Date.now() - startTime;

      const fallbackResponse = {
        answer: chunks.length > 0
          ? `Keyword search results:\n\n${chunks.map((c, i) => `${i + 1}. ${c.content.substring(0, 200)}...`).join('\n\n')}`
          : 'No relevant information found in the knowledge base.',
        sources: chunks.map(chunk => ({
          document: chunk.document_name,
          version: chunk.document_metadata?.version || '1.0',
          department: chunk.document_metadata?.department || 'Unknown',
          category: chunk.document_metadata?.category || 'Unknown',
          confidence: 0.5,
        })),
        confidence: chunks.length > 0 ? 0.5 : 0,
        model: 'keyword-search-fallback',
        retrieval_time_ms: retrievalTime,
        status: 'FALLBACK',
        message: 'Using keyword search. RAG service unavailable.',
      };

      try {
        await Response.create({
          query,
          answer: fallbackResponse.answer,
          confidenceScore: fallbackResponse.confidence,
          retrievalStrategy: 'keyword-fallback',
          retrievalTimeMs: retrievalTime,
          chunkIds: chunks.map(c => c.id),
          metadata: { fallback: true },
        });
      } catch (dbError) {
        logger.error('Failed to store fallback response', dbError);
      }

      cache.set(cacheKey, fallbackResponse);
      res.json(fallbackResponse);
    }
  } catch (error) {
    next(error);
  }
});

/**
 * POST /api/chat/feedback
 * Send feedback on an answer
 */
router.post('/feedback', async (req, res, next) => {
  try {
    const { response_id, is_helpful, comments = '' } = req.body;

    if (!response_id || typeof is_helpful !== 'boolean') {
      return res.status(400).json({ error: 'Invalid feedback data' });
    }

    // Store feedback in database
    const feedback = await Response.createFeedback(response_id, is_helpful, comments);

    res.json({
      status: 'success',
      message: 'Feedback recorded',
      feedback_id: feedback.id,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/chat/history
 * Get chat history
 */
router.get('/history', async (req, res, next) => {
  try {
    const limit = parseInt(req.query.limit) || 20;
    const offset = parseInt(req.query.offset) || 0;

    const responses = await Response.findAll({
      limit,
      offset,
      order: [['createdAt', 'DESC']],
    });

    res.json({
      data: responses,
      limit,
      offset,
      total: responses.length,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/chat/status
 * Check if RAG service is available
 */
router.get('/status', async (req, res) => {
  try {
    const response = await axios.get(`${RAG_SERVICE_URL}/health`, {
      timeout: 5000,
    });

    res.json({
      rag_service: 'online',
      rag_url: RAG_SERVICE_URL,
      status: 'ok',
    });
  } catch (error) {
    res.json({
      rag_service: 'offline',
      rag_url: RAG_SERVICE_URL,
      status: 'error',
      message: 'RAG service is not available',
      fallback: 'Using keyword search',
    });
  }
});

module.exports = router;
