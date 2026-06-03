const express = require('express');
const cache = require('../utils/cache');

const router = express.Router();

router.get('/stats', (req, res) => {
  const stats = cache.getStats();
  res.json(stats);
});

router.post('/clear', (req, res) => {
  const entriesRemoved = cache.clear();
  res.json({
    status: 'cleared',
    entries_removed: entriesRemoved,
  });
});

module.exports = router;
