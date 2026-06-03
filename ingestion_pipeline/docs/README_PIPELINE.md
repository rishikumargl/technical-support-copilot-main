# Document Ingestion Pipeline for Enterprise RAG

A production-ready Python-based document ingestion system that parses PDFs, extracts structured metadata, and applies configurable chunking strategies.

## Architecture

### Hour 1: Document Parsing (`document_parser.py`)
Extracts documents from a directory structure and parses PDF content with metadata extraction:
- **Input**: Directory of PDF files organized by department
- **Schema Validation**: Enforces department and category standards
- **Metadata Extraction**: Parses file paths and headers
- **Output**: List of documents with extracted text and metadata

### Hour 2-3: Chunking Strategies (`chunking_strategies.py`)
Two distinct chunking approaches for text splitting:

#### Fixed-Size Chunking
- **Chunk Size**: 500 characters (configurable)
- **Overlap**: 50 characters (configurable)
- **Use Case**: Consistent chunk sizes, predictable retrieval
- **Output**: UUID-identified chunks with position tracking

#### Semantic Chunking
- **Sentence-Based**: Respects logical boundaries
- **Structural Awareness**: Recognizes page breaks and section headers
- **Target Size**: 500 characters (adaptive)
- **Use Case**: Maintains semantic coherence, better context preservation

## Schema

### Document Schema
```json
{
  "document_name": "string",
  "department": "string (Engineering|HR|Operations|Support)",
  "category": "string (Policy|Ticket|Guide)",
  "version": "string (e.g., '1.0')",
  "text_content": "string (raw extracted text)"
}
```

### Chunk Schema
```json
{
  "chunk_id": "string (UUID)",
  "document_name": "string",
  "department": "string",
  "category": "string",
  "version": "string",
  "strategy": "string (fixed_size|semantic)",
  "text": "string",
  "start_pos": "integer",
  "end_pos": "integer",
  "size": "integer (character count)"
}
```

## Installation

```bash
pip install -r requirements.txt
```

### Dependencies
- `pypdf>=4.0.0` - PDF parsing
- `sentence-transformers>=2.2.0` - Semantic embeddings (optional, for semantic chunking)
- `numpy` - Numerical operations

## Usage

### Basic Usage: Full Pipeline

```python
from ingestion_pipeline import IngestionPipeline

# Run with fixed-size chunking
pipeline = IngestionPipeline(
    source_dir="data",
    output_dir="output",
    chunking_strategy="fixed"
)
result = pipeline.run()
print(result)
```

### Switch Between Strategies

```python
# Using semantic chunking instead
pipeline = IngestionPipeline(
    source_dir="data",
    output_dir="output",
    chunking_strategy="semantic"
)
result = pipeline.run()
```

### Custom Configuration

```python
from document_parser import DocumentParser
from chunking_strategies import FixedSizeChunking, ChunkingPipeline

# Custom parsing
parser = DocumentParser("data")
documents = parser.parse_directory()

# Custom chunking
chunker = FixedSizeChunking(chunk_size=1000, overlap=100)
chunks = chunker.chunk(text, "doc_name")

# Save output
pipeline = ChunkingPipeline(strategy="fixed")
pipeline.save_chunks_to_json(chunks, "output.json")
```

## Running the Pipeline

### Full Pipeline
```bash
python ingestion_pipeline.py fixed
python ingestion_pipeline.py semantic
```

### Individual Components
```bash
python document_parser.py
python chunking_strategies.py
```

### Run Tests
```bash
python -m pytest test_pipeline.py -v
# or
python test_pipeline.py
```

## Directory Structure

```
project/
├── data/                          # Input PDFs organized by department
│   ├── Engineering/
│   │   └── v1_setup_guide.pdf
│   ├── HR/
│   │   └── v2_remote_policy.pdf
│   ├── Operations/
│   └── Support/
├── output/                        # Generated chunks (JSON)
│   ├── ingestion_output_fixed.json
│   └── ingestion_output_semantic.json
├── document_parser.py             # Parsing logic
├── chunking_strategies.py         # Chunking implementations
├── ingestion_pipeline.py          # Main orchestration
├── test_pipeline.py               # Unit tests
└── requirements.txt               # Dependencies
```

## Output Format

### Complete Output JSON Structure
```json
{
  "pipeline_metadata": {
    "total_documents": 5,
    "total_chunks": 127,
    "chunking_strategy": "fixed",
    "avg_chunk_size": 487
  },
  "documents_summary": [
    {
      "document_name": "v1_setup_guide",
      "department": "Engineering",
      "category": "Guide",
      "version": "1.0",
      "chunk_count": 12
    }
  ],
  "chunks": [
    {
      "chunk_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p",
      "document_name": "v1_setup_guide",
      "department": "Engineering",
      "category": "Guide",
      "version": "1.0",
      "strategy": "fixed_size",
      "text": "Chapter 1: System Prerequisites...",
      "start_pos": 0,
      "end_pos": 500,
      "size": 500
    }
  ]
}
```

## Key Features

✅ **Robust Error Handling**: Gracefully handles corrupt PDFs, encoding issues
✅ **Modular Design**: Independent components for parsing and chunking
✅ **Configurable Strategies**: Easy switching between chunking approaches
✅ **UUID Tracking**: Every chunk has a unique identifier for traceability
✅ **Production-Ready**: Logging, validation, and comprehensive testing
✅ **JSON Output**: Database-ready structured format

## Performance Considerations

- **Fixed-Size**: Faster processing, suitable for large-scale pipelines
- **Semantic**: Better quality chunks, slower processing due to NLP overhead
- **Memory**: Process documents in batches for very large collections

## Extension Points

### Adding Custom Chunking Strategy
```python
from chunking_strategies import ChunkingStrategy

class CustomChunking(ChunkingStrategy):
    def chunk(self, text: str, document_name: str) -> List[Dict]:
        # Your implementation
        pass
```

### Custom Metadata Extraction
Override `_extract_metadata_from_path()` in DocumentParser for custom logic.

## Logging

All modules use Python's standard logging. Control verbosity:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Future Enhancements

- [ ] Multi-format support (DOCX, XLSX, TXT)
- [ ] Language-aware semantic chunking
- [ ] Caching for repeated document processing
- [ ] Streaming API for large file processing
- [ ] Database integration for chunk storage
