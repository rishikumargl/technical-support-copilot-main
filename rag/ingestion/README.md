# Ingestion Pipeline - Organized Package

Complete document ingestion and chunking system for Enterprise RAG applications.

## Quick Start

```bash
# 1. Install dependencies
pip install -r config/requirements.txt

# 2. Run examples
python examples/basic_usage.py

# 3. Run pipeline
python -c "from src.ingestion_pipeline import IngestionPipeline; p = IngestionPipeline('data', 'output', 'fixed'); p.run()"

# 4. Run tests
python -m pytest tests/test_pipeline.py -v
```

## Folder Structure

```
ingestion_pipeline/
├── __init__.py                    # Package initialization
├── INTEGRATION_GUIDE.md           # How to integrate
├── setup.py                       # Package setup
├── README.md                      # This file
│
├── src/                           # Core implementation
│   ├── document_parser.py         # Hour 1: Parsing
│   ├── chunking_strategies.py     # Hours 2-3: Chunking
│   └── ingestion_pipeline.py      # Full orchestration
│
├── tests/                         # Test suite
│   ├── test_pipeline.py           # 10 unit tests
│   └── verify_pipeline.py         # Output verification
│
├── docs/                          # Complete documentation
│   ├── README.md
│   ├── QUICK_START.md
│   ├── EXAMPLES.md
│   ├── README_PIPELINE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── PROJECT_FILES.md
│
├── config/                        # Configuration
│   └── requirements.txt
│
├── data/                          # Sample input documents
│   ├── Engineering/
│   └── HR/
│
├── output/                        # Generated output
│   ├── ingestion_output_fixed.json
│   └── ingestion_output_semantic.json
│
└── examples/                      # Usage examples
    └── basic_usage.py
```

## Features

✅ **Document Parsing** (Hour 1)
- PDF/text file support
- Metadata extraction from file paths
- Schema validation
- Error handling

✅ **Chunking Strategies** (Hours 2-3)
- Fixed-size chunking (500 chars, 50-char overlap)
- Semantic chunking (sentence-aware)
- UUID generation for every chunk
- Position tracking

✅ **Integration Ready**
- Single-file import
- Production-grade code
- Comprehensive documentation
- 10/10 tests passing

## Usage

### Option 1: Import as Package

```python
from ingestion_pipeline import IngestionPipeline

pipeline = IngestionPipeline("documents", "output", "fixed")
result = pipeline.run()
```

### Option 2: Use Components

```python
from ingestion_pipeline import DocumentParser, FixedSizeChunking

parser = DocumentParser("documents")
docs = parser.parse_directory()

chunker = FixedSizeChunking()
for doc in docs:
    chunks = chunker.chunk(doc["text_content"], doc["document_name"])
```

### Option 3: Run Examples

```bash
python examples/basic_usage.py
```

## Installation

### Standard Installation
```bash
pip install -r config/requirements.txt
```

### Editable Installation (for development)
```bash
pip install -e .
```

## Documentation

- **INTEGRATION_GUIDE.md** - How to integrate into your project
- **docs/QUICK_START.md** - 5-minute setup
- **docs/EXAMPLES.md** - 20+ code examples
- **docs/README_PIPELINE.md** - Technical reference

## Testing

```bash
# Run all tests
python tests/test_pipeline.py

# Run with pytest
python -m pytest tests/test_pipeline.py -v

# Verify outputs
python tests/verify_pipeline.py
```

## Integration Example

```python
from ingestion_pipeline import IngestionPipeline
import json

# Run pipeline
pipeline = IngestionPipeline("documents", "chunks", "fixed")
result = pipeline.run()

# Load JSON
with open(result['output_file']) as f:
    data = json.load(f)

# Use chunks
for chunk in data['chunks']:
    print(f"{chunk['chunk_id']}: {chunk['text'][:50]}...")
```

## Next Steps

1. Review INTEGRATION_GUIDE.md for integration options
2. Check examples/basic_usage.py for usage patterns
3. See docs/EXAMPLES.md for detailed examples
4. Read docs/README_PIPELINE.md for technical details

## Status

✅ Production-Ready
✅ 10/10 Tests Passing
✅ Complete Documentation

---

Ready to integrate! See INTEGRATION_GUIDE.md for next steps.
