function sanitizeString(str) {
  if (typeof str !== 'string') return '';
  return str.trim().slice(0, 10000);
}

function sanitizePayload(payload) {
  return {
    query: sanitizeString(payload.query || ''),
    filters: {
      department: sanitizeString(payload.filters?.department || ''),
      category: sanitizeString(payload.filters?.category || ''),
      documentType: sanitizeString(payload.filters?.documentType || ''),
    },
    collectionName: sanitizeString(payload.collectionName || 'technical_docs'),
  };
}

function validateChatPayload(payload) {
  const sanitized = sanitizePayload(payload);
  if (!sanitized.query) {
    return { valid: false, error: 'Query cannot be empty' };
  }
  return { valid: true, data: sanitized };
}

module.exports = {
  sanitizeString,
  sanitizePayload,
  validateChatPayload,
};
