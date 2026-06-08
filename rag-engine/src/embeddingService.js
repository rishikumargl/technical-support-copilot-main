const OpenAI = require('openai');

const client = new OpenAI({
  apiKey: 'ollama',
  baseURL: 'http://localhost:11434/v1',
});

async function generateDenseEmbedding(text) {
  try {
    console.log('[EMBEDDING] Calling Ollama nomic-embed-text...');
    const response = await client.embeddings.create({
      model: 'nomic-embed-text',
      input: text.slice(0, 512),
    });
    console.log('[EMBEDDING] ✓ Got Ollama embedding, size:', response.data[0].embedding.length);
    return response.data[0].embedding;
  } catch (error) {
    console.error('[EMBEDDING] Ollama call failed:', error.message);
    console.log('[EMBEDDING] Using hash fallback');
    return hashTextToEmbedding(text);
  }
}

function hashTextToEmbedding(text) {
  const embedding = Array(384).fill(0);
  let hash = 0;

  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }

  for (let i = 0; i < 384; i++) {
    const seed = hash + i;
    embedding[i] = ((Math.sin(seed) * 10000) % 2) - 1;
  }

  let magnitude = 0;
  for (let i = 0; i < embedding.length; i++) {
    magnitude += embedding[i] * embedding[i];
  }
  magnitude = Math.sqrt(magnitude);

  for (let i = 0; i < embedding.length; i++) {
    embedding[i] = magnitude > 0 ? embedding[i] / magnitude : 0;
  }

  return embedding;
}

function generateSparseVector(text) {
  const tokens = text.toLowerCase().split(/\W+/);
  const frequencies = {};

  tokens.forEach((token) => {
    if (token.length > 0) {
      frequencies[token] = (frequencies[token] || 0) + 1;
    }
  });

  return frequencies;
}

module.exports = {
  generateDenseEmbedding,
  generateSparseVector,
};
