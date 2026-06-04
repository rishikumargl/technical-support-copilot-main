# Enterprise RAG Document Ingestion Pipeline

A production-ready Python system for parsing documents, extracting structured metadata, and applying configurable chunking strategies for Retrieval-Augmented Generation (RAG) systems.

## Overview

This implementation covers a complete document ingestion pipeline with three hours of work:

- **Hour 1**: Document parsing with schema matching and metadata extraction
- **Hours 2-3**: Two distinct chunking strategies with configurable parameters

## Features

✅ **Document Parsing**
- Extracts content from PDF and text files
- Validates metadata (department, category, version)
- Robust error handling for corrupted files

✅ **Two Chunking Strategies**
- Fixed-Size: 500-char chunks with configurable overlap (faster)
- Semantic: Sentence-aware, respects boundaries (better quality)

✅ **Schema Compliance**
- Validates against allowed departments and categories
- Generates unique UUIDs for every chunk
- Enriches chunks with document metadata
- Position tracking (start_pos, end_pos)

✅ **Production Ready**
- Comprehensive unit tests (10/10 passing)
- Complete logging and error handling
- JSON output ready for database ingestion
- Extensive documentation with examples

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline (generates sample data)
python ingestion_pipeline.py fixed      # Fixed-size chunking
python ingestion_pipeline.py semantic   # Semantic chunking

# Run tests
python test_pipeline.py

# Check output
ls output/
```

## Core Components

| File | Purpose |
|------|---------|
| `document_parser.py` | PDF/text parsing & metadata extraction |
| `chunking_strategies.py` | Fixed-size & semantic chunking |
| `ingestion_pipeline.py` | Full pipeline orchestration |
| `test_pipeline.py` | 10 comprehensive unit tests |

## Verification Results

```
✓ Documents parsed: 2
✓ Total chunks created: 6
✓ Schema validation: PASS
✓ UUID generation: PASS
✓ Metadata enrichment: PASS
✓ Unit tests: 10/10 PASS
✓ JSON output: Valid and complete
```

## Documentation

- **QUICK_START.md** - 5-minute setup
- **README_PIPELINE.md** - Technical reference
- **EXAMPLES.md** - 20+ code examples
- **IMPLEMENTATION_SUMMARY.md** - Architecture details

## Status

✅ Complete and Production-Ready
