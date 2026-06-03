const express = require('express');
const Response = require('../models/Response');
const Chunk = require('../models/Chunk');
const cache = require('../utils/cache');
const logger = require('../utils/logger');

const router = express.Router();

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
    const chunks = await Chunk.search(query, 5);
    const retrievalTime = Date.now() - startTime;

    const response = {
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
      status: 'RAG_NOT_IMPLEMENTED',
      message: 'Embedding and vector search not yet implemented. Showing keyword search results only.',
      retrieval_time_ms: retrievalTime,
    };

    const dbResponse = await Response.create({
      query,
      answer: response.answer,
      confidenceScore: response.confidence_score,
      retrievalStrategy: 'keyword',
      retrievalTimeMs: retrievalTime,
      chunkIds: chunks.map(c => c.id),
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

    let chunks = await Chunk.search(query, top_k);

    const retrievalTime = Date.now() - startTime;

    const response = {
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
      status: 'RAG_NOT_IMPLEMENTED',
      message: 'Embedding and vector search not yet implemented. Showing keyword search results only.',
      retrieval_method: retrieval_strategy,
      rerank_applied: rerank,
      search_time_ms: retrievalTime,
    };

    const dbResponse = await Response.create({
      query,
      answer: response.answer,
      confidenceScore: response.confidence_score,
      retrievalStrategy: retrieval_strategy,
      retrievalTimeMs: retrievalTime,
      chunkIds: chunks.map(c => c.id),
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

module.exports = router;
