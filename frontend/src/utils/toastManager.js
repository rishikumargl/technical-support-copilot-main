/**
 * Toast Manager - Global toast notification system
 * Manages toast notifications for API success/failure feedback
 */

let toastListeners = [];
let toastId = 0;

export const toastManager = {
  subscribe(listener) {
    toastListeners.push(listener);
    return () => {
      toastListeners = toastListeners.filter(l => l !== listener);
    };
  },

  notify(message, type = 'info', duration = 3000) {
    const id = toastId++;
    const toast = { id, message, type, duration };

    toastListeners.forEach(listener => listener('ADD_TOAST', toast));

    if (duration > 0) {
      setTimeout(() => {
        toastListeners.forEach(listener => listener('REMOVE_TOAST', id));
      }, duration);
    }

    return id;
  },

  success(message, duration = 3000) {
    return this.notify(message, 'success', duration);
  },

  error(message, duration = 4000) {
    return this.notify(message, 'error', duration);
  },

  warning(message, duration = 3500) {
    return this.notify(message, 'warning', duration);
  },

  info(message, duration = 3000) {
    return this.notify(message, 'info', duration);
  },

  remove(id) {
    toastListeners.forEach(listener => listener('REMOVE_TOAST', id));
  },

  clear() {
    toastListeners.forEach(listener => listener('CLEAR_ALL'));
  }
};

export default toastManager;
