import React from 'react';
import './CitationCard.css';

export function CitationCard({ source }) {
  return (
    <div className="citation-card">
      <div className="citation-header">
        <strong>{source.documentName || 'Unknown Document'}</strong>
        <span className="citation-version">v{source.version || 'N/A'}</span>
      </div>
      <div className="citation-score">Confidence: {(source.score * 100).toFixed(1)}%</div>
    </div>
  );
}
