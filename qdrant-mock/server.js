const express = require('express');
const app = express();

app.use(express.json());

// Log all requests
app.use((req, res, next) => {
  console.log(`[QDRANT] ${req.method} ${req.path}`);
  next();
});

let collections = {};
let pointIdCounter = 0;

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/collections', (req, res) => {
  res.json({
    result: {
      collections: Object.keys(collections).map((name) => ({ name })),
    },
  });
});

app.put('/collections/:name', (req, res) => {
  const { name } = req.params;
  collections[name] = {
    name,
    points: [],
    vectors: req.body,
  };
  res.json({ result: { status: 'ok' } });
});

// Handle both POST /upsert and PUT /points
const handleUpsert = (req, res) => {
  console.log(`[QDRANT] Upsert request for collection: ${req.params.name}`);
  const { name } = req.params;
  const { points } = req.body;

  console.log(`[QDRANT] Points to upsert: ${points ? points.length : 0}`);

  if (!collections[name]) {
    console.log(`[QDRANT] Collection doesn't exist, creating...`);
    collections[name] = { name, points: [] };
  }

  if (!points || !Array.isArray(points)) {
    console.log(`[QDRANT] ERROR: Invalid points`);
    return res.status(400).json({ error: 'Invalid points' });
  }

  points.forEach((point) => {
    const index = collections[name].points.findIndex((p) => p.id === point.id);
    if (index >= 0) {
      collections[name].points[index] = point;
    } else {
      collections[name].points.push(point);
    }
  });

  console.log(`[QDRANT] ✓ Upserted ${points.length} points`);
  res.json({ result: { status: 'ok', operation_id: 1 } });
};

app.post('/collections/:name/points/upsert', handleUpsert);
app.put('/collections/:name/points', handleUpsert);

app.post('/collections/:name/points/search', (req, res) => {
  const { name } = req.params;
  const { vector, limit = 5, query_filter } = req.body;

  const collection = collections[name];
  if (!collection) {
    return res.json({ result: [] });
  }

  const scores = collection.points.map((point) => {
    let score = 0.7; // Default score for mock
    if (point.vector && point.vector.dense) {
      const dense = point.vector.dense;
      if (Array.isArray(vector.vector)) {
        score = cosineSimilarity(vector.vector, dense);
      }
    }
    return { ...point, score };
  });

  const sorted = scores.sort((a, b) => b.score - a.score).slice(0, limit);

  res.json({ result: sorted });
});

function cosineSimilarity(a, b) {
  if (a.length !== b.length) return 0;
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  normA = Math.sqrt(normA);
  normB = Math.sqrt(normB);

  return normA === 0 || normB === 0 ? 0 : dotProduct / (normA * normB);
}

const PORT = 6333;
app.listen(PORT, () => {
  console.log(`Mock Qdrant server running on port ${PORT}`);
}).on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.log(`Port ${PORT} already in use`);
    process.exit(1);
  }
  throw err;
});

process.on('SIGINT', () => {
  console.log('\nQdrant server stopping...');
  process.exit(0);
});
