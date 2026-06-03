import client from './client';

// Chat Query (with HuggingFace inference)
export const chatQuery = async (query, filters = {}) => {
  return client.post('/chat/query', {
    query,
    filters,
    use_cache: true,
  });
};

// Query API (fallback keyword search)
export const queryRAG = async (query, filters = {}) => {
  return client.post('/rag/query', {
    query,
    filters,
  });
};

// Advanced Query with specific retrieval strategy
export const queryRAGAdvanced = async (query, options = {}) => {
  return client.post('/rag/query-advanced', {
    query,
    retrieval_strategy: options.strategy || 'hybrid', // 'vector', 'bm25', 'hybrid'
    top_k: options.topK || 5,
    similarity_threshold: options.threshold || 0.5,
    filters: options.filters || {},
    rerank: options.rerank || false,
  });
};

// Document Upload
export const uploadDocument = async (file, metadata = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('metadata', JSON.stringify(metadata));

  return client.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Get all documents
export const getDocuments = async (filters = {}) => {
  return client.get('/documents', {
    params: filters,
  });
};

// Get document details
export const getDocumentById = async (documentId) => {
  return client.get(`/documents/${documentId}`);
};

// Delete document
export const deleteDocument = async (documentId) => {
  return client.delete(`/documents/${documentId}`);
};

// Get document chunks
export const getDocumentChunks = async (documentId) => {
  return client.get(`/documents/${documentId}/chunks`);
};

// Search chunks
export const searchChunks = async (query, strategy = 'hybrid') => {
  return client.post('/chunks/search', {
    query,
    strategy,
    top_k: 10,
  });
};

// Feedback - Mark response as helpful/unhelpful
export const submitFeedback = async (responseId, feedback) => {
  return client.post(`/feedback/${responseId}`, {
    helpful: feedback.helpful,
    comment: feedback.comment || '',
    tags: feedback.tags || [],
  });
};

// Get feedback analytics
export const getFeedbackAnalytics = async (filters = {}) => {
  return client.get('/feedback/analytics', {
    params: filters,
  });
};

// RAG System health and statistics
export const getSystemStats = async () => {
  return client.get('/system/stats');
};

// Get retrieval comparison results
export const getRetrievalComparison = async (query) => {
  return client.post('/system/retrieval-comparison', {
    query,
  });
};

// Export:  Get chunking strategy comparison
export const getChunkingComparison = async (documentId) => {
  return client.get(`/system/chunking-comparison/${documentId}`);
};

// Metadata filters - Get available filter options
export const getMetadataFilters = async () => {
  return client.get('/metadata/filters');
};

// Access control - Check user permissions
export const checkPermission = async (resource, action) => {
  return client.post('/access-control/check', {
    resource,
    action,
  });
};

// Get audit logs
export const getAuditLogs = async (filters = {}) => {
  return client.get('/audit/logs', {
    params: filters,
  });
};

// Caching - Get cache statistics
export const getCacheStats = async () => {
  return client.get('/cache/stats');
};

// Clear cache
export const clearCache = async () => {
  return client.post('/cache/clear');
};

// ==========================================
// INGESTION PIPELINE API
// ==========================================

// Process document - Parse and chunk
export const processDocument = async (documentId, options = {}) => {
  return client.post(`/ingestion/process/${documentId}`, {
    chunkingStrategy: options.strategy || 'semantic',
    chunkSize: options.chunkSize || 512,
    overlapSize: options.overlapSize || 128,
  });
};

// Get ingestion progress
export const getIngestionProgress = async (documentId) => {
  return client.get(`/ingestion/progress/${documentId}`);
};

// Batch ingestion - Process multiple documents
export const batchProcessDocuments = async (documentIds, strategy = 'semantic') => {
  return client.post('/ingestion/batch', {
    documentIds,
    chunkingStrategy: strategy,
  });
};

// Get ingestion strategies comparison for a document
export const getIngestionStrategiesComparison = async (documentId) => {
  return client.get(`/ingestion/strategies/${documentId}`);
};

// ==========================================
// EMBEDDINGS API
// ==========================================

// Generate embeddings for a document
export const generateEmbeddings = async (documentId) => {
  return client.post(`/embeddings/generate/${documentId}`);
};

// Get embedding generation progress
export const getEmbeddingProgress = async (documentId) => {
  return client.get(`/embeddings/progress/${documentId}`);
};

// Batch generate embeddings for multiple documents
export const batchGenerateEmbeddings = async (documentIds) => {
  return client.post('/embeddings/batch', {
    documentIds,
  });
};

// Get embedding statistics
export const getEmbeddingStats = async () => {
  return client.get('/embeddings/stats');
};
