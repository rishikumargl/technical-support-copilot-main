# Redis Cloud Caching Setup Guide

This guide walks you through setting up cloud-based Redis caching to dramatically improve query performance.

## What You Get

- **97% faster responses** for repeated queries (1-3s → 50-100ms)
- **Automatic cache invalidation** when new documents are ingested
- **No local infrastructure** needed - fully managed by Redis Cloud
- **Scalable** - from free tier to production clusters

## Step-by-Step Setup

### Step 1: Create Redis Cloud Account

1. Go to **https://redis.com/try-free/**
2. Click "Sign up for free"
3. Fill in your details and verify email
4. Login to Redis Cloud console

### Step 2: Create a Database

1. Click **"Create a database"** or **"New database"**
2. Select plan: **Free** (30MB - perfect for dev/testing)
3. Region: Choose closest to your location
4. Database name: `rag-cache` or your preference
5. Click **"Create"**

Wait for database to initialize (1-2 minutes)

### Step 3: Get Connection Credentials

1. Click on your database name
2. In the **"Configuration"** tab, find:
   - **Public endpoint** (e.g., `redis-12345.c123.us-east-1-2.ec2.cloud.redisLabs.com:12345`)
   - **Default user password** (or create a new one)

The connection string format is:
```
redis://:PASSWORD@HOST:PORT
```

Example:
```
redis://:mySecurePassword123@redis-12345.c123.us-east-1-2.ec2.cloud.redisLabs.com:12345
```

### Step 4: Update Backend Environment

**File: `backend/.env`**

```env
# Enable Redis caching
REDIS_ENABLED=true

# Paste your Redis Cloud connection string
REDIS_URL=redis://:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT
```

Replace with your actual credentials from Step 3.

### Step 5: Install Dependencies

```bash
cd backend
npm install
cd ..
```

This installs the `redis` npm package.

### Step 6: Start Backend

```bash
cd backend
npm start
```

You should see logs like:
```
[STARTUP] Backend server running on port 5001
[CACHE] Connected to cloud Redis
[CACHE] Redis cache initialized successfully
```

### Step 7: Test It Works

1. Open frontend: http://localhost:3001
2. Ask a query (e.g., "What is a SOC?")
3. First response takes ~1-3 seconds
4. **Ask the exact same query again**
5. Second response takes ~50-100ms (look for `[CACHE] Hit:` in backend logs)

## Troubleshooting

### "Connection refused"

**Problem**: Redis URL is invalid or network blocked

**Solution**:
1. Double-check your Redis Cloud credentials in `.env`
2. Verify database is running (green status in Redis Cloud console)
3. Check if your network blocks Redis port (12375+ typically)

### "ECONNREFUSED 127.0.0.1:6379"

**Problem**: Backend trying to connect to local Redis instead of cloud

**Solution**:
1. Ensure `.env` has correct `REDIS_URL` (should have `.redis.cloud` in hostname)
2. Restart backend after updating `.env`

### Cache not working (logs show "Redis disabled")

**Problem**: `REDIS_ENABLED=false` or connection failed silently

**Solution**:
1. Check `.env` has `REDIS_ENABLED=true`
2. Verify `REDIS_URL` is not empty
3. Check backend logs for connection errors
4. If no logs appear about Redis, run:
   ```bash
   echo "REDIS_ENABLED=true" >> backend/.env
   npm start
   ```

### High latency from cache

**Problem**: Cloud Redis adds network roundtrip time

**Normal**: 10-50ms extra network latency is expected. You'll still see 10-20x speedup overall (with synthesis).

**Optimize**:
- Use Redis database in same region as your backend
- Monitor with `[CACHE]` log lines

## API Reference

### Cache Behavior

| Scenario | Behavior |
|----------|----------|
| Query with filters | **Not cached** (filters make results unique) |
| Repeated query (no filters) | **Cache hit** - returns in <100ms |
| New document ingested | **Cache cleared** - next query rebuilds cache |
| Backend restart | **Cache persists** - Redis Cloud retains data |

### Manual Cache Control

In backend code, you can:

```javascript
import { flushCache } = require('./src/cacheService');

// Clear all cache
await flushCache();

// Or use Redis Cloud console
// Tools > Console > `FLUSHDB`
```

## Cost Estimate

- **Free tier**: 30MB, 1,000 commands/sec
  - Perfect for: Development, testing, <100 users
  - Cost: **$0/month**

- **Paid tiers**: Starting at $7/month
  - Perfect for: Small production deployments
  - Includes: Backups, replication, 99.99% uptime SLA

## Next Steps

1. **Monitor cache effectiveness**: Check logs for `[CACHE] Hit:` vs misses
2. **Adjust TTL**: Currently set to 3600s (1 hour) - modify in `backend/src/cacheService.js`
3. **Scale**: As users grow, upgrade to paid Redis plan in console

## Security Best Practices

1. **Rotate password** - Change default password in Redis Cloud console
2. **Network ACL** - Restrict to your backend IP (optional)
3. **Never commit credentials** - Always use `.env` files
4. **Sensitive data** - Don't cache PII; current setup only caches queries + responses

## Disable Caching

To go back to no caching:

```bash
# In backend/.env, change:
REDIS_ENABLED=false
```

Restart backend. It will work normally without cache.
