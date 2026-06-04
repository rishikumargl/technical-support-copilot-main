import React, { useState, useEffect } from 'react';
import { FiUpload, FiTrash2, FiLoader, FiX, FiFileText } from 'react-icons/fi';
import { getDocuments, uploadDocument, deleteDocument, getDocumentChunks } from '../api/ragApi';
import toastManager from '../utils/toastManager';
import './DocumentManager.css';

function DocumentManager() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [metadata, setMetadata] = useState({
    department: '',
    category: '',
    version: '1.0',
  });
  const [viewingChunks, setViewingChunks] = useState(null);
  const [chunksLoading, setChunksLoading] = useState(false);

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

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    try {
      await uploadDocument(selectedFile, metadata);
      setSelectedFile(null);
      setMetadata({ department: '', category: '', version: '1.0' });
      await fetchDocuments();
      toastManager.success(`${selectedFile.name} uploaded successfully`);
    } catch (error) {
      console.error('Upload error:', error);
      toastManager.error(`Failed to upload document: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(docId);
        await fetchDocuments();
        toastManager.success('Document deleted successfully');
      } catch (error) {
        console.error('Delete error:', error);
        toastManager.error(`Failed to delete document: ${error.message}`);
      }
    }
  };

  const handleViewChunks = async (doc) => {
    setViewingChunks(doc);
    setChunksLoading(true);
    try {
      const data = await getDocumentChunks(doc.id);
      setViewingChunks({ ...doc, chunks: data.chunks || [] });
      toastManager.info(`Loaded ${(data.chunks || []).length} chunks`);
    } catch (error) {
      console.error('Error fetching chunks:', error);
      setViewingChunks({ ...doc, chunks: [], error: 'Failed to load chunks' });
      toastManager.error('Failed to load document chunks');
    } finally {
      setChunksLoading(false);
    }
  };

  const closeModal = () => {
    setViewingChunks(null);
  };

  return (
    <div className="document-manager">
      <div className="manager-header">
        <h2>Document Management</h2>
        <p>Upload and manage knowledge base documents</p>
      </div>

      <div className="upload-section">
        <form onSubmit={handleUpload} className="upload-form">
          <div className="form-group">
            <label>Upload Document</label>
            <input
              type="file"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              accept=".pdf,.txt,.docx"
              disabled={uploading}
              className="file-input"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Department</label>
              <select
                value={metadata.department}
                onChange={(e) =>
                  setMetadata({ ...metadata, department: e.target.value })
                }
                disabled={uploading}
              >
                <option value="">Select Department</option>
                <option value="engineering">Engineering</option>
                <option value="support">Support</option>
                <option value="operations">Operations</option>
                <option value="hr">Human Resources</option>
              </select>
            </div>

            <div className="form-group">
              <label>Category</label>
              <input
                type="text"
                placeholder="e.g., Troubleshooting, FAQ, Release Notes"
                value={metadata.category}
                onChange={(e) =>
                  setMetadata({ ...metadata, category: e.target.value })
                }
                disabled={uploading}
              />
            </div>

            <div className="form-group">
              <label>Version</label>
              <input
                type="text"
                placeholder="e.g., 1.0"
                value={metadata.version}
                onChange={(e) =>
                  setMetadata({ ...metadata, version: e.target.value })
                }
                disabled={uploading}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={!selectedFile || uploading}
            className="upload-btn"
          >
            {uploading ? (
              <>
                <FiLoader className="spin" size={20} />
                Uploading...
              </>
            ) : (
              <>
                <FiUpload size={20} />
                Upload Document
              </>
            )}
          </button>
        </form>
      </div>

      <div className="documents-section">
        <h3>Knowledge Base Documents</h3>
        {loading ? (
          <div className="loading">
            <FiLoader className="spin" size={24} />
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <p>No documents uploaded yet</p>
            <p>Upload your first document to get started</p>
          </div>
        ) : (
          <div className="documents-grid">
            {documents.map((doc) => (
              <div key={doc.id} className="document-card">
                <div className="doc-header">
                  <h4>{doc.name}</h4>
                  {doc.metadata && (
                    <div className="doc-meta">
                      {doc.metadata.department && (
                        <span className="badge department">
                          {doc.metadata.department}
                        </span>
                      )}
                      {doc.metadata.version && (
                        <span className="badge version">v{doc.metadata.version}</span>
                      )}
                    </div>
                  )}
                </div>

                {doc.metadata?.category && (
                  <p className="doc-category">{doc.metadata.category}</p>
                )}

                <div className="doc-stats">
                  <span>📄 {doc.chunk_count || 0} chunks</span>
                  <span>📊 {((doc.size || 0) / 1024).toFixed(1)} KB</span>
                </div>

                <div className="doc-actions">
                  <button
                    className="action-btn chunks-btn"
                    onClick={() => handleViewChunks(doc)}
                    title="View document chunks"
                  >
                    <FiFileText size={18} />
                    View Chunks
                  </button>
                  <button
                    className="action-btn delete-btn"
                    onClick={() => handleDelete(doc.id)}
                  >
                    <FiTrash2 size={18} />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Chunks Modal */}
      {viewingChunks && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content chunks-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Document Chunks - {viewingChunks.name}</h3>
              <button className="close-btn" onClick={closeModal}>
                <FiX size={24} />
              </button>
            </div>
            <div className="modal-body chunks-body">
              {chunksLoading ? (
                <div className="chunks-loading">
                  <FiLoader className="spin" size={24} />
                  <p>Loading chunks...</p>
                </div>
              ) : viewingChunks.error ? (
                <div className="chunks-error">
                  <p>{viewingChunks.error}</p>
                </div>
              ) : viewingChunks.chunks && viewingChunks.chunks.length > 0 ? (
                <div className="chunks-list">
                  {viewingChunks.chunks.map((chunk, idx) => (
                    <div key={chunk.chunk_id || idx} className="chunk-item">
                      <div className="chunk-header">
                        <span className="chunk-number">Chunk {chunk.position + 1}</span>
                        {chunk.embedding && (
                          <span className="chunk-badge">Has Embedding</span>
                        )}
                      </div>
                      <p className="chunk-content">{chunk.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="chunks-empty">
                  <p>No chunks found for this document</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentManager;
