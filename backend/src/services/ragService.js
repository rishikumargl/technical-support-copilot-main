const { spawn } = require('child_process');
const path = require('path');
const logger = require('../utils/logger');

/**
 * RAG Service - Bridge between Node.js backend and Python RAG layer
 * Uses subprocess to call Python's RAG integration pipeline
 */

class RAGService {
  constructor() {
    this.pythonPath = process.env.PYTHON_PATH || 'python';
    this.ragScriptPath = process.env.RAG_SCRIPT_PATH ||
      path.join(__dirname, '../../..', 'rag-layer', 'rag_bridge.py');
    this.initialized = false;
  }

  /**
   * Initialize RAG system - call once at startup
   */
  async initialize() {
    try {
      if (this.initialized) {
        logger.info('RAG Service already initialized');
        return { success: true };
      }

      logger.info('Initializing RAG Service...');

      // Import and initialize the RAG pipeline
      const result = await this.executePythonCommand('initialize', {});

      if (result.success) {
        this.initialized = true;
        logger.info('RAG Service initialized successfully');
      }

      return result;
    } catch (error) {
      logger.error('Failed to initialize RAG Service', error);
      throw error;
    }
  }

  /**
   * Query the RAG system
   */
  async query(question, options = {}) {
    try {
      const {
        topK = 5,
        searchType = 'hybrid',
        department = null,
        category = null,
        threshold = 0.5,
      } = options;

      const params = {
        question,
        top_k: topK,
        search_type: searchType,
        department,
        category,
        threshold,
      };

      logger.info(`RAG Query: ${question}`, { params });

      const result = await this.executePythonCommand('query', params);

      if (!result.success) {
        logger.warn('RAG query failed', result);
        return {
          success: false,
          error: result.error || 'Unknown error',
          results: [],
        };
      }

      return {
        success: true,
        results: result.results || [],
        metadata: result.metadata || {},
      };
    } catch (error) {
      logger.error('RAG query error', error);
      throw error;
    }
  }

  /**
   * Run the complete ingestion pipeline
   */
  async runIngestionPipeline(sourceDir, options = {}) {
    try {
      const {
        outputDir = './output',
        chunkingStrategy = 'fixed',
      } = options;

      const params = {
        source_dir: sourceDir,
        output_dir: outputDir,
        chunking_strategy: chunkingStrategy,
      };

      logger.info('Running RAG ingestion pipeline', { params });

      const result = await this.executePythonCommand('ingest', params);

      return result;
    } catch (error) {
      logger.error('Ingestion pipeline error', error);
      throw error;
    }
  }

  /**
   * Get RAG system statistics
   */
  async getStats() {
    try {
      const result = await this.executePythonCommand('stats', {});
      return result;
    } catch (error) {
      logger.error('Failed to get RAG stats', error);
      throw error;
    }
  }

  /**
   * Execute Python command via subprocess
   * This bridges Python and Node.js
   */
  async executePythonCommand(command, params) {
    return new Promise((resolve, reject) => {
      try {
        // For now, we'll use a simpler approach: direct Python import
        // In production, you'd use a dedicated service or subprocess

        // This is a placeholder - we'll implement actual Python bridge below
        const mockResult = {
          success: false,
          command,
          message: 'Python bridge not yet implemented in this environment',
        };

        // Resolve immediately with mock response
        setTimeout(() => resolve(mockResult), 100);
      } catch (error) {
        reject(error);
      }
    });
  }
}

module.exports = new RAGService();
