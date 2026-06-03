import React, { useState, useEffect } from 'react';
import { FiUpload, FiTrash2, FiLoader, FiEye } from 'react-icons/fi';
import { getDocuments, uploadDocument, deleteDocument } from '../api/ragApi';
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
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(docId);
        await fetchDocuments();
      } catch (error) {
        console.error('Delete error:', error);
      }
    }
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
                  <button className="action-btn view-btn">
                    <FiEye size={18} />
                    View
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
    </div>
  );
}

export default DocumentManager;
