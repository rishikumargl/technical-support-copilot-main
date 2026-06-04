import React, { useState, useEffect } from 'react';
import { FiCheckCircle, FiAlertCircle, FiAlertTriangle, FiInfo, FiX } from 'react-icons/fi';
import toastManager from '../utils/toastManager';
import './Toast.css';

function Toast() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const unsubscribe = toastManager.subscribe((action, payload) => {
      if (action === 'ADD_TOAST') {
        setToasts(prev => [...prev, payload]);
      } else if (action === 'REMOVE_TOAST') {
        setToasts(prev => prev.filter(toast => toast.id !== payload));
      } else if (action === 'CLEAR_ALL') {
        setToasts([]);
      }
    });

    return unsubscribe;
  }, []);

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <FiCheckCircle size={20} />;
      case 'error':
        return <FiAlertCircle size={20} />;
      case 'warning':
        return <FiAlertTriangle size={20} />;
      case 'info':
        return <FiInfo size={20} />;
      default:
        return <FiInfo size={20} />;
    }
  };

  const removeToast = (id) => {
    toastManager.remove(id);
  };

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast toast-${toast.type}`}>
          <div className="toast-icon">{getIcon(toast.type)}</div>
          <div className="toast-message">{toast.message}</div>
          <button
            className="toast-close"
            onClick={() => removeToast(toast.id)}
            title="Close"
          >
            <FiX size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}

export default Toast;
