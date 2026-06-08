require('dotenv').config();
const path = require('path');

// Clear require cache
delete require.cache[require.resolve('../rag-engine/src/queryClassifier')];

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { classifyQuery } = require('../rag-engine/src/queryClassifier');
const { retrieveAndSynthesize } = require('../rag-engine/src/retrievalPipeline');
const { ingestDocument, extractTextFromPDF } = require('../rag-engine/src/documentIngestion');
const { initializeCollection } = require('../rag-engine/src/qdrantClient');
const { validateChatPayload } = require('./src/inputSanitizer');
const { aggregateResponse, errorResponse } = require('./src/responseAggregator');
const { initCache, getCache, setCache, flushCache, closeCache } = require('./src/cacheService');

const app = express();
const PORT = process.env.PORT || 3000;
const COLLECTION_NAME = 'technical_docs';

app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb' }));

let initialized = false;

async function initializeApp() {
  try {
    await initializeCollection(COLLECTION_NAME);
    await initCache();
    initialized = true;
    console.log('Application initialized successfully.');
  } catch (error) {
    console.error('Initialization error:', error.message);
    console.log('Continuing anyway - service degraded');
    initialized = true;
  }
}

app.post('/api/chat', async (req, res) => {
  console.log('\n[CHAT] =====REQUEST=====');
  console.log('[CHAT] Time:', new Date().toISOString());
  console.log('[CHAT] Query:', req.body.query);
  console.log('[CHAT] Filters:', req.body.filters);

  try {
    if (!initialized) {
      console.log('[CHAT] ERROR: Not initialized');
      return res.status(503).json({ error: 'Service not ready' });
    }

    const validation = validateChatPayload(req.body);
    if (!validation.valid) {
      console.log('[CHAT] ERROR: Validation failed -', validation.error);
      return res.status(400).json({ error: validation.error });
    }

    const { query, filters, collectionName } = validation.data;
    const cleanFilters = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== '')
    );

    // Check cache only if no filters
    const hasFilters = Object.keys(cleanFilters).length > 0;
    if (!hasFilters) {
      const cacheKey = `query:${query.toLowerCase()}`;
      const cachedResult = await getCache(cacheKey);
      if (cachedResult) {
        console.log('[CHAT] Using cached response');
        console.log('[CHAT] =====SUCCESS=====\n');
        return res.json(cachedResult);
      }
    }

    console.log('[CHAT] Classifying query...');
    const classification = await classifyQuery(query);
    console.log(`[CHAT] Classification: ${classification}`);

    if (classification === 'CHAT') {
      console.log('[CHAT] Mode: CHAT (no database lookup)');
      const chatResponse = aggregateResponse(
        {
          response: `I understand you're asking: "${query}". I'm designed to help with technical support. Please ask me about specific errors, troubleshooting steps, or configuration issues.`,
          sources: [],
          score: 0,
          status: 'CHAT_MODE',
        },
        query
      );
      console.log('[CHAT] =====SUCCESS=====\n');
      return res.json(chatResponse);
    }

    console.log('[CHAT] Mode: RETRIEVE (database lookup)');
    console.log('[CHAT] Calling retrieveAndSynthesize...');
    const result = await retrieveAndSynthesize(query, collectionName || COLLECTION_NAME, cleanFilters);
    console.log('[CHAT] Result score:', result.score);

    const response = aggregateResponse(result, query);

    // Cache for 1 hour if no filters
    if (!hasFilters) {
      await setCache(`query:${query.toLowerCase()}`, response, 3600);
    }

    console.log('[CHAT] =====SUCCESS=====\n');
    return res.json(response);
  } catch (error) {
    console.error('[CHAT] =====ERROR=====');
    console.error('[CHAT] Message:', error.message);
    console.error('[CHAT] Stack:', error.stack);
    console.error('[CHAT] =====END ERROR=====\n');
    return res.status(500).json(errorResponse(error, req.body.query || ''));
  }
});

app.post('/api/ingest', async (req, res) => {
  console.log('\n[INGEST] =====START=====');
  console.log('[INGEST] Document:', req.body.documentName);
  console.log('[INGEST] Initialized:', initialized);

  try {
    if (!initialized) {
      console.log('[INGEST] ERROR: Not initialized');
      return res.status(503).json({ error: 'Service not ready' });
    }

    const { documentName, metadata } = req.body;
    const fileBuffer = Buffer.from(req.body.fileContent, 'base64');

    console.log('[INGEST] Buffer size:', fileBuffer.length, 'bytes');
    console.log('[INGEST] Metadata:', JSON.stringify(metadata));

    if (!documentName || !fileBuffer || fileBuffer.length === 0) {
      console.log('[INGEST] ERROR: Missing data');
      return res.status(400).json({ error: 'Missing documentName or fileContent' });
    }

    console.log('[INGEST] Calling ingestDocument...');
    const result = await ingestDocument(fileBuffer, documentName, COLLECTION_NAME, metadata);
    console.log('[INGEST] Result:', result);

    // Clear cache after ingestion since new documents are available
    console.log('[INGEST] Clearing query cache...');
    await flushCache();

    console.log('[INGEST] =====SUCCESS=====\n');

    return res.json({
      success: true,
      message: 'Document ingested successfully',
      ...result,
    });
  } catch (error) {
    console.error('[INGEST] =====ERROR=====');
    console.error('[INGEST] Message:', error.message);
    console.error('[INGEST] Code:', error.code);
    console.error('[INGEST] Stack:', error.stack);
    console.error('[INGEST] =====END ERROR=====\n');

    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    initialized,
    timestamp: new Date().toISOString(),
  });
});

const server = app.listen(PORT, () => {
  console.log(`[STARTUP] Backend server running on port ${PORT} - timestamp: ${new Date().toISOString()}`);
  initializeApp().catch(err => console.error('Init failed:', err.message));
});

server.on('error', (err) => {
  console.error('Server error:', err);
});

process.on('SIGINT', async () => {
  console.log('\nShutting down...');
  await closeCache();
  server.close();
});

module.exports = app;
