import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

try:
    from pypdf import PdfReader
except ImportError:
    print("pypdf not installed. Install with: pip install pypdf")
    raise

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse documents from a directory and extract metadata."""

    VALID_DEPARTMENTS = {"Engineering", "HR", "Operations", "Support"}
    VALID_CATEGORIES = {"Policy", "Ticket", "Guide"}

    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")

    def parse_directory(self) -> List[Dict]:
        """Parse all PDF files in the directory and return structured documents."""
        documents = []

        pdf_files = list(self.source_dir.rglob("*.pdf"))
        if not pdf_files:
            pdf_files = list(self.source_dir.rglob("*.txt"))

        logger.info(f"Found {len(pdf_files)} document files")

        for pdf_path in pdf_files:
            try:
                if pdf_path.suffix == '.pdf':
                    doc = self._parse_pdf(pdf_path)
                else:
                    doc = self._parse_text_file(pdf_path)
                if doc:
                    documents.append(doc)
                    logger.info(f"Successfully parsed: {pdf_path.name}")
            except Exception as e:
                logger.error(f"Failed to parse {pdf_path.name}: {str(e)}")

        return documents

    def _parse_text_file(self, file_path: Path) -> Optional[Dict]:
        """Parse a text file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            if not text_content.strip():
                logger.warning(f"No text content in {file_path.name}")
                return None

            metadata = self._extract_metadata_from_path(file_path)
            metadata["text_content"] = text_content

            return metadata
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {str(e)}")
            return None

    def _parse_pdf(self, pdf_path: Path) -> Optional[Dict]:
        """Parse a single PDF file and extract metadata and text."""
        try:
            reader = PdfReader(pdf_path)
            text_content = self._extract_text(reader)

            if not text_content.strip():
                logger.warning(f"No text content extracted from {pdf_path.name}")
                return None

            metadata = self._extract_metadata_from_path(pdf_path)
            metadata["text_content"] = text_content

            return metadata
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {str(e)}")
            return None

    def _extract_text(self, reader: PdfReader) -> str:
        """Extract text from all pages of a PDF."""
        text = []
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text.append(f"--- Page {page_num + 1} ---\n{page_text}")
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {str(e)}")

        return "\n".join(text)

    def _extract_metadata_from_path(self, pdf_path: Path) -> Dict:
        """Extract metadata from file path structure."""
        parts = pdf_path.parts

        department = self._extract_department(parts)
        category, version = self._extract_category_and_version(pdf_path.stem)

        document_name = pdf_path.stem

        return {
            "document_name": document_name,
            "department": department,
            "category": category,
            "version": version,
        }

    def _extract_department(self, path_parts: tuple) -> str:
        """Extract department from path, validate against allowed departments."""
        for part in path_parts:
            if part in self.VALID_DEPARTMENTS:
                return part
        return "Unknown"

    def _extract_category_and_version(self, filename: str) -> tuple:
        """Extract category and version from filename."""
        category = "Unknown"
        version = "1.0"

        filename_lower = filename.lower()

        for cat in self.VALID_CATEGORIES:
            if cat.lower() in filename_lower:
                category = cat
                break

        version_match = re.search(r'v(\d+(?:\.\d+)*)', filename_lower)
        if version_match:
            version = version_match.group(1)

        return category, version


def main():
    """Example usage."""
    parser = DocumentParser("data")
    documents = parser.parse_directory()

    logger.info(f"Parsed {len(documents)} documents total")
    for doc in documents[:3]:
        logger.info(f"Doc: {doc['document_name']} | Dept: {doc['department']} | Cat: {doc['category']}")


if __name__ == "__main__":
    main()
