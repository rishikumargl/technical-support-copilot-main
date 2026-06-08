const redis = require('redis');

let client = null;
let isEnabled = process.env.REDIS_ENABLED === 'true';

async function initCache() {
  if (!isEnabled) {
    console.log('[CACHE] Redis disabled (REDIS_ENABLED not set)');
    return;
  }

  try {
    client = redis.createClient({
      url: process.env.REDIS_URL,
      socket: {
        reconnectStrategy: (retries) => Math.min(retries * 50, 500),
      },
    });

    client.on('error', (err) => {
      console.error('[CACHE] Redis error:', err.message);
      isEnabled = false;
    });

    client.on('connect', () => {
      console.log('[CACHE] Connected to cloud Redis');
    });

    await client.connect();
    console.log('[CACHE] Redis cache initialized successfully');
  } catch (error) {
    console.error('[CACHE] Failed to initialize Redis:', error.message);
    console.log('[CACHE] Continuing without caching...');
    isEnabled = false;
  }
}

async function getCache(key) {
  if (!isEnabled || !client) return null;
  try {
    const value = await client.get(key);
    if (value) {
      console.log('[CACHE] Hit:', key);
      return JSON.parse(value);
    }
    return null;
  } catch (error) {
    console.error('[CACHE] Get error:', error.message);
    return null;
  }
}

async function setCache(key, value, ttl = 3600) {
  if (!isEnabled || !client) return;
  try {
    await client.setEx(key, ttl, JSON.stringify(value));
    console.log('[CACHE] Set:', key, `(TTL: ${ttl}s)`);
  } catch (error) {
    console.error('[CACHE] Set error:', error.message);
  }
}

async function deleteCache(key) {
  if (!isEnabled || !client) return;
  try {
    await client.del(key);
    console.log('[CACHE] Deleted:', key);
  } catch (error) {
    console.error('[CACHE] Delete error:', error.message);
  }
}

async function flushCache() {
  if (!isEnabled || !client) return;
  try {
    await client.flushDb();
    console.log('[CACHE] Flushed all cache');
  } catch (error) {
    console.error('[CACHE] Flush error:', error.message);
  }
}

async function closeCache() {
  if (client) {
    try {
      await client.quit();
      console.log('[CACHE] Connection closed');
    } catch (error) {
      console.error('[CACHE] Close error:', error.message);
    }
  }
}

module.exports = { initCache, getCache, setCache, deleteCache, flushCache, closeCache };
