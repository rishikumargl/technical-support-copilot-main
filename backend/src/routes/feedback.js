const express = require('express');
const Feedback = require('../models/Feedback');
const Response = require('../models/Response');

const router = express.Router();

router.post('/:responseId', async (req, res, next) => {
  try {
    const { helpful, comment = '', tags = [] } = req.body;

    const response = await Response.findById(req.params.responseId);
    if (!response) {
      return res.status(404).json({ error: 'Response not found' });
    }

    const feedback = await Feedback.create({
      responseId: req.params.responseId,
      helpful: helpful === true || helpful === 'true',
      comment,
      tags,
    });

    res.status(201).json({
      id: feedback.id,
      response_id: feedback.response_id,
      helpful: feedback.helpful,
      created_at: feedback.created_at,
    });
  } catch (error) {
    next(error);
  }
});

router.get('/analytics', async (req, res, next) => {
  try {
    const filters = {};

    if (req.query.startDate) {
      filters.startDate = new Date(req.query.startDate);
    }

    if (req.query.endDate) {
      filters.endDate = new Date(req.query.endDate);
    }

    const stats = await Feedback.getStats(filters);
    const tags = await Feedback.getTagStats();
    const ratingsByStrategy = await Feedback.getStrategyRatings();

    res.json({
      ...stats,
      most_common_tags: tags,
      ratings_by_strategy: ratingsByStrategy,
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
