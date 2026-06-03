# Document Ingestion Pipeline - Usage Examples

## Quick Start

### 1. Running the Complete Pipeline

```bash
# Process with fixed-size chunking
python ingestion_pipeline.py fixed

# Process with semantic chunking
python ingestion_pipeline.py semantic
```

### 2. Using Individual Components

```python
from document_parser import DocumentParser
from chunking_strategies import FixedSizeChunking, ChunkingPipeline

# Step 1: Parse documents
parser = DocumentParser("data")
documents = parser.parse_directory()

# Step 2: Choose chunking strategy
pipeline = ChunkingPipeline(strategy="fixed")

# Step 3: Process documents
chunks = pipeline.process_documents(documents)

# Step 4: Save to JSON
pipeline.save_chunks_to_json(chunks, "output.json")
```

## Hour 1: Document Parsing Examples

### Basic Document Parsing

```python
from document_parser import DocumentParser

parser = DocumentParser("data")
documents = parser.parse_directory()

for doc in documents:
    print(f"Document: {doc['document_name']}")
    print(f"Department: {doc['department']}")
    print(f"Category: {doc['category']}")
    print(f"Version: {doc['version']}")
    print(f"Text Length: {len(doc['text_content'])} characters")
    print("---")
```

### Custom Document Parsing

```python
from document_parser import DocumentParser
from pathlib import Path

parser = DocumentParser("data")

# Parse a specific file
pdf_path = Path("data/Engineering/setup.pdf")
doc = parser._parse_pdf(pdf_path)

# Access extracted metadata
print(f"Name: {doc['document_name']}")
print(f"Dept: {doc['department']}")
```

## Hour 2-3: Chunking Strategy Examples

### Fixed-Size Chunking

```python
from chunking_strategies import FixedSizeChunking

# Create chunker with custom configuration
chunker = FixedSizeChunking(
    chunk_size=1000,    # 1000 characters per chunk
    overlap=100         # 100 character overlap between chunks
)

text = "Your document text here..."
chunks = chunker.chunk(text, "document_name")

# Each chunk includes:
# - chunk_id: Unique UUID
# - text: The chunk content
# - start_pos, end_pos: Position in original text
# - size: Character count
for chunk in chunks:
    print(f"Chunk {chunk['chunk_id']}: {chunk['size']} chars")
```

### Semantic Chunking

```python
from chunking_strategies import SemanticChunking

# Create semantic chunker
chunker = SemanticChunking(
    model_name="all-MiniLM-L6-v2",  # Transformer model
    target_size=500                  # Target chunk size
)

text = """
Chapter 1: Introduction

This is an important paragraph about system setup.
It spans multiple sentences and provides context.

--- Page 2 ---

Chapter 2: Installation

Follow these steps to install the system.
"""

chunks = chunker.chunk(text, "guide")

# Semantic chunks respect sentence and section boundaries
for chunk in chunks:
    print(f"Semantic chunk: {chunk['text'][:100]}...")
```

### Comparing Both Strategies

```python
from chunking_strategies import FixedSizeChunking, SemanticChunking

document_text = """
Engineering Setup Guide v1.0
=============================

This document covers the complete setup procedure for our engineering infrastructure.

Chapter 1: System Prerequisites

Before beginning, ensure your machine meets the following requirements:
- Python 3.8 or higher
- PostgreSQL 12.0 or higher
- Node.js 16.0 or higher
- At least 8GB RAM
- 50GB free disk space
"""

# Fixed-size chunking
fixed_chunker = FixedSizeChunking(chunk_size=500, overlap=50)
fixed_chunks = fixed_chunker.chunk(document_text, "setup_guide")

# Semantic chunking
semantic_chunker = SemanticChunking(target_size=500)
semantic_chunks = semantic_chunker.chunk(document_text, "setup_guide")

print(f"Fixed-size chunks: {len(fixed_chunks)}")
print(f"Semantic chunks: {len(semantic_chunks)}")

# Fixed-size may split mid-sentence
print("\nFixed-size chunk 1:")
print(fixed_chunks[0]['text'][:100] + "...")

# Semantic respects boundaries
print("\nSemantic chunk 1:")
print(semantic_chunks[0]['text'][:100] + "...")
```

## Complete Pipeline Examples

### Example 1: Basic Pipeline Execution

```python
from ingestion_pipeline import IngestionPipeline

# Create pipeline
pipeline = IngestionPipeline(
    source_dir="data",
    output_dir="output",
    chunking_strategy="fixed"
)

# Run pipeline
result = pipeline.run()

print(f"Status: {result['status']}")
print(f"Documents: {result['documents']}")
print(f"Chunks: {result['chunks']}")
print(f"Output: {result['output_file']}")
```

### Example 2: Processing Multiple Departments

