const pool = require('../config/database');
const { v4: uuidv4 } = require('uuid');

class Feedback {
  static async create(data) {
    const { responseId, helpful, comment, tags } = data;
    const id = uuidv4();

    const query = `
      INSERT INTO feedback (id, response_id, helpful, comment, tags)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;

    const result = await pool.query(query, [
      id,
      responseId,
      helpful,
      comment,
      tags || [],
    ]);

    return result.rows[0];
  }

  static async findByResponseId(responseId) {
    const query = 'SELECT * FROM feedback WHERE response_id = $1';
    const result = await pool.query(query, [responseId]);
    return result.rows;
  }

  static async getStats(filters = {}) {
    let query = 'SELECT helpful, COUNT(*) as count FROM feedback WHERE 1=1';
    const params = [];
    let paramCount = 1;

    if (filters.startDate) {
      query += ` AND created_at >= $${paramCount}`;
      params.push(filters.startDate);
      paramCount++;
    }

    if (filters.endDate) {
      query += ` AND created_at <= $${paramCount}`;
      params.push(filters.endDate);
      paramCount++;
    }

    query += ' GROUP BY helpful';

    const result = await pool.query(query, params);
    const rows = result.rows;

    const helpfulCount = rows.find(r => r.helpful === true)?.count || 0;
    const unhelpfulCount = rows.find(r => r.helpful === false)?.count || 0;
    const total = helpfulCount + unhelpfulCount;

    return {
      helpful_count: helpfulCount,
      unhelpful_count: unhelpfulCount,
      total_feedback: total,
      helpful_percentage: total > 0 ? ((helpfulCount / total) * 100).toFixed(1) : 0,
      unhelpful_percentage: total > 0 ? ((unhelpfulCount / total) * 100).toFixed(1) : 0,
    };
  }

  static async getTagStats() {
    const query = `
      SELECT
        tag,
        COUNT(*) as count
      FROM feedback, LATERAL unnest(tags) as tag
      WHERE tag IS NOT NULL
      GROUP BY tag
      ORDER BY count DESC
      LIMIT 10
    `;

    try {
      const result = await pool.query(query);
      return result.rows.map(r => r.tag);
    } catch (error) {
      return [];
    }
  }

  static async getStrategyRatings() {
    const query = `
      SELECT
        r.retrieval_strategy,
        AVG(CASE WHEN f.helpful THEN 1 ELSE 0 END) as helpful_rate
      FROM feedback f
      JOIN responses r ON f.response_id = r.id
      GROUP BY r.retrieval_strategy
    `;

    try {
      const result = await pool.query(query);
      const ratings = {};
      result.rows.forEach(row => {
        ratings[row.retrieval_strategy] = parseFloat(row.helpful_rate).toFixed(2);
      });
      return ratings;
    } catch (error) {
      return {};
    }
  }
}

module.exports = Feedback;
