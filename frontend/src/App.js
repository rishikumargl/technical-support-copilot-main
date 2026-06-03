import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ChatInterface from './pages/ChatInterface';
import DocumentManager from './pages/DocumentManager';
import Analytics from './pages/Analytics';
import SystemConfig from './pages/SystemConfig';
import './App.css';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(true);

  return (
    <Router>
      <div className={`app ${isDarkMode ? 'dark' : 'light'}`}>
        <Navbar
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          isDarkMode={isDarkMode}
          onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
        />
        <div className="app-container">
          <Sidebar isOpen={isSidebarOpen} />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<ChatInterface />} />
              <Route path="/documents" element={<DocumentManager />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/config" element={<SystemConfig />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
