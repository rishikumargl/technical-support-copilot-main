const pool = require('../config/database');
const { v4: uuidv4 } = require('uuid');

class Response {
  static async create(data) {
    const { query, answer, confidenceScore, retrievalStrategy, retrievalTimeMs, chunkIds, metadata } = data;
    const id = uuidv4();

    const query_str = `
      INSERT INTO responses (id, query, answer, confidence_score, retrieval_strategy, retrieval_time_ms, chunk_ids, metadata)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING *
    `;

    const result = await pool.query(query_str, [
      id,
      query,
      answer,
      confidenceScore,
      retrievalStrategy,
      retrievalTimeMs,
      chunkIds || [],
      JSON.stringify(metadata || {}),
    ]);

    return result.rows[0];
  }

  static async findById(id) {
    const query = 'SELECT * FROM responses WHERE id = $1';
    const result = await pool.query(query, [id]);
    return result.rows[0];
  }

  static async findRecent(limit = 50) {
    const query = `
      SELECT * FROM responses
      ORDER BY created_at DESC
      LIMIT $1
    `;
    const result = await pool.query(query, [limit]);
    return result.rows;
  }

  static async findByStrategy(strategy, limit = 50) {
    const query = `
      SELECT * FROM responses
      WHERE retrieval_strategy = $1
      ORDER BY created_at DESC
      LIMIT $2
    `;
    const result = await pool.query(query, [strategy, limit]);
    return result.rows;
  }

  static async getAverageConfidence(strategy = null) {
    let query = 'SELECT AVG(confidence_score) as avg_confidence FROM responses';
    const params = [];

    if (strategy) {
      query += ' WHERE retrieval_strategy = $1';
      params.push(strategy);
    }

    const result = await pool.query(query, params);
    return result.rows[0].avg_confidence || 0;
  }

  static async getStrategyStats() {
    const query = `
      SELECT
        retrieval_strategy,
        COUNT(*) as count,
        AVG(confidence_score) as avg_confidence,
        AVG(retrieval_time_ms) as avg_time_ms
      FROM responses
      GROUP BY retrieval_strategy
    `;
    const result = await pool.query(query);
    return result.rows;
  }
}

module.exports = Response;
