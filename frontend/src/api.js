const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

export async function sendChatQuery(query, filters = {}) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      filters,
      collectionName: 'technical_docs',
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function ingestDocument(file, metadata = {}) {
  const buffer = await file.arrayBuffer();
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));

  const response = await fetch(`${API_URL}/api/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      documentName: file.name,
      fileContent: base64,
      metadata,
    }),
  });

  if (!response.ok) {
    throw new Error(`Ingest error: ${response.statusText}`);
  }

  return response.json();
}

export async function checkHealth() {
  try {
    const response = await fetch(`${API_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
}
