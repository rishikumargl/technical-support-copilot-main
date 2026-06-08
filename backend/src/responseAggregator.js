function aggregateResponse(ragResult, query) {
  return {
    success: true,
    query,
    response: ragResult.response || '',
    sources: ragResult.sources || [],
    metadata: {
      scoreStatus: ragResult.status,
      similarityScore: ragResult.score,
      timestamp: new Date().toISOString(),
    },
  };
}

function errorResponse(error, query) {
  return {
    success: false,
    query,
    response: error.message || 'An unexpected error occurred',
    sources: [],
    metadata: {
      error: true,
      timestamp: new Date().toISOString(),
    },
  };
}

module.exports = {
  aggregateResponse,
  errorResponse,
};
