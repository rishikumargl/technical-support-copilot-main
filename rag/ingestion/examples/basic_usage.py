#!/usr/bin/env python3
"""
Basic usage examples for the ingestion pipeline.

Shows how to integrate the pipeline into your project.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion_pipeline import IngestionPipeline
from src.document_parser import DocumentParser
from src.chunking_strategies import FixedSizeChunking, SemanticChunking


def example_1_basic_pipeline():
    """Example 1: Run complete pipeline with fixed-size chunking."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Pipeline")
    print("="*70)

    pipeline = IngestionPipeline(
        source_dir="data",
        output_dir="output",
        chunking_strategy="fixed"
    )

    result = pipeline.run()

    print(f"\nResult:")
    print(f"  Status: {result['status']}")
    print(f"  Documents: {result['documents']}")
    print(f"  Chunks: {result['chunks']}")
    print(f"  Output: {result['output_file']}")


def example_2_semantic_chunking():
    """Example 2: Use semantic chunking strategy."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Semantic Chunking")
    print("="*70)

    pipeline = IngestionPipeline(
        source_dir="data",
        output_dir="output",
        chunking_strategy="semantic"
    )

    result = pipeline.run()

    print(f"\nSemantic chunking result:")
    print(f"  Chunks created: {result['chunks']}")


def example_3_step_by_step():
    """Example 3: Step-by-step processing."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Step-by-Step Processing")
    print("="*70)

    # Step 1: Parse documents
    print("\nStep 1: Parsing documents...")
    parser = DocumentParser("data")
    documents = parser.parse_directory()
    print(f"  Parsed {len(documents)} documents")

    # Step 2: View parsed documents
    print("\nStep 2: Viewing parsed documents...")
    for doc in documents[:2]:
        print(f"  - {doc['document_name']} ({doc['department']})")

    # Step 3: Apply chunking
    print("\nStep 3: Applying chunking strategy...")
    chunker = FixedSizeChunking(chunk_size=500, overlap=50)
    for doc in documents:
        chunks = chunker.chunk(doc["text_content"], doc["document_name"])
        print(f"  - {doc['document_name']}: {len(chunks)} chunks")


def example_4_custom_configuration():
    """Example 4: Custom chunking configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Configuration")
    print("="*70)

    # Custom fixed-size chunking
    print("\nCustom fixed-size chunking (1000 chars, 200 overlap):")
    chunker = FixedSizeChunking(chunk_size=1000, overlap=200)

    parser = DocumentParser("data")
    documents = parser.parse_directory()

    if documents:
        doc = documents[0]
        chunks = chunker.chunk(doc["text_content"], doc["document_name"])
        print(f"  Document: {doc['document_name']}")
        print(f"  Chunks: {len(chunks)}")
        if chunks:
            print(f"  Chunk size range: {min(c['size'] for c in chunks)}-{max(c['size'] for c in chunks)} chars")


def example_5_strategy_comparison():
    """Example 5: Compare both strategies."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Strategy Comparison")
    print("="*70)

    parser = DocumentParser("data")
    documents = parser.parse_directory()

    if not documents:
        print("No documents found in data folder")
        return

    doc = documents[0]
    text = doc["text_content"]

    # Fixed-size
    print(f"\nProcessing: {doc['document_name']}")
    fixed_chunker = FixedSizeChunking(chunk_size=500, overlap=50)
    fixed_chunks = fixed_chunker.chunk(text, doc["document_name"])

    # Semantic
    semantic_chunker = SemanticChunking(target_size=500)
    semantic_chunks = semantic_chunker.chunk(text, doc["document_name"])

    print(f"\nComparison:")
    print(f"  Strategy          | Chunks | Avg Size | Min Size | Max Size")
    print(f"  ─────────────────────────────────────────────────────────")

    fixed_sizes = [c["size"] for c in fixed_chunks]
    semantic_sizes = [c["size"] for c in semantic_chunks]

    print(f"  Fixed-size        | {len(fixed_chunks):6} | {sum(fixed_sizes)//len(fixed_sizes):8} | {min(fixed_sizes):8} | {max(fixed_sizes):8}")
    print(f"  Semantic          | {len(semantic_chunks):6} | {sum(semantic_sizes)//len(semantic_sizes):8} | {min(semantic_sizes):8} | {max(semantic_sizes):8}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("INGESTION PIPELINE - USAGE EXAMPLES")
    print("="*70)

    try:
        example_1_basic_pipeline()
    except Exception as e:
        print(f"Example 1 error: {e}")

    try:
        example_2_semantic_chunking()
    except Exception as e:
        print(f"Example 2 error: {e}")

    try:
        example_3_step_by_step()
    except Exception as e:
        print(f"Example 3 error: {e}")

    try:
        example_4_custom_configuration()
    except Exception as e:
        print(f"Example 4 error: {e}")

    try:
        example_5_strategy_comparison()
    except Exception as e:
        print(f"Example 5 error: {e}")

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
