#!/usr/bin/env python3
"""
Complete document ingestion pipeline for Enterprise RAG system.

Hour 1: Parses documents from a directory and extracts metadata.
Hour 2-3: Applies configurable chunking strategies and outputs JSON.
"""

import json
import logging
from pathlib import Path
from typing import Literal

from document_parser import DocumentParser
from chunking_strategies import ChunkingPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Full document ingestion pipeline with parsing and chunking."""

    def __init__(
        self,
        source_dir: str,
        output_dir: str = "output",
        chunking_strategy: Literal["fixed", "semantic"] = "fixed",
    ):
        self.source_dir = source_dir
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.parser = DocumentParser(source_dir)
        self.chunking_pipeline = ChunkingPipeline(strategy=chunking_strategy)

        logger.info(f"IngestionPipeline initialized")
        logger.info(f"  Source directory: {source_dir}")
        logger.info(f"  Output directory: {output_dir}")
        logger.info(f"  Chunking strategy: {chunking_strategy}")

    def run(self) -> dict:
        """Execute the full ingestion pipeline."""
        logger.info("="*60)
        logger.info("STARTING DOCUMENT INGESTION PIPELINE")
        logger.info("="*60)

        logger.info("\n[Step 1/3] Parsing documents from source directory...")
        documents = self.parser.parse_directory()
        logger.info(f"✓ Parsed {len(documents)} documents")

        if not documents:
            logger.warning("No documents found. Exiting.")
            return {"status": "no_documents", "documents": 0, "chunks": 0}

        logger.info("\n[Step 2/3] Applying chunking strategy...")
        chunks = self.chunking_pipeline.process_documents(documents)
        logger.info(f"✓ Created {len(chunks)} total chunks")

        logger.info("\n[Step 3/3] Saving output to JSON...")
        output_path = self._save_output(documents, chunks)
        logger.info(f"✓ Saved to {output_path}")

        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*60)

        return {
            "status": "success",
            "documents": len(documents),
            "chunks": len(chunks),
            "output_file": str(output_path),
        }

    def _save_output(self, documents: list, chunks: list) -> Path:
        """Save parsed documents and chunks to JSON file."""
        output_data = {
            "pipeline_metadata": {
                "total_documents": len(documents),
                "total_chunks": len(chunks),
                "chunking_strategy": self.chunking_pipeline.strategy_type,
                "avg_chunk_size": sum(c.get("size", 0) for c in chunks) // len(chunks) if chunks else 0,
            },
            "documents_summary": [
                {
                    "document_name": doc["document_name"],
                    "department": doc["department"],
                    "category": doc["category"],
                    "version": doc["version"],
                    "chunk_count": sum(1 for c in chunks if c["document_name"] == doc["document_name"]),
                }
                for doc in documents
            ],
            "chunks": chunks,
        }

        output_path = self.output_dir / f"ingestion_output_{self.chunking_pipeline.strategy_type}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        return output_path


def create_sample_data():
    """Create sample PDF files for testing (uses text files as placeholder)."""
    sample_dir = Path("data")
    sample_dir.mkdir(exist_ok=True)

    (sample_dir / "Engineering").mkdir(exist_ok=True)
    (sample_dir / "HR").mkdir(exist_ok=True)

    engineering_doc = """
    Engineering Setup Guide v1.0
    ============================

    This document covers the complete setup procedure for our engineering infrastructure.

    Chapter 1: System Prerequisites

    Before beginning, ensure your machine meets the following requirements:
    - Python 3.8 or higher
    - PostgreSQL 12.0 or higher
    - Node.js 16.0 or higher
    - At least 8GB RAM
    - 50GB free disk space

    All tools should be installed from their official sources. Package managers like
    apt, brew, or choco can be used for convenience on respective platforms.

    Chapter 2: Installation Steps

    Step 1: Clone the repository from GitHub
    Step 2: Install Python dependencies using pip
    Step 3: Initialize the database schema
    Step 4: Run the test suite to verify installation
    Step 5: Configure environment variables

    Each step must complete successfully before proceeding to the next.

    Chapter 3: Configuration

    Edit the .env file with your specific configuration. Key variables include:
    - DATABASE_URL: Connection string for PostgreSQL
    - API_KEY: Authentication token for external services
    - LOG_LEVEL: Verbosity of application logging

    After configuration, restart all services to apply changes.
    """

    hr_doc = """
    HR Policy Document - Remote Work Policy v2.0
    =============================================

    Effective Date: January 1, 2024
    Last Updated: June 2024

    Section 1: Overview

    This policy establishes guidelines for remote work arrangements within our organization.
    Employees may request remote work status through their direct manager and HR department.
    All remote workers must maintain the same productivity and communication standards as
    office-based employees.

    Section 2: Eligibility

    Not all positions are eligible for remote work. Positions requiring physical presence
    for security, equipment access, or client interaction may not qualify. Managers will
    evaluate each request on a case-by-case basis.

    Section 3: Work Hours and Availability

    Remote workers are expected to maintain standard business hours. Daily stand-ups and
    weekly team meetings are mandatory. Communication must occur via Slack, email, or
    scheduled video calls.

    Section 4: Equipment and Technology

    The company provides or reimburses for necessary equipment including laptop, monitor,
    keyboard, and mouse. Internet connectivity must support video conferencing and large
    file transfers. Backup internet (e.g., mobile hotspot) is recommended.
    """

    with open(sample_dir / "Engineering" / "v1_setup_guide.txt", 'w') as f:
        f.write(engineering_doc)

    with open(sample_dir / "HR" / "v2_remote_policy.txt", 'w') as f:
        f.write(hr_doc)

    logger.info("Sample data created in ./data directory")


def main():
    """Run the ingestion pipeline with both chunking strategies."""
    import sys

    create_sample_data()

    strategies = ["fixed", "semantic"]
    if len(sys.argv) > 1:
        strategies = [sys.argv[1]]

    for strategy in strategies:
        logger.info(f"\n\nProcessing with {strategy.upper()} strategy...")
        pipeline = IngestionPipeline(
            source_dir="data",
            output_dir="output",
            chunking_strategy=strategy,
        )
        result = pipeline.run()
        logger.info(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
