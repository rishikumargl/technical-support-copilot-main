import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiSliders, FiLoader } from 'react-icons/fi';
import ChatMessage from '../components/ChatMessage';
import { queryRAGAdvanced, submitFeedback } from '../api/ragApi';
import toastManager from '../utils/toastManager';
import 'katex/dist/katex.min.css';
import './ChatInterface.css';

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      type: 'assistant',
      content:
        'Welcome to the RAG Assistant! I can help you troubleshoot technical issues. Ask me questions about error codes, system issues, or best practices.',
      strategy: 'hybrid',
      timestamp: new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      }),
    },
  ]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    strategy: 'hybrid',
    department: '',
    topK: 5,
    threshold: 0.5,
    rerank: false,
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await queryRAGAdvanced(query, {
        strategy: filters.strategy,
        topK: filters.topK,
        threshold: filters.threshold,
        rerank: filters.rerank,
        filters: filters.department ? { department: filters.department } : {},
      });

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer || response.response || 'No answer available.',
        sources: response.sources || [],
        strategy: filters.strategy,
        confidence: response.confidence_score,
        status: response.status,
        message: response.message,
        timestamp: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      toastManager.success('Query processed successfully');
    } catch (error) {
      console.error('Query error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `Error: ${error.message || 'Failed to retrieve answer. Please try again.'}`,
        strategy: filters.strategy,
        timestamp: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        }),
      };

      setMessages((prev) => [...prev, errorMessage]);
      toastManager.error(`Failed to process query: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (feedback) => {
    try {
      await submitFeedback(feedback.responseId, {
        helpful: feedback.helpful,
        comment: '',
      });
      console.log('Feedback submitted:', feedback);
      toastManager.success('Feedback submitted successfully');
    } catch (error) {
      console.error('Feedback error:', error);
      toastManager.error('Failed to submit feedback');
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Technical Support Copilot</h2>
        <p>Ask questions about troubleshooting, errors, and best practices</p>
      </div>

      <div className="chat-container">
        <div className="messages-area">
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              onFeedback={handleFeedback}
            />
          ))}
          {loading && (
            <div className="loading-message">
              <div className="spinner" />
              <p>Searching knowledge base...</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-section">
          {showFilters && (
            <div className="filters-panel">
              <div className="filter-group">
                <label>Retrieval Strategy</label>
                <select
                  value={filters.strategy}
                  onChange={(e) =>
                    setFilters({ ...filters, strategy: e.target.value })
                  }
                >
                  <option value="hybrid">Hybrid (Vector + BM25)</option>
                  <option value="vector">Vector Search Only</option>
                  <option value="bm25">BM25 Only</option>
                </select>
              </div>

              <div className="filter-group">
                <label>Department Filter</label>
                <select
                  value={filters.department}
                  onChange={(e) =>
                    setFilters({ ...filters, department: e.target.value })
                  }
                >
                  <option value="">All Departments</option>
                  <option value="engineering">Engineering</option>
                  <option value="support">Support</option>
                  <option value="operations">Operations</option>
                  <option value="hr">Human Resources</option>
                </select>
              </div>

              <div className="filter-group">
                <label>Top K Results: {filters.topK}</label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={filters.topK}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      topK: parseInt(e.target.value),
                    })
                  }
                />
              </div>

              <div className="filter-group">
                <label>Similarity Threshold: {filters.threshold.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={filters.threshold}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      threshold: parseFloat(e.target.value),
                    })
                  }
                />
              </div>

              <div className="filter-group checkbox">
                <input
                  type="checkbox"
                  id="rerank"
                  checked={filters.rerank}
                  onChange={(e) =>
                    setFilters({ ...filters, rerank: e.target.checked })
                  }
                />
                <label htmlFor="rerank">Enable Reranking</label>
              </div>
            </div>
          )}

          <form onSubmit={handleQuery} className="input-form">
            <div className="input-wrapper">
              <input
                type="text"
                placeholder="Ask a question... (e.g., 'How do I troubleshoot CrashLoopBackOff?')"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
                className="input-field"
              />
              <button
                type="button"
                className="filter-toggle"
                onClick={() => setShowFilters(!showFilters)}
                title="Advanced Filters"
              >
                <FiSliders size={20} />
              </button>
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="send-button"
              >
                {loading ? (
                  <FiLoader size={20} className="spin" />
                ) : (
                  <FiSend size={20} />
                )}
              </button>
            </div>
          </form>

          <p className="input-hint">
            💡 Use filters to compare retrieval strategies and refine search results
          </p>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
