import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FiMessageSquare,
  FiFileText,
  FiBarChart2,
  FiSettings,
  FiGithub,
  FiExternalLink,
} from 'react-icons/fi';
import './Sidebar.css';

function Sidebar({ isOpen }) {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Chat', icon: FiMessageSquare },
    { path: '/documents', label: 'Documents', icon: FiFileText },
    { path: '/analytics', label: 'Analytics', icon: FiBarChart2 },
    { path: '/config', label: 'Configuration', icon: FiSettings },
  ];

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-content">
        <div className="nav-section">
          <h3>Navigation</h3>
          <nav className="nav-menu">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-item ${isActive ? 'active' : ''}`}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="nav-section docs">
          <h3>Resources</h3>
          <a
            href="https://github.com/rishikumargl/technical-support-copilot-main/blob/frontend/frontend/README.md"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-item external"
          >
            <FiFileText size={20} />
            <span>API Documentation</span>
            <FiExternalLink size={16} />
          </a>
          <a
            href="https://github.com/rishikumargl/technical-support-copilot-main/"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-item external"
          >
            <FiGithub size={20} />
            <span>GitHub Repository</span>
            <FiExternalLink size={16} />
          </a>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="version-info">
          <p>RAG Assistant v1.0.0</p>
          <p className="status">Ready</p>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
