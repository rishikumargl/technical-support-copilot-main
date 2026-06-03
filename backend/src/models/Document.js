const pool = require('../config/database');
const { v4: uuidv4 } = require('uuid');

class Document {
  static async create(data) {
    const { name, filePath, fileSize, fileType, metadata, department, category, version, documentType } = data;
    const id = uuidv4();

    const query = `
      INSERT INTO documents (id, name, file_path, file_size, file_type, department, category, version, document_type, metadata)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING *
    `;

    const result = await pool.query(query, [
      id,
      name,
      filePath,
      fileSize,
      fileType,
      department,
      category,
      version,
      documentType,
      JSON.stringify(metadata || {}),
    ]);

    return result.rows[0];
  }

  static async findById(id) {
    const query = 'SELECT * FROM documents WHERE id = $1';
    const result = await pool.query(query, [id]);
    return result.rows[0];
  }

  static async findAll(filters = {}, skip = 0, limit = 10) {
    let query = 'SELECT * FROM documents WHERE 1=1';
    const params = [];
    let paramCount = 1;

    if (filters.department) {
      query += ` AND department = $${paramCount}`;
      params.push(filters.department);
      paramCount++;
    }

    if (filters.category) {
      query += ` AND category = $${paramCount}`;
      params.push(filters.category);
      paramCount++;
    }

    if (filters.version) {
      query += ` AND version = $${paramCount}`;
      params.push(filters.version);
      paramCount++;
    }

    query += ` ORDER BY created_at DESC LIMIT $${paramCount} OFFSET $${paramCount + 1}`;
    params.push(limit, skip);

    const result = await pool.query(query, params);
    return result.rows;
  }

  static async count(filters = {}) {
    let query = 'SELECT COUNT(*) FROM documents WHERE 1=1';
    const params = [];
    let paramCount = 1;

    if (filters.department) {
      query += ` AND department = $${paramCount}`;
      params.push(filters.department);
      paramCount++;
    }

    if (filters.category) {
      query += ` AND category = $${paramCount}`;
      params.push(filters.category);
      paramCount++;
    }

    const result = await pool.query(query, params);
    return parseInt(result.rows[0].count);
  }

  static async delete(id) {
    const query = 'DELETE FROM documents WHERE id = $1 RETURNING *';
    const result = await pool.query(query, [id]);
    return result.rows[0];
  }

  static async updateChunkCount(id, count) {
    const query = 'UPDATE documents SET chunk_count = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING *';
    const result = await pool.query(query, [count, id]);
    return result.rows[0];
  }
}

module.exports = Document;
