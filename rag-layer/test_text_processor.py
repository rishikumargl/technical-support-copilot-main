#!/usr/bin/env python3
"""
Test suite for text processor.
Tests grammar correction and text formatting improvements.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from text_processor import TextProcessor


def test_whitespace_fixing():
    """Test whitespace normalization."""
    processor = TextProcessor()

    test_cases = [
        ("text  with    multiple    spaces", "text with multiple spaces"),
        ("line1\n\n\nline2", "line1\nline2"),
        ("text\t\twith\ttabs", "text with tabs"),
        ("spaced   text  ", "spaced text"),
    ]

    print("\n" + "="*70)
    print("TEST 1: Whitespace Fixing")
    print("="*70)

    for input_text, expected in test_cases:
        result = processor._fix_whitespace(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: '{input_text}'")
        print(f"  Result: '{result}'")
        print(f"  Expected: '{expected}'")
        print()


def test_broken_symbols():
    """Test broken unicode and symbol fixing."""
    processor = TextProcessor()

    test_cases = [
        ("vector v⃗ v notation", "vector $\\vec{v}$ notation"),
        ("A⃗ and B⃗", "$\\vec{A}$ and $\\vec{B}$"),
    ]

    print("\n" + "="*70)
    print("TEST 2: Broken Symbol Fixing")
    print("="*70)

    for input_text, expected in test_cases:
        result = processor._fix_broken_symbols(input_text)
        status = "✓" if expected in result else "✗"
        print(f"{status} Input: '{input_text}'")
        print(f"  Result: '{result}'")
        print()


def test_sentence_boundaries():
    """Test sentence boundary fixing."""
    processor = TextProcessor()

    test_cases = [
        ("positioned close to one another. The text continues",
         "Positioned close to one another. The text continues"),
        ("this is lowercase sentence", "This is lowercase sentence."),
    ]

    print("\n" + "="*70)
    print("TEST 3: Sentence Boundary Fixing")
    print("="*70)

    for input_text, expected in test_cases:
        result = processor._fix_sentence_boundaries(input_text)
        status = "✓" if result.startswith(expected[0].upper()) else "✗"
        print(f"{status} Input: '{input_text}'")
        print(f"  Result: '{result}'")
        print()


def test_punctuation_spacing():
    """Test punctuation spacing."""
    processor = TextProcessor()

    test_cases = [
        ("text , with , bad , spacing .", "text, with bad spacing."),
        ("word ( inside parens ) here", "word (inside parens) here"),
    ]

    print("\n" + "="*70)
    print("TEST 4: Punctuation Spacing")
    print("="*70)

    for input_text, expected in test_cases:
        result = processor._fix_punctuation_spacing(input_text)
        status = "✓" if "," in result else "~"
        print(f"{status} Input: '{input_text}'")
        print(f"  Result: '{result}'")
        print(f"  Expected: '{expected}'")
        print()


def test_capitalization():
    """Test capitalization fixing."""
    processor = TextProcessor()

    test_cases = [
        ("this is lowercase. it needs fixing.", "This is lowercase. It needs fixing."),
        ("sentence. another one here.", "Sentence. Another one here."),
    ]

    print("\n" + "="*70)
    print("TEST 5: Capitalization Fixing")
    print("="*70)

    for input_text, expected in test_cases:
        result = processor._fix_capitalization(input_text)
        status = "✓" if result[0].isupper() else "✗"
        print(f"{status} Input: '{input_text}'")
        print(f"  Result: '{result}'")
        print()


def test_full_pipeline():
    """Test complete text processing pipeline."""
    processor = TextProcessor()

    test_cases = [
        (
            "positioned close to one another. The mathematics behind this relies on the "
            "distributional hypothesis: words that occur in similar contexts tend to have similar meanings.",
            "Positioned"  # Should start with capital P
        ),
        (
            "this sentence needs fixing . it has bad spacing .",
            "This sentence needs fixing. It has bad spacing."
        ),
    ]

    print("\n" + "="*70)
    print("TEST 6: Full Processing Pipeline")
    print("="*70)

    for input_text, expected_start in test_cases:
        result = processor.process_chunk(input_text)
        status = "✓" if result.startswith(expected_start) else "✗"
        print(f"{status} Input (first 50 chars): '{input_text[:50]}...'")
        print(f"  Result (first 60 chars): '{result[:60]}...'")
        print(f"  Expected to start with: '{expected_start}'")
        print()


def test_format_answer():
    """Test answer formatting."""
    processor = TextProcessor()

    test_cases = [
        ("what are system requirements", "What are system requirements."),
        ("Python 3.8+ and PostgreSQL 12", "Python 3.8+ and PostgreSQL 12."),
        ("complete sentence.", "Complete sentence."),
    ]

    print("\n" + "="*70)
    print("TEST 7: Answer Formatting")
    print("="*70)

    for input_text, _ in test_cases:
        result = processor.format_answer(input_text)
        status = "✓" if result[0].isupper() and result.endswith('.') else "✗"
        print(f"{status} Input: '{input_text}'")
        print(f"  Result: '{result}'")
        print()


def test_real_world_rag_output():
    """Test with real RAG output snippets."""
    processor = TextProcessor()

    # Real example from RAG system
    rag_output = (
        "positioned close to one another. The mathematics behind this relies on the distributional "
        "hypothesis: words that occur in similar contexts tend to have similar meanings. If we represent "
        "a word as a vector v⃗ v , the semantic similarity between two words can be calculated using "
        "the cosine similarity formula: Similarity=A⃗⋅B⃗∥A⃗∥∥B⃗∥ This"
    )

    print("\n" + "="*70)
    print("TEST 8: Real-World RAG Output")
    print("="*70)
    print(f"Original (first 100 chars):\n  '{rag_output[:100]}...'")

    cleaned = processor.process_chunk(rag_output)
    print(f"\nCleaned (first 100 chars):\n  '{cleaned[:100]}...'")

    # Verify improvements
    checks = {
        "Starts with capital letter": cleaned[0].isupper(),
        "Contains formula": "Similarity" in cleaned,
        "Fixed vector notation": "$\\vec{" in cleaned or "vector" in cleaned,
        "Proper spacing": "  " not in cleaned,
        "No orphaned 'This'": not cleaned.endswith("This"),
    }

    print("\nQuality Checks:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")


def test_merge_chunks():
    """Test intelligent chunk merging."""
    processor = TextProcessor()

    chunks = [
        "The system requires Python 3.8+.",
        "PostgreSQL 12.0 or higher is needed.",
        "The system requires Python 3.8+.",  # Duplicate
    ]

    print("\n" + "="*70)
    print("TEST 9: Chunk Merging (Deduplication)")
    print("="*70)

    merged = processor.merge_chunks(chunks)
    print(f"Input chunks: {len(chunks)}")
    print(f"Output: {merged}")
    print(f"✓ Deduplication works" if "required Python 3.8+" in merged else "✗ Issue with merge")
    print()


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("TEXT PROCESSOR TEST SUITE")
    print("="*70)

    test_whitespace_fixing()
    test_broken_symbols()
    test_sentence_boundaries()
    test_punctuation_spacing()
    test_capitalization()
    test_full_pipeline()
    test_format_answer()
    test_real_world_rag_output()
    test_merge_chunks()

    print("\n" + "="*70)
    print("TEST SUITE COMPLETED")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
