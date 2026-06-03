-- Documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  file_path TEXT,
  file_size BIGINT,
  file_type VARCHAR(10),
  chunk_count INT DEFAULT 0,
  department VARCHAR(100),
  category VARCHAR(100),
  version VARCHAR(50),
  document_type VARCHAR(50),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_documents_department (department),
  INDEX idx_documents_category (category),
  INDEX idx_documents_created_at (created_at)
);

-- Chunks table
CREATE TABLE IF NOT EXISTS chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  position INT NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  tokens INT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_chunks_document_id (document_id),
  INDEX idx_chunks_position (position),
  INDEX idx_chunks_embedding (embedding)
);

-- Responses table (for tracking RAG responses)
CREATE TABLE IF NOT EXISTS responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query TEXT NOT NULL,
  answer TEXT,
  confidence_score DECIMAL(3,2),
  retrieval_strategy VARCHAR(50),
  retrieval_time_ms INT,
  chunk_ids TEXT[],
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_responses_created_at (created_at),
  INDEX idx_responses_strategy (retrieval_strategy)
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  response_id UUID NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
  helpful BOOLEAN,
  comment TEXT,
  tags TEXT[],
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_feedback_response_id (response_id),
  INDEX idx_feedback_helpful (helpful),
  INDEX idx_feedback_created_at (created_at)
);

-- Search metrics table (for retrieval comparison)
CREATE TABLE IF NOT EXISTS search_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query TEXT NOT NULL,
  strategy VARCHAR(50) NOT NULL,
  results_count INT,
  accuracy DECIMAL(3,2),
  precision DECIMAL(3,2),
  avg_time_ms DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_search_metrics_strategy (strategy),
  INDEX idx_search_metrics_created_at (created_at)
);

-- Create indexes for better performance
CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);
CREATE INDEX idx_chunks_metadata ON chunks USING GIN(metadata);
CREATE INDEX idx_responses_metadata ON responses USING GIN(metadata);
