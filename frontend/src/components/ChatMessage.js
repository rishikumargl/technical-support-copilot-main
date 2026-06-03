import React, { useState } from 'react';
import { FiThumbsUp, FiThumbsDown, FiCopy, FiCheck } from 'react-icons/fi';
import './ChatMessage.css';

function ChatMessage({ message, onFeedback }) {
  const [copiedId, setCopiedId] = useState(null);
  const [feedbackGiven, setFeedbackGiven] = useState(null);

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleFeedback = (helpful) => {
    setFeedbackGiven(helpful);
    if (onFeedback) {
      onFeedback({ helpful, responseId: message.id });
    }
  };

  if (message.type === 'user') {
    return (
      <div className="chat-message user-message">
        <div className="message-content">
          <p>{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-message assistant-message">
      <div className="message-header">
        <span className="model-badge">
          {message.model ? `${message.model}` : 'RAG Assistant'}
        </span>
        <span className="strategy-badge">{message.strategy || 'hybrid'}</span>
      </div>

      <div className="message-content">
        <div className="response-text">
          <p>{message.content}</p>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="sources-section">
            <h4>📚 Sources</h4>
            <div className="sources-list">
              {message.sources.map((source, idx) => (
                <div key={idx} className="source-item">
                  <div className="source-header">
                    <span className="source-doc">
                      {source.document || source.document_name}
                    </span>
                    <span className="source-meta">
                      {(source.department || source.metadata?.department) && (
                        <span className="meta-tag">{source.department || source.metadata.department}</span>
                      )}
                      {(source.category || source.metadata?.category) && (
                        <span className="meta-tag">{source.category || source.metadata.category}</span>
                      )}
                    </span>
                  </div>
                  {source.chunk && <p className="source-content">{source.chunk}</p>}
                  <div className="source-meta-info">
                    {source.confidence && (
                      <span className="relevance">
                        Match: {typeof source.confidence === 'number' ? (source.confidence * 100).toFixed(1) : source.confidence}%
                      </span>
                    )}
                    {source.relevance_score && (
                      <span className="relevance">
                        Match: {(source.relevance_score * 100).toFixed(1)}%
                      </span>
                    )}
                    {(source.version || source.metadata?.version) && (
                      <span className="version">v{source.version || source.metadata.version}</span>
                    )}
                  </div>
                  {source.chunk && (
                    <button
                      className="copy-btn"
                      onClick={() => handleCopy(source.chunk, `source-${idx}`)}
                      title="Copy to clipboard"
                    >
                      {copiedId === `source-${idx}` ? (
                        <>
                          <FiCheck size={16} /> Copied
                        </>
                      ) : (
                        <>
                          <FiCopy size={16} /> Copy
                        </>
                      )}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {message.status === 'RAG_NOT_IMPLEMENTED' && (
          <div className="status-section warning">
            <span className="status-icon">⚠️</span>
            <span className="status-message">{message.message}</span>
          </div>
        )}

        {message.confidence !== null && message.confidence !== undefined && (
          <div className="confidence-section">
            <span className="confidence-label">Confidence Score:</span>
            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{
                  width: `${message.confidence * 100}%`,
                  backgroundColor:
                    message.confidence > 0.8
                      ? '#4ade80'
                      : message.confidence > 0.5
                      ? '#eab308'
                      : '#ef4444',
                }}
              />
            </div>
            <span className="confidence-value">{(message.confidence * 100).toFixed(0)}%</span>
          </div>
        )}
      </div>

      <div className="message-footer">
        <span className="timestamp">{message.timestamp}</span>
        <div className="feedback-buttons">
          <button
            className={`feedback-btn ${feedbackGiven === true ? 'active' : ''}`}
            onClick={() => handleFeedback(true)}
            title="Mark as helpful"
          >
            <FiThumbsUp size={18} />
          </button>
          <button
            className={`feedback-btn ${feedbackGiven === false ? 'active' : ''}`}
            onClick={() => handleFeedback(false)}
            title="Mark as not helpful"
          >
            <FiThumbsDown size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;
