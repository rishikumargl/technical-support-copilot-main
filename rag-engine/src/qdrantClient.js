const { QdrantClient } = require('@qdrant/js-client-rest');

const client = new QdrantClient({
  url: process.env.QDRANT_URL || 'http://localhost:6333',
  apiKey: process.env.QDRANT_API_KEY,
  timeout: 10000,
});

async function initializeCollection(collectionName) {
  try {
    const collections = await client.getCollections();
    const exists = collections.result?.collections?.some((c) => c.name === collectionName) ||
                   collections.collections?.some((c) => c.name === collectionName);

    if (!exists) {
      console.log(`Creating collection '${collectionName}'...`);
      await client.createCollection(collectionName, {
        vectors: {
          dense: {
            size: 384,
            distance: 'Cosine',
          },
        },
      });
      console.log(`✓ Collection '${collectionName}' created.`);
    } else {
      console.log(`✓ Collection '${collectionName}' already exists.`);
    }
  } catch (error) {
    console.error('Collection initialization error:', error.message);
    console.log('Attempting to recreate collection...');
    try {
      await client.recreateCollection(collectionName, {
        vectors: {
          dense: {
            size: 384,
            distance: 'Cosine',
          },
        },
      });
      console.log(`✓ Collection '${collectionName}' recreated.`);
    } catch (e) {
      console.error('Recreate failed:', e.message);
    }
  }
}

async function upsertPoint(collectionName, point) {
  try {
    await client.upsert(collectionName, {
      points: [point],
    });
  } catch (error) {
    console.error('Upsert error:', error.message);
    throw error;
  }
}

async function hybridSearch(collectionName, denseVector, sparseVector, sparseIndices, filters = {}) {
  try {
    const results = await client.search(collectionName, {
      vector: {
        name: 'dense',
        vector: denseVector,
      },
      limit: 5,
      query_filter: filters && Object.keys(filters).length > 0 ? { must: Object.entries(filters).map(([key, value]) => ({ key, match: { value } })) } : undefined,
    });

    return Array.isArray(results) ? results : results.result || [];
  } catch (error) {
    console.error('Search error:', error.message);
    return [];
  }
}

module.exports = {
  client,
  initializeCollection,
  upsertPoint,
  hybridSearch,
};
