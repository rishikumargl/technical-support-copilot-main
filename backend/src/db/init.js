const pool = require('../config/database');
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

const initializeDatabase = async () => {
  try {
    logger.info('Initializing database...');

    // Create documents table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        file_path TEXT,
        file_size BIGINT,
        file_type VARCHAR(10),
        chunk_count INT DEFAULT 0,
        department VARCHAR(100),
        category VARCHAR(100),
        version VARCHAR(50),
        document_type VARCHAR(50),
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create chunks table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS chunks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        position INT NOT NULL,
        content TEXT NOT NULL,
        embedding TEXT,
        tokens INT,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create responses table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS responses (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        query TEXT NOT NULL,
        answer TEXT,
        confidence_score NUMERIC(3,2),
        retrieval_strategy VARCHAR(50),
        retrieval_time_ms INT,
        chunk_ids TEXT[],
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create feedback table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS feedback (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        response_id UUID NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
        helpful BOOLEAN,
        comment TEXT,
        tags TEXT[],
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create search metrics table
    await pool.query(`
      CREATE TABLE IF NOT EXISTS search_metrics (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        query TEXT NOT NULL,
        strategy VARCHAR(50) NOT NULL,
        results_count INT,
        accuracy NUMERIC(3,2),
        precision NUMERIC(3,2),
        avg_time_ms NUMERIC(10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create indexes
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_documents_department ON documents(department)
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id)
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_responses_created_at ON responses(created_at)
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_feedback_response_id ON feedback(response_id)
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_search_metrics_strategy ON search_metrics(strategy)
    `);

    logger.info('Database initialized successfully');
    return true;
  } catch (error) {
    logger.error('Database initialization failed', error);
    throw error;
  }
};

module.exports = { initializeDatabase };
