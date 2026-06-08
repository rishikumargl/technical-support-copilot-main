import { useState, useCallback } from 'react';

export function useStore() {
  const [messages, setMessages] = useState([]);
  const [filters, setFilters] = useState({
    department: '',
    category: '',
    documentType: '',
  });
  const [loading, setLoading] = useState(false);

  const addMessage = useCallback((role, content, sources = []) => {
    setMessages((prev) => [...prev, { role, content, sources, timestamp: new Date() }]);
  }, []);

  const updateFilters = useCallback((newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    addMessage,
    filters,
    updateFilters,
    loading,
    setLoading,
    clearMessages,
  };
}