```python
from ingestion_pipeline import IngestionPipeline
import json

for dept in ["Engineering", "HR", "Operations", "Support"]:
    print(f"\nProcessing {dept} documents...")
    
    pipeline = IngestionPipeline(
        source_dir=f"data/{dept}",
        output_dir="output",
        chunking_strategy="fixed"
    )
    
    result = pipeline.run()
    
    with open(result['output_file']) as f:
        data = json.load(f)
        print(f"  Total chunks: {data['pipeline_metadata']['total_chunks']}")
```

### Example 3: Batch Processing with Strategy Comparison

```python
from ingestion_pipeline import IngestionPipeline
import json

strategies = ["fixed", "semantic"]

for strategy in strategies:
    print(f"\nProcessing with {strategy} strategy...")
    
    pipeline = IngestionPipeline(
        source_dir="data",
        output_dir="output",
        chunking_strategy=strategy
    )
    
    result = pipeline.run()
    
    # Load and analyze output
    with open(result['output_file']) as f:
        data = json.load(f)
        metadata = data['pipeline_metadata']
        
        print(f"  Total chunks: {metadata['total_chunks']}")
        print(f"  Avg chunk size: {metadata['avg_chunk_size']} chars")
```

## Advanced Usage Patterns

### Pattern 1: Custom Metadata Extraction

```python
from document_parser import DocumentParser
from pathlib import Path

class CustomDocumentParser(DocumentParser):
    def _extract_metadata_from_path(self, pdf_path: Path):
        metadata = super()._extract_metadata_from_path(pdf_path)
        
        # Add custom fields
        metadata["source"] = "enterprise_system"
        metadata["indexed_date"] = "2024-06-03"
        
        return metadata

parser = CustomDocumentParser("data")
documents = parser.parse_directory()
```

### Pattern 2: Filtering Chunks

```python
from ingestion_pipeline import IngestionPipeline
import json

pipeline = IngestionPipeline("data", chunking_strategy="fixed")
result = pipeline.run()

with open(result['output_file']) as f:
    data = json.load(f)
    
    # Get only Engineering chunks
    engineering_chunks = [
        c for c in data['chunks'] 
        if c['department'] == 'Engineering'
    ]
    
    print(f"Engineering chunks: {len(engineering_chunks)}")
```

### Pattern 3: Quality Assessment

```python
from ingestion_pipeline import IngestionPipeline
import json

pipeline = IngestionPipeline("data", chunking_strategy="fixed")
result = pipeline.run()

with open(result['output_file']) as f:
    data = json.load(f)
    chunks = data['chunks']
    
    # Analyze chunk distribution
    sizes = [c['size'] for c in chunks]
    
    print(f"Min size: {min(sizes)} chars")
    print(f"Max size: {max(sizes)} chars")
    print(f"Avg size: {sum(sizes) // len(sizes)} chars")
    
    # Find small chunks
    small_chunks = [c for c in chunks if c['size'] < 100]
    print(f"Small chunks (< 100 chars): {len(small_chunks)}")
```

## Data Flow Diagram

```
Input Documents (PDF/TXT)
         ↓
    Document Parser
         ↓
  Parsed Documents
  (with metadata)
         ↓
    Choose Strategy
         ↓
  ┌─────┴─────┐
  ↓           ↓
Fixed-Size  Semantic
Chunking    Chunking
  ↓           ↓
  └─────┬─────┘
        ↓
   Chunk Objects
   (with UUIDs)
        ↓
  JSON Output
        ↓
Database Ready
```

## Output JSON Structure

```json
{
  "pipeline_metadata": {
    "total_documents": 10,
    "total_chunks": 247,
    "chunking_strategy": "fixed",
    "avg_chunk_size": 485
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
      "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
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

## Performance Tips

1. **Fixed-size chunking** for large-scale ingestion (faster)
2. **Semantic chunking** for high-quality retrieval (slower)
3. Process documents in batches for very large datasets
4. Use appropriate chunk sizes based on downstream tasks:
   - Retrieval: 400-600 chars
   - Summarization: 1000+ chars
   - Classification: 200-400 chars

## Testing

```bash
# Run unit tests
python test_pipeline.py

# Test with specific strategy
python ingestion_pipeline.py fixed
python ingestion_pipeline.py semantic

# Check output
python -m json.tool output/ingestion_output_fixed.json | head -50
```

## Troubleshooting

### Issue: No documents found
**Solution**: Ensure PDFs are in the correct directory structure and named appropriately

### Issue: Text extraction is empty
**Solution**: Check if PDFs are readable and not encrypted. Use text files for testing.

### Issue: Memory error with large files
**Solution**: Process documents in smaller batches or increase available RAM

### Issue: Semantic chunking is slow
**Solution**: First run downloads the model (~150MB). Subsequent runs are faster. Consider fixed-size chunking for speed.
