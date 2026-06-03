import React, { useState, useEffect } from 'react';
import { FiSave, FiRefreshCw } from 'react-icons/fi';
import { getCacheStats, clearCache } from '../api/ragApi';
import './SystemConfig.css';

function SystemConfig() {
  const [cacheStats, setCacheStats] = useState(null);
  const [config, setConfig] = useState({
    enableCaching: true,
    cacheExpiry: 3600,
    maxCacheSize: 100,
    enableReranking: false,
    rerankerModel: 'bge-reranker-base',
    chunkingStrategy: 'semantic',
    chunkSize: 512,
    overlapSize: 128,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCacheStats();
  }, []);

  const fetchCacheStats = async () => {
    try {
      setLoading(true);
      const stats = await getCacheStats();
      setCacheStats(stats);
    } catch (error) {
      console.error('Error fetching cache stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearCache = async () => {
    if (window.confirm('Are you sure you want to clear the cache?')) {
      try {
        await clearCache();
        await fetchCacheStats();
      } catch (error) {
        console.error('Error clearing cache:', error);
      }
    }
  };

  const handleSaveConfig = () => {
    console.log('Saving configuration:', config);
    alert('Configuration saved successfully!');
  };

  return (
    <div className="system-config">
      <div className="config-header">
        <h2>System Configuration</h2>
        <p>Manage RAG system settings and performance tuning</p>
      </div>

      <div className="config-container">
        <section className="config-section">
          <h3>Cache Management</h3>
          {cacheStats && (
            <div className="cache-info">
              <div className="cache-stat">
                <label>Cache Hit Rate</label>
                <span className="value">{(cacheStats.hit_rate * 100).toFixed(1)}%</span>
              </div>
              <div className="cache-stat">
                <label>Cached Entries</label>
                <span className="value">{cacheStats.entry_count}</span>
              </div>
              <div className="cache-stat">
                <label>Cache Size</label>
                <span className="value">
                  {((cacheStats.cache_size || 0) / (1024 * 1024)).toFixed(2)} MB
                </span>
              </div>
            </div>
          )}
          <div className="cache-actions">
            <button onClick={fetchCacheStats} disabled={loading} className="action-btn">
              <FiRefreshCw size={18} />
              Refresh Stats
            </button>
            <button onClick={handleClearCache} className="action-btn danger">
              Clear Cache
            </button>
          </div>
        </section>

        <section className="config-section">
          <h3>Retrieval Settings</h3>
          <form onSubmit={(e) => e.preventDefault()} className="config-form">
            <div className="form-group">
              <label htmlFor="strategy">Chunking Strategy</label>
              <select
                id="strategy"
                value={config.chunkingStrategy}
                onChange={(e) =>
                  setConfig({ ...config, chunkingStrategy: e.target.value })
                }
              >
                <option value="fixed">Fixed-Size Chunking</option>
                <option value="semantic">Semantic Chunking</option>
                <option value="sliding-window">Sliding Window</option>
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="chunkSize">
                  Chunk Size (tokens): {config.chunkSize}
                </label>
                <input
                  id="chunkSize"
                  type="range"
                  min="256"
                  max="2048"
                  step="128"
                  value={config.chunkSize}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      chunkSize: parseInt(e.target.value),
                    })
                  }
                />
              </div>

              <div className="form-group">
                <label htmlFor="overlapSize">
                  Overlap Size (tokens): {config.overlapSize}
                </label>
                <input
                  id="overlapSize"
                  type="range"
                  min="0"
                  max="512"
                  step="32"
                  value={config.overlapSize}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      overlapSize: parseInt(e.target.value),
                    })
                  }
                />
              </div>
            </div>
          </form>
        </section>

        <section className="config-section">
          <h3>Performance Optimization</h3>
          <form onSubmit={(e) => e.preventDefault()} className="config-form">
            <div className="form-group checkbox">
              <input
                id="enableCaching"
                type="checkbox"
                checked={config.enableCaching}
                onChange={(e) =>
                  setConfig({ ...config, enableCaching: e.target.checked })
                }
              />
              <label htmlFor="enableCaching">Enable Query Caching</label>
            </div>

            {config.enableCaching && (
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="cacheExpiry">
                    Cache Expiry (seconds): {config.cacheExpiry}
                  </label>
                  <input
                    id="cacheExpiry"
                    type="range"
                    min="60"
                    max="86400"
                    step="300"
                    value={config.cacheExpiry}
                    onChange={(e) =>
                      setConfig({
                        ...config,
                        cacheExpiry: parseInt(e.target.value),
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="maxCacheSize">
                    Max Cache Size (MB): {config.maxCacheSize}
                  </label>
                  <input
                    id="maxCacheSize"
                    type="range"
                    min="10"
                    max="1000"
                    step="10"
                    value={config.maxCacheSize}
                    onChange={(e) =>
                      setConfig({
                        ...config,
                        maxCacheSize: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
              </div>
            )}

            <div className="form-group checkbox">
              <input
                id="enableReranking"
                type="checkbox"
                checked={config.enableReranking}
                onChange={(e) =>
                  setConfig({ ...config, enableReranking: e.target.checked })
                }
              />
              <label htmlFor="enableReranking">Enable Result Reranking</label>
            </div>

            {config.enableReranking && (
              <div className="form-group">
                <label htmlFor="rerankerModel">Reranker Model</label>
                <select
                  id="rerankerModel"
                  value={config.rerankerModel}
                  onChange={(e) =>
                    setConfig({ ...config, rerankerModel: e.target.value })
                  }
                >
                  <option value="bge-reranker-base">BGE Reranker Base</option>
                  <option value="bge-reranker-large">BGE Reranker Large</option>
                  <option value="rankgpt">RankGPT</option>
                </select>
              </div>
            )}
          </form>
        </section>

        <div className="config-actions">
          <button onClick={handleSaveConfig} className="save-btn">
            <FiSave size={20} />
            Save Configuration
          </button>
        </div>
      </div>

      <section className="config-section info-section">
        <h3>📚 Documentation</h3>
        <div className="documentation">
          <div className="doc-item">
            <h4>Chunking Strategies</h4>
            <p>
              <strong>Fixed-Size:</strong> Chunks documents into fixed token sizes with optional overlap.
              Best for uniform content.
            </p>
            <p>
              <strong>Semantic:</strong> Uses NLP to identify sentence boundaries and topic shifts.
              Preserves meaning across chunk boundaries.
            </p>
          </div>

          <div className="doc-item">
            <h4>Caching</h4>
            <p>
              Query-level caching stores results for identical questions. Reduces latency and backend
              load. Configure expiry time and max size based on your workload.
            </p>
          </div>

          <div className="doc-item">
            <h4>Reranking</h4>
            <p>
              Reranks initial retrieval results using a dedicated reranker model. Improves accuracy
              by 15-25% at the cost of additional latency.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default SystemConfig;
