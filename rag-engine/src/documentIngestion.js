const { generateDenseEmbedding, generateSparseVector } = require('./embeddingService');
const { upsertPoint } = require('./qdrantClient');

function splitDocumentByStructure(text, documentName, maxChunkSize = 1000) {
  const chunks = [];
  const lines = text.split('\n');
  let currentChunk = '';

  lines.forEach((line) => {
    if ((currentChunk + line).length > maxChunkSize && currentChunk.length > 0) {
      chunks.push({
        text: currentChunk.trim(),
        documentName,
      });
      currentChunk = line;
    } else {
      currentChunk += (currentChunk ? '\n' : '') + line;
    }
  });

  if (currentChunk.trim()) {
    chunks.push({
      text: currentChunk.trim(),
      documentName,
    });
  }

  return chunks;
}

async function extractTextFromPDF(buffer) {
  try {
    // Simple fallback: treat PDF buffer as UTF-8 text (for demo purposes)
    // In production, use a proper PDF library
    return buffer.toString('utf-8');
  } catch (error) {
    console.error('PDF extraction error:', error.message);
    // Return a demo text if PDF parsing fails
    return 'Sample documentation content. This is a demo for testing the RAG system.';
  }
}

async function ingestDocument(buffer, documentName, collectionName, metadata = {}) {
  try {
    let text;

    if (documentName.endsWith('.pdf')) {
      text = await extractTextFromPDF(buffer);
    } else {
      text = buffer.toString('utf-8');
    }

    const chunks = splitDocumentByStructure(text, documentName);
    let pointId = 1;

    for (const chunk of chunks) {
      const denseVector = await generateDenseEmbedding(chunk.text);
      const sparseVectorFreqs = generateSparseVector(chunk.text);

      const point = {
        id: pointId++,
        vector: {
          dense: denseVector,
          sparse: {
            indices: Object.keys(sparseVectorFreqs).map((k) => k.charCodeAt(0)),
            values: Object.values(sparseVectorFreqs),
          },
        },
        payload: {
          text: chunk.text,
          documentName: chunk.documentName,
          metadata: {
            documentName: chunk.documentName,
            version: metadata.version || '1.0',
            category: metadata.category || 'General',
            department: metadata.department || 'Engineering',
            documentType: metadata.documentType || 'Documentation',
          },
        },
      };

      await upsertPoint(collectionName, point);
    }

    return {
      success: true,
      chunksIngested: chunks.length,
      documentName,
    };
  } catch (error) {
    console.error('Document ingestion error:', error.message);
    throw error;
  }
}

module.exports = {
  ingestDocument,
  extractTextFromPDF,
  splitDocumentByStructure,
};
