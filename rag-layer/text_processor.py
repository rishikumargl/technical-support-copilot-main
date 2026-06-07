"""
Text post-processor for RAG outputs.
Cleans, normalizes, and corrects grammatical issues in retrieved text.
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Disable regex warnings for complex patterns
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)


class TextProcessor:
    """Clean and normalize text output from RAG system."""

    def __init__(self):
        """Initialize text processor with grammar rules."""
        self.acronyms = {
            'llm': 'Large Language Model',
            'rag': 'Retrieval-Augmented Generation',
            'nlp': 'Natural Language Processing',
            'npl': 'Natural Language Processing',
        }

    def process_chunk(self, text: str) -> str:
        """Process single text chunk for grammar and formatting.

        Args:
            text: Raw text from retrieval

        Returns:
            Clean, grammatically correct text
        """
        if not text or not isinstance(text, str):
            return ""

        # Step 1: Fix whitespace issues
        text = self._fix_whitespace(text)

        # Step 2: Fix broken unicode/symbol issues
        text = self._fix_broken_symbols(text)

        # Step 3: Fix incomplete sentences at edges
        text = self._fix_sentence_boundaries(text)

        # Step 4: Fix spacing around punctuation
        text = self._fix_punctuation_spacing(text)

        # Step 5: Fix LaTeX/math formatting
        text = self._fix_math_formatting(text)

        # Step 6: Normalize common patterns
        text = self._normalize_patterns(text)

        # Step 7: Fix capitalization issues
        text = self._fix_capitalization(text)

        return text.strip()

    def _fix_whitespace(self, text: str) -> str:
        """Fix whitespace issues: multiple spaces, tabs, newlines."""
        # Replace multiple spaces with single space
        text = re.sub(r' {2,}', ' ', text)

        # Replace multiple newlines with single newline
        text = re.sub(r'\n{2,}', '\n', text)

        # Replace tabs with spaces
        text = re.sub(r'\t+', ' ', text)

        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text

    def _fix_broken_symbols(self, text: str) -> str:
        """Fix broken unicode and symbol rendering issues."""
        # Use simple string replacement instead of regex to avoid escape issues
        try:
            # Fix vector notation (broken unicode)
            text = text.replace('v⃗ v', '$\\vec{v}$')
            text = text.replace('v⃗', '$\\vec{v}$')
            text = text.replace('A⃗', '$\\vec{A}$')
            text = text.replace('B⃗', '$\\vec{B}$')

            # Fix symbols
            text = text.replace('∥', '|')
            text = text.replace('⋅', ' · ')

            # Fix arrows
            text = text.replace('→', '->')

            # Fix broken brackets
            text = text.replace('( . )', '(...)')
            text = text.replace('( .\n )', '(...)')

            # Fix double equals
            if '= =' in text:
                text = text.replace('= =', '=')

        except Exception as e:
            logger.warning(f"Symbol fixing error: {e}")

        return text

    def _fix_sentence_boundaries(self, text: str) -> str:
        """Fix incomplete sentences at chunk boundaries."""
        # If text starts with lowercase letter (likely mid-sentence), capitalize
        if text and text[0].islower() and not text.startswith('e.g.') and not text.startswith('i.e.'):
            # Check if it looks like a continuation
            if not any(text.startswith(abbr) for abbr in ['the ', 'a ', 'and ', 'but ', 'or ', 'so ']):
                text = text[0].upper() + text[1:]

        # If text ends abruptly (incomplete sentence), try to complete it
        if text and not text.endswith(('.', '!', '?', ')', ']', '`')):
            # Check if it looks like an incomplete sentence
            if len(text.split()) > 3:  # More than just a phrase
                # Add ellipsis to indicate continuation
                if not text.endswith('...'):
                    text = text + '.'

        return text

    def _fix_punctuation_spacing(self, text: str) -> str:
        """Fix spacing around punctuation marks."""
        # Remove space before punctuation
        text = re.sub(r'\s+([.,!?;:)\]])', r'\1', text)

        # Add space after punctuation (except in abbreviations)
        text = re.sub(r'([.,!?;:])\s*(?=[A-Z])', r'\1 ', text)

        # Fix spacing around parentheses
        text = re.sub(r'\(\s+', '(', text)
        text = re.sub(r'\s+\)', ')', text)

        # Fix spacing around brackets
        text = re.sub(r'\[\s+', '[', text)
        text = re.sub(r'\s+\]', ']', text)

        return text

    def _fix_math_formatting(self, text: str) -> str:
        """Fix LaTeX and math formula formatting.

        Converts broken math notation to proper LaTeX.
        """
        try:
            # Fix cosine similarity formula patterns - use raw strings safely
            # Pattern 1: Similarity = A·B / ||A|| ||B||
            if 'Similarity' in text and ('·' in text or 'A' in text):
                # Simple string replacement approach to avoid regex issues
                text = text.replace('Similarity=A⃗⋅B⃗∥A⃗∥∥B⃗∥',
                                  r'$$ \text{Similarity} = \cos(\theta) = \frac{\vec{A} \cdot \vec{B}}{|\vec{A}| |\vec{B}|} $$')
                text = text.replace('Similarity=A·B/||A||||B||',
                                  r'$$ \text{Similarity} = \cos(\theta) = \frac{\vec{A} \cdot \vec{B}}{|\vec{A}| |\vec{B}|} $$')

            # Pattern 2: Fix dot products safely
            if '·' in text:
                # Simple replacement for common patterns
                text = text.replace('A·B', r'$\vec{A} \cdot \vec{B}$')

            # Don't modify text that already has LaTeX (contains backslashes)
            # This prevents regex errors on escaped sequences
            if '\\' not in text:
                # Only do regex on safe text without LaTeX
                try:
                    text = re.sub(r'\$([^$]+)\$', r'$\1$', text)  # Normalize dollar signs
                except (re.error, ValueError):
                    pass  # Skip if regex fails

        except Exception as e:
            logger.warning(f"Math formatting error: {e}. Skipping math fixes.")

        return text

    def _normalize_patterns(self, text: str) -> str:
        """Normalize common text patterns."""
        try:
            # Fix common typos - simple string replacement
            text = text.replace('teh ', 'the ')
            text = text.replace('hte ', 'the ')

            # Fix duplicate words
            text = text.replace(' a a ', ' a ')
            text = text.replace(' the the ', ' the ')
            text = text.replace(' and and ', ' and ')
            text = text.replace(' is is ', ' is ')

            # Fix spacing around colons
            text = re.sub(r'(\w+)\s+:\s+', r'\1: ', text)

            # Fix spacing around hyphens
            text = re.sub(r'\s+-\s+', '-', text)

        except (re.error, ValueError):
            pass  # Skip if regex fails

        return text

    def _fix_capitalization(self, text: str) -> str:
        """Fix capitalization issues."""
        try:
            # Capitalize sentence starts after periods
            def capitalize_after_period(match):
                space = match.group(1)
                word = match.group(2)
                return space + word.capitalize()

            text = re.sub(r'(\.\s+)([a-z])', capitalize_after_period, text)
        except (re.error, ValueError):
            pass

        return text

    def process_response(self, results: List[Dict]) -> List[Dict]:
        """Process multiple results for clean output.

        Args:
            results: List of chunk results from retrieval

        Returns:
            List of cleaned results with proper grammar
        """
        cleaned_results = []

        for result in results:
            cleaned = result.copy()

            # Process the text field
            if 'text' in cleaned:
                cleaned['text'] = self.process_chunk(cleaned['text'])

            # Process metadata if present
            if 'chunk' in cleaned:
                cleaned['chunk'] = self.process_chunk(cleaned['chunk'])

            cleaned_results.append(cleaned)

        return cleaned_results

    def format_answer(self, answer_text: str) -> str:
        """Format final answer text for presentation.

        Ensures the answer is a complete, well-formed sentence or paragraph.

        Args:
            answer_text: Raw answer text

        Returns:
            Formatted, grammatically correct answer
        """
        if not answer_text:
            return "No answer found."

        # Process the text
        text = self.process_chunk(answer_text)

        # Ensure it ends with proper punctuation
        if text and not text.endswith(('.', '!', '?')):
            text = text + '.'

        # Ensure first letter is capitalized
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        return text

    def merge_chunks(self, chunks: List[str], separator: str = ' ') -> str:
        """Intelligently merge multiple chunks into coherent text.

        Args:
            chunks: List of text chunks to merge
            separator: Separator between chunks (space or newline)

        Returns:
            Merged, coherent text
        """
        if not chunks:
            return ""

        # Clean each chunk
        cleaned = [self.process_chunk(c) for c in chunks if c]

        if not cleaned:
            return ""

        # Smart merging: avoid duplicate sentences and maintain coherence
        merged = []
        seen = set()

        for chunk in cleaned:
            # Get first sentence for duplicate detection
            first_sentence = chunk.split('.')[0]

            if first_sentence not in seen:
                merged.append(chunk)
                seen.add(first_sentence)

        # Join with appropriate separator
        if separator == 'newline':
            result = '\n\n'.join(merged)
        else:
            result = separator.join(merged)

        return result


def create_text_processor() -> TextProcessor:
    """Factory function to create text processor."""
    return TextProcessor()
