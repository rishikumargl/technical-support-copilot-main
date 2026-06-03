import React, { useState, useEffect } from 'react';
import {
  FiPlay,
  FiLoader,
  FiCheck,
  FiAlertCircle,
  FiGitBranch,
  FiZap,
  FiActivity,
} from 'react-icons/fi';
import {
  processDocument,
  getIngestionProgress,
  generateEmbeddings,
  getEmbeddingProgress,
  batchProcessDocuments,
  batchGenerateEmbeddings,
  getIngestionStrategiesComparison,
  getEmbeddingStats,
  getDocuments,
} from '../api/ragApi';
import './RAGPipeline.css';

function RAGPipeline() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState({});
  const [embedding, setEmbedding] = useState({});
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [activeTab, setActiveTab] = useState('ingestion');
  const [stats, setStats] = useState(null);
  const [strategies, setStrategies] = useState({});

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await getDocuments();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProcessDocument = async (documentId) => {
    try {
      setProcessing(prev => ({ ...prev, [documentId]: 'processing' }));

      await processDocument(documentId, {
        strategy: 'semantic',
        chunkSize: 512,
        overlapSize: 128,
      });

      // Poll for progress
      const progressInterval = setInterval(async () => {
        const progress = await getIngestionProgress(documentId);
        if (progress.progress === 100) {
          clearInterval(progressInterval);
          setProcessing(prev => ({ ...prev, [documentId]: 'completed' }));
          await fetchDocuments();
        }
      }, 1000);

      setTimeout(() => {
        clearInterval(progressInterval);
      }, 10000);
    } catch (error) {
      console.error('Processing error:', error);
      setProcessing(prev => ({ ...prev, [documentId]: 'error' }));
    }
  };

  const handleGenerateEmbeddings = async (documentId) => {
    try {
      setEmbedding(prev => ({ ...prev, [documentId]: 'processing' }));

      await generateEmbeddings(documentId);

      // Poll for progress
      const progressInterval = setInterval(async () => {
        const progress = await getEmbeddingProgress(documentId);
        const percentage = Math.round(progress.progress_percentage || 0);
        if (percentage === 100) {
          clearInterval(progressInterval);
          setEmbedding(prev => ({ ...prev, [documentId]: 'completed' }));
          await fetchDocuments();
        }
      }, 1000);

      setTimeout(() => {
        clearInterval(progressInterval);
      }, 10000);
    } catch (error) {
      console.error('Embedding error:', error);
      setEmbedding(prev => ({ ...prev, [documentId]: 'error' }));
    }
  };

  const handleBatchProcess = async () => {
    if (selectedDocs.length === 0) {
      alert('Select at least one document');
      return;
    }

    try {
      setProcessing(prev => {
        const newState = { ...prev };
        selectedDocs.forEach(id => (newState[id] = 'processing'));
        return newState;
      });

      await batchProcessDocuments(selectedDocs, 'semantic');

      setTimeout(() => {
        setProcessing(prev => {
          const newState = { ...prev };
          selectedDocs.forEach(id => (newState[id] = 'completed'));
          return newState;
        });
        fetchDocuments();
        setSelectedDocs([]);
      }, 2000);
    } catch (error) {
      console.error('Batch processing error:', error);
    }
  };

  const handleBatchEmbedding = async () => {
    if (selectedDocs.length === 0) {
      alert('Select at least one document');
      return;
    }

    try {
      setEmbedding(prev => {
        const newState = { ...prev };
        selectedDocs.forEach(id => (newState[id] = 'processing'));
        return newState;
      });

      await batchGenerateEmbeddings(selectedDocs);

      setTimeout(() => {
        setEmbedding(prev => {
          const newState = { ...prev };
          selectedDocs.forEach(id => (newState[id] = 'completed'));
          return newState;
        });
        fetchDocuments();
        setSelectedDocs([]);
      }, 2000);
    } catch (error) {
      console.error('Batch embedding error:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processing':
        return <FiLoader className="spin" />;
      case 'completed':
        return <FiCheck />;
      case 'error':
        return <FiAlertCircle />;
      default:
        return <FiPlay />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'processing':
        return '#f59e0b';
      case 'completed':
        return '#4ade80';
      case 'error':
        return '#ef4444';
      default:
        return '#60a5fa';
    }
  };

  return (
    <div className="rag-pipeline">
      <div className="pipeline-header">
        <h2>RAG Pipeline Manager</h2>
        <p>Manage document ingestion and embedding generation</p>
      </div>

      {/* Tab Navigation */}
      <div className="pipeline-tabs">
        <button
          className={`tab-btn ${activeTab === 'ingestion' ? 'active' : ''}`}
          onClick={() => setActiveTab('ingestion')}
        >
          <FiGitBranch size={18} />
          Ingestion
        </button>
        <button
          className={`tab-btn ${activeTab === 'embeddings' ? 'active' : ''}`}
          onClick={() => setActiveTab('embeddings')}
        >
          <FiZap size={18} />
          Embeddings
        </button>
        <button
          className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          <FiActivity size={18} />
          Statistics
        </button>
      </div>

      {/* Ingestion Tab */}
      {activeTab === 'ingestion' && (
        <div className="pipeline-section">
          <div className="section-header">
            <h3>Document Ingestion</h3>
            <p>Parse documents and create chunks</p>
          </div>

          {documents.length === 0 && !loading && (
            <div className="empty-state">
              <p>No documents yet. Upload documents first.</p>
            </div>
          )}

          {loading ? (
            <div className="loading">
              <FiLoader className="spin" size={24} />
              Loading documents...
            </div>
          ) : (
            <>
              <div className="batch-controls">
                <div className="doc-selector">
                  <label>
                    <input
                      type="checkbox"
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedDocs(documents.map(d => d.id));
                        } else {
                          setSelectedDocs([]);
                        }
                      }}
                      checked={selectedDocs.length === documents.length && documents.length > 0}
                    />
                    Select All ({selectedDocs.length} selected)
                  </label>
                </div>
                <button
                  className="batch-action-btn"
                  onClick={handleBatchProcess}
                  disabled={selectedDocs.length === 0}
                >
                  <FiPlay size={16} />
                  Process Selected ({selectedDocs.length})
                </button>
              </div>

              <div className="documents-list">
                {documents.map(doc => (
                  <div key={doc.id} className="pipeline-item">
                    <div className="item-header">
                      <input
                        type="checkbox"
                        checked={selectedDocs.includes(doc.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedDocs([...selectedDocs, doc.id]);
                          } else {
                            setSelectedDocs(
                              selectedDocs.filter(id => id !== doc.id)
                            );
                          }
                        }}
                      />
                      <div className="item-info">
                        <h4>{doc.name}</h4>
                        <div className="item-meta">
                          {doc.metadata?.department && (
                            <span className="badge">{doc.metadata.department}</span>
                          )}
                          {doc.metadata?.category && (
                            <span className="badge">{doc.metadata.category}</span>
                          )}
                        </div>
                      </div>
                      <div className="item-status">
                        <span className="status-label">
                          {doc.chunk_count || 0} chunks
                        </span>
                        <span className="status-label">
                          {((doc.size || 0) / 1024).toFixed(1)} KB
                        </span>
                      </div>
                      <button
                        className="action-btn"
                        onClick={() => handleProcessDocument(doc.id)}
                        disabled={processing[doc.id] === 'processing'}
                        style={{ color: getStatusColor(processing[doc.id]) }}
                      >
                        {getStatusIcon(processing[doc.id])}
                        {processing[doc.id] === 'processing'
                          ? 'Processing...'
                          : processing[doc.id] === 'completed'
                          ? 'Processed'
                          : 'Process'}
                      </button>
                    </div>

                    {processing[doc.id] === 'processing' && (
                      <div className="progress-bar">
                        <div className="progress-fill"></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Embeddings Tab */}
      {activeTab === 'embeddings' && (
        <div className="pipeline-section">
          <div className="section-header">
            <h3>Embedding Generation</h3>
            <p>Generate vector embeddings using OpenAI</p>
          </div>

          {documents.length === 0 && !loading && (
            <div className="empty-state">
              <p>No documents to embed. Process documents first.</p>
            </div>
          )}

          {loading ? (
            <div className="loading">
              <FiLoader className="spin" size={24} />
              Loading documents...
            </div>
          ) : (
            <>
              <div className="batch-controls">
                <div className="doc-selector">
                  <label>
                    <input
                      type="checkbox"
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedDocs(documents.map(d => d.id));
                        } else {
                          setSelectedDocs([]);
                        }
                      }}
                      checked={selectedDocs.length === documents.length && documents.length > 0}
                    />
                    Select All ({selectedDocs.length} selected)
                  </label>
                </div>
                <button
                  className="batch-action-btn"
                  onClick={handleBatchEmbedding}
                  disabled={selectedDocs.length === 0}
                >
                  <FiZap size={16} />
                  Generate Embeddings ({selectedDocs.length})
                </button>
              </div>

              <div className="documents-list">
                {documents.map(doc => (
                  <div key={doc.id} className="pipeline-item">
                    <div className="item-header">
                      <input
                        type="checkbox"
                        checked={selectedDocs.includes(doc.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedDocs([...selectedDocs, doc.id]);
                          } else {
                            setSelectedDocs(
                              selectedDocs.filter(id => id !== doc.id)
                            );
                          }
                        }}
                      />
                      <div className="item-info">
                        <h4>{doc.name}</h4>
                        <p className="item-desc">
                          Chunks: {doc.chunk_count || 0}
                        </p>
                      </div>
                      <button
                        className="action-btn"
                        onClick={() => handleGenerateEmbeddings(doc.id)}
                        disabled={embedding[doc.id] === 'processing'}
                        style={{ color: getStatusColor(embedding[doc.id]) }}
                      >
                        {getStatusIcon(embedding[doc.id])}
                        {embedding[doc.id] === 'processing'
                          ? 'Embedding...'
                          : embedding[doc.id] === 'completed'
                          ? 'Embedded'
                          : 'Generate'}
                      </button>
                    </div>

                    {embedding[doc.id] === 'processing' && (
                      <div className="progress-bar">
                        <div className="progress-fill"></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Statistics Tab */}
      {activeTab === 'stats' && (
        <div className="pipeline-section">
          <div className="section-header">
            <h3>Pipeline Statistics</h3>
            <p>Overview of ingestion and embedding progress</p>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📄</div>
              <div className="stat-content">
                <h4>Total Documents</h4>
                <p className="stat-value">{documents.length}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <h4>Total Chunks</h4>
                <p className="stat-value">
                  {documents.reduce((sum, d) => sum + (d.chunk_count || 0), 0)}
                </p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">⚡</div>
              <div className="stat-content">
                <h4>Processed</h4>
                <p className="stat-value">
                  {documents.filter(d => d.chunk_count > 0).length}
                </p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">✨</div>
              <div className="stat-content">
                <h4>Model</h4>
                <p className="stat-value">text-embedding-3-small</p>
              </div>
            </div>
          </div>

          <div className="progress-section">
            <h4>Ingestion Progress</h4>
            {documents.length > 0 ? (
              <div className="progress-chart">
                {documents.map(doc => (
                  <div key={doc.id} className="progress-item">
                    <div className="progress-label">
                      <span>{doc.name}</span>
                      <span className="progress-value">
                        {((doc.chunk_count / 10) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${((doc.chunk_count / 10) * 100).toFixed(0)}%`,
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-message">No documents to display</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default RAGPipeline;
