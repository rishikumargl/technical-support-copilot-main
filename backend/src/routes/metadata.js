const express = require('express');
const pool = require('../config/database');

const router = express.Router();

router.get('/filters', async (req, res, next) => {
  try {
    const departments = await pool.query(
      'SELECT DISTINCT department FROM documents WHERE department IS NOT NULL ORDER BY department'
    );
    const categories = await pool.query(
      'SELECT DISTINCT category FROM documents WHERE category IS NOT NULL ORDER BY category'
    );
    const versions = await pool.query(
      'SELECT DISTINCT version FROM documents WHERE version IS NOT NULL ORDER BY version'
    );
    const types = await pool.query(
      'SELECT DISTINCT file_type FROM documents WHERE file_type IS NOT NULL ORDER BY file_type'
    );

    res.json({
      departments: departments.rows.map(r => r.department).filter(Boolean),
      categories: categories.rows.map(r => r.category).filter(Boolean),
      versions: versions.rows.map(r => r.version).filter(Boolean),
      document_types: types.rows.map(r => r.file_type).filter(Boolean),
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
