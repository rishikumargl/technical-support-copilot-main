import React, { useState } from 'react';
import { FiThumbsUp, FiThumbsDown, FiCopy, FiCheck } from 'react-icons/fi';
import { InlineMath, BlockMath } from 'react-katex';
import './ChatMessage.css';

// Parse content to extract and render LaTeX
function renderContentWithMath(content) {
  if (!content) return null;

  const parts = [];
  let lastIndex = 0;

  // Match both $$ (block) and $ (inline) delimiters
  const regex = /(\$\$[\s\S]*?\$\$)|(\$[^\$\n]+\$)/g;
  let match;

  while ((match = regex.exec(content)) !== null) {
    // Add text before the math
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        value: content.substring(lastIndex, match.index),
      });
    }

    // Determine if it's block or inline math
    if (match[1]) {
      // Block math ($$...$$)
      const formula = match[1].slice(2, -2);
      parts.push({
        type: 'block',
        value: formula,
      });
    } else {
      // Inline math ($...$)
      const formula = match[2].slice(1, -1);
      parts.push({
        type: 'inline',
        value: formula,
      });
    }

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < content.length) {
    parts.push({
      type: 'text',
      value: content.substring(lastIndex),
    });
  }

  return parts;
}

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
          {renderContentWithMath(message.content).map((part, idx) => {
            if (part.type === 'text') {
              return <span key={idx}>{part.value}</span>;
            } else if (part.type === 'inline') {
              return <InlineMath key={idx}>{part.value}</InlineMath>;
            } else if (part.type === 'block') {
              return <BlockMath key={idx}>{part.value}</BlockMath>;
            }
            return null;
          })}
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
