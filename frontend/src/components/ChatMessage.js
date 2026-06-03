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
        <span className="model-badge">RAG Assistant</span>
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
                      {source.document_name}
                    </span>
                    {source.metadata && (
                      <span className="source-meta">
                        {source.metadata.department && (
                          <span className="meta-tag">{source.metadata.department}</span>
                        )}
                        {source.metadata.category && (
                          <span className="meta-tag">{source.metadata.category}</span>
                        )}
                      </span>
                    )}
                  </div>
                  <p className="source-content">{source.chunk}</p>
                  <div className="source-meta-info">
                    <span className="relevance">
                      Match: {(source.relevance_score * 100).toFixed(1)}%
                    </span>
                    {source.metadata?.version && (
                      <span className="version">v{source.metadata.version}</span>
                    )}
                  </div>
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
                </div>
              ))}
            </div>
          </div>
        )}

        {message.confidence && (
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
