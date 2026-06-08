import React from 'react';
import './MetadataFilter.css';

const departments = ['Engineering', 'Support', 'Operations', 'Product'];
const categories = ['Troubleshooting', 'Configuration', 'FAQ', 'Release Notes'];
const documentTypes = ['Documentation', 'Guide', 'Tutorial', 'Error Reference'];

export function MetadataFilter({ filters, onFilterChange }) {
  return (
    <div className="filter-panel">
      <h3>Filter Results</h3>

      <div className="filter-group">
        <label>Department</label>
        <select
          value={filters.department}
          onChange={(e) => onFilterChange('department', e.target.value)}
        >
          <option value="">All Departments</option>
          {departments.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Category</label>
        <select
          value={filters.category}
          onChange={(e) => onFilterChange('category', e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Document Type</label>
        <select
          value={filters.documentType}
          onChange={(e) => onFilterChange('documentType', e.target.value)}
        >
          <option value="">All Types</option>
          {documentTypes.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
