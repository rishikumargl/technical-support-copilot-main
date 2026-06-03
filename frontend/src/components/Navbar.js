import React from 'react';
import { FiMenu, FiMoon, FiSun, FiLogOut } from 'react-icons/fi';
import './Navbar.css';

function Navbar({ onToggleSidebar, isDarkMode, onToggleDarkMode }) {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <button className="menu-btn" onClick={onToggleSidebar}>
          <FiMenu size={24} />
        </button>
        <div className="navbar-title">
          <h1>RAG Assistant</h1>
          <p>Enterprise Technical Support Copilot</p>
        </div>
      </div>
      <div className="navbar-right">
        <button
          className="theme-toggle"
          onClick={onToggleDarkMode}
          title={isDarkMode ? 'Light Mode' : 'Dark Mode'}
        >
          {isDarkMode ? <FiSun size={20} /> : <FiMoon size={20} />}
        </button>
        <button className="logout-btn">
          <FiLogOut size={20} />
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
