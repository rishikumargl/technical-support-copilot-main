const pool = require('../config/database');
const { v4: uuidv4 } = require('uuid');

class Chunk {
  static async create(data) {
    const { documentId, position, content, embedding, tokens, metadata } = data;
    const id = uuidv4();

    const query = `
      INSERT INTO chunks (id, document_id, position, content, embedding, tokens, metadata)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `;

    const result = await pool.query(query, [
      id,
      documentId,
      position,
      content,
      embedding ? JSON.stringify(embedding) : null,
      tokens,
      JSON.stringify(metadata || {}),
    ]);

    return result.rows[0];
  }

  static async findById(id) {
    const query = 'SELECT * FROM chunks WHERE id = $1';
    const result = await pool.query(query, [id]);
    return result.rows[0];
  }

  static async findByDocumentId(documentId) {
    const query = 'SELECT * FROM chunks WHERE document_id = $1 ORDER BY position ASC';
    const result = await pool.query(query, [documentId]);
    return result.rows;
  }

  static async findByDocumentIdPaginated(documentId, skip = 0, limit = 10) {
    const query = `
      SELECT * FROM chunks
      WHERE document_id = $1
      ORDER BY position ASC
      LIMIT $2 OFFSET $3
    `;
    const result = await pool.query(query, [documentId, limit, skip]);
    return result.rows;
  }

  static async countByDocumentId(documentId) {
    const query = 'SELECT COUNT(*) FROM chunks WHERE document_id = $1';
    const result = await pool.query(query, [documentId]);
    return parseInt(result.rows[0].count);
  }

  static async deleteByDocumentId(documentId) {
    const query = 'DELETE FROM chunks WHERE document_id = $1';
    await pool.query(query, [documentId]);
  }

  static async search(query, limit = 10) {
    const searchQuery = `
      SELECT c.*, d.name as document_name, d.metadata as document_metadata
      FROM chunks c
      JOIN documents d ON c.document_id = d.id
      WHERE c.content ILIKE '%' || $1 || '%'
      LIMIT $2
    `;
    const result = await pool.query(searchQuery, [query, limit]);
    return result.rows;
  }
}

module.exports = Chunk;
