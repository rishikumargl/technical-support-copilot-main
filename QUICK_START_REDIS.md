# Quick Start: Enable Redis Cloud Caching

**Time to enable: 5 minutes**

## 1. Get Credentials (2 min)

```
Visit: https://redis.com/try-free/
↓
Sign up → Create account
↓
"Create database" → Select "Free" → Region → Create
↓
Wait for DB to start (1-2 min)
↓
Copy connection string from Configuration tab
Format: redis://:PASSWORD@HOST:PORT
```

## 2. Update Backend Config (1 min)

Edit `backend/.env`:

```env
REDIS_ENABLED=true
REDIS_URL=redis://:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT
```

## 3. Install & Restart (2 min)

```bash
cd backend
npm install
npm start
```

## 4. Verify (30 sec)

Look for in logs:
```
[CACHE] Connected to cloud Redis
[CACHE] Redis cache initialized successfully
```

Done! ✅

---

## Test It

```bash
# Ask same query twice in frontend
Query: "What is a SOC?"
Response 1: ~1-3 seconds
Response 2: ~0.05 seconds ← 20-60x faster!
```

Check logs:
```
[CACHE] Hit: query:what is a soc?
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Connection refused" | Check Redis URL in `.env` |
| Still slow | Restart backend after `.env` change |
| Cache not working | Check `REDIS_ENABLED=true` |

See `REDIS_SETUP.md` for detailed troubleshooting.
