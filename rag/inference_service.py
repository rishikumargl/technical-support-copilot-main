"""
Inference Service - HuggingFace Inference API
Uses HuggingFace inference for LLM responses instead of OpenAI
"""
import os
import logging
from typing import Optional, List, Dict
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

logger = logging.getLogger(__name__)


class InferenceService:
    """Handle LLM inference using HuggingFace API with OpenAI-compatible interface."""

    def __init__(self, hf_token: Optional[str] = None, model: str = "meta-llama/Llama-3.1-8B-Instruct:novita"):
        """
        Initialize inference service.

        Args:
            hf_token: HuggingFace API token (from environment if not provided)
            model: Model to use (default: Llama 3.1 8B)
        """
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN not found in environment variables")

        self.model = model
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.hf_token,
        )
        logger.info(f"Initialized HuggingFace inference with model: {model}")

    def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        """
        Generate a response using HuggingFace inference.

        Args:
            query: User's question
            context: Retrieved context from RAG
            system_prompt: Custom system prompt (optional)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text
        """
        try:
            # Build system prompt
            if system_prompt is None:
                system_prompt = (
                    "You are a helpful enterprise assistant. "
                    "Answer questions based on the provided context. "
                    "If the context doesn't contain the answer, say 'I don't have this information in my knowledge base.'"
                )

            # Build user message with context
            if context:
                user_message = (
                    f"Context:\n{context}\n\n"
                    f"Question: {query}\n\n"
                    f"Answer:"
                )
            else:
                user_message = query

            # Call HuggingFace inference
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            response = completion.choices[0].message.content
            logger.info(f"Generated response for query: {query[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            return f"Error generating response: {str(e)}"

    def answer_with_sources(
        self,
        query: str,
        search_results: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> Dict[str, any]:
        """
        Generate an answer using retrieved search results as context.

        Args:
            query: User's question
            search_results: Results from hybrid_search
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            if not search_results:
                return {
                    "answer": "No relevant information found in the knowledge base.",
                    "sources": [],
                    "confidence": 0.0,
                    "model": self.model
                }

            # Build context from search results
            context_parts = []
            sources = []
            for i, result in enumerate(search_results[:3], 1):  # Top 3 results
                context_parts.append(
                    f"[Source {i}] {result['document_name']} (v{result['version']})\n"
                    f"{result['text']}"
                )
                sources.append({
                    "document": result['document_name'],
                    "version": result['version'],
                    "department": result['department'],
                    "category": result['category'],
                    "confidence": float(result['combined_score'])
                })

            context = "\n\n".join(context_parts)

            # Generate answer
            answer = self.generate_response(
                query=query,
                context=context,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Calculate average confidence from sources
            avg_confidence = sum(s['confidence'] for s in sources) / len(sources) if sources else 0.0

            return {
                "answer": answer,
                "sources": sources,
                "confidence": avg_confidence,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "model": self.model
            }

    def stream_response(
        self,
        query: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Stream response generation (if supported by model).

        Args:
            query: User's question
            context: Retrieved context
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Yields:
            Response chunks as they are generated
        """
        try:
            if context:
                user_message = (
                    f"Context:\n{context}\n\n"
                    f"Question: {query}\n\n"
                    f"Answer:"
                )
            else:
                user_message = query

            # Create streaming completion
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful enterprise assistant."},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Stream failed: {str(e)}")
            yield f"Error: {str(e)}"


# Global inference service instance
_inference = None


def initialize_inference(hf_token: Optional[str] = None) -> InferenceService:
    """Initialize global inference service."""
    global _inference
    if _inference is None:
        _inference = InferenceService(hf_token=hf_token)
    return _inference


def get_inference() -> InferenceService:
    """Get initialized inference service."""
    global _inference
    if _inference is None:
        _inference = initialize_inference()
    return _inference


if __name__ == "__main__":
    # Test the inference service
    import sys

    print("Testing HuggingFace Inference Service")
    print("=" * 50)

    try:
        service = InferenceService()

        # Test 1: Simple query
        print("\n1. Simple query test:")
        response = service.generate_response(
            query="What is the capital of France?",
            temperature=0.5,
            max_tokens=100
        )
        print(f"Response: {response}")

        # Test 2: With context
        print("\n2. Query with context:")
        context = "Paris is the capital and largest city of France."
        response = service.generate_response(
            query="What is the capital of France?",
            context=context,
            temperature=0.5,
            max_tokens=100
        )
        print(f"Response: {response}")

        # Test 3: Answer with sources
        print("\n3. Answer with sources:")
        mock_results = [
            {
                'document_name': 'Geography Guide',
                'version': '1.0',
                'department': 'Education',
                'category': 'Guide',
                'text': 'France is a country in Western Europe. Paris is its capital.',
                'combined_score': 0.95
            }
        ]
        result = service.answer_with_sources(
            query="What is the capital of France?",
            search_results=mock_results
        )
        print(f"Answer: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print(f"Confidence: {result['confidence']:.2%}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
