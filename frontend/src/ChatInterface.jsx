import React, { useState, useRef, useEffect } from 'react';
import { sendChatQuery, ingestDocument, checkHealth } from './api';
import { MetadataFilter } from './MetadataFilter';
import { CitationCard } from './CitationCard';
import './ChatInterface.css';

export function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [filters, setFilters] = useState({
    department: '',
    category: '',
    documentType: '',
  });
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [health, setHealth] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const checkStatus = async () => {
      const ok = await checkHealth();
      setHealth(ok);
    };
    checkStatus();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading || !health) return;

    const userMessage = { role: 'user', content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const result = await sendChatQuery(inputValue, filters);
      const assistantMessage = {
        role: 'assistant',
        content: result.response,
        sources: result.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}`,
        sources: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files) return;

    for (const file of files) {
      try {
        setLoading(true);
        const result = await ingestDocument(file, {
          version: '1.0',
          department: 'Engineering',
          category: 'Documentation',
          documentType: 'Documentation',
        });
        const successMessage = {
          role: 'system',
          content: `Document "${file.name}" ingested successfully (${result.chunksIngested} chunks)`,
          sources: [],
        };
        setMessages((prev) => [...prev, successMessage]);
      } catch (error) {
        const errorMessage = {
          role: 'system',
          content: `Failed to ingest "${file.name}": ${error.message}`,
          sources: [],
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>Technical Support Copilot</h1>
        <div className="health-status">
          {health === true ? (
            <span className="status-ok">● Connected</span>
          ) : health === false ? (
            <span className="status-error">● Disconnected</span>
          ) : (
            <span className="status-loading">● Checking...</span>
          )}
        </div>
      </div>

      <div className="chat-container">
        <div className="sidebar">
          <MetadataFilter filters={filters} onFilterChange={handleFilterChange} />

          <div className="upload-section">
            <h3>Ingest Documents</h3>
            <label className="upload-button">
              <input
                type="file"
                multiple
                accept=".pdf,.txt,.md"
                onChange={handleFileUpload}
                disabled={loading}
              />
              Choose Files
            </label>
          </div>
        </div>

        <div className="main-chat">
          <div className="messages">
            {messages.length === 0 && (
              <div className="empty-state">
                <p>Welcome to Technical Support Copilot</p>
                <p>Upload documents or ask technical questions to get started</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role}`}>
                <div className="message-content">{msg.content}</div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="citations">
                    {msg.sources.map((source, sidx) => (
                      <CitationCard key={sidx} source={source} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="input-form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={health ? 'Ask a technical question...' : 'Service unavailable...'}
              disabled={loading || !health}
            />
            <button type="submit" disabled={loading || !health}>
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
