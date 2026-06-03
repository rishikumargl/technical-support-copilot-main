require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');

const { initializeDatabase } = require('./db/init');
const logger = require('./utils/logger');
const errorHandler = require('./middleware/errorHandler');

// Import routes
const documentsRouter = require('./routes/documents');
const ragRouter = require('./routes/rag');
const chunksRouter = require('./routes/chunks');
const feedbackRouter = require('./routes/feedback');
const systemRouter = require('./routes/system');
const cacheRouter = require('./routes/cache');
const metadataRouter = require('./routes/metadata');

const app = express();
const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || 'localhost';

app.use(helmet());
app.use(compression());

app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

const limiter = rateLimit({
  windowMs: parseInt(process.env.API_RATE_LIMIT_WINDOW) || 900000,
  max: parseInt(process.env.API_RATE_LIMIT) || 100,
  message: 'Too many requests from this IP, please try again later.',
});

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

app.use('/api/', limiter);

app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.use('/api/documents', documentsRouter);
app.use('/api/rag', ragRouter);
app.use('/api/chunks', chunksRouter);
app.use('/api/feedback', feedbackRouter);
app.use('/api/system', systemRouter);
app.use('/api/cache', cacheRouter);
app.use('/api/metadata', metadataRouter);

app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

app.use(errorHandler);

const startServer = async () => {
  try {
    logger.info('Initializing database...');
    await initializeDatabase();
    logger.info('Database initialized successfully');

    app.listen(PORT, HOST, () => {
      logger.info(`Server running at http://${HOST}:${PORT}`);
      logger.info('API base URL: http://' + HOST + ':' + PORT + '/api');
    });
  } catch (error) {
    logger.error('Failed to start server', error);
    process.exit(1);
  }
};

startServer();

process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

module.exports = app;
