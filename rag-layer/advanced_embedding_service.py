"""
Advanced embedding service with ensemble and query expansion capabilities.
Combines multiple embedding models and provides adaptive weighting.
"""
import logging
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import re

logger = logging.getLogger(__name__)


class EnsembleEmbeddingService:
    """Generate embeddings using ensemble of multiple models.

    Combines embeddings from multiple models for better coverage of semantic space.
    Supports weighted ensemble and dimension reduction.
    """

    def __init__(
        self,
        model_names: Optional[List[str]] = None,
        use_ensemble: bool = True,
        ensemble_strategy: str = "mean"
    ):
        """Initialize ensemble embedding service.

        Args:
            model_names: List of HuggingFace model names
                Default: ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
            use_ensemble: If True, use ensemble of models; if False, use first model only
            ensemble_strategy: "mean" (average), "concat" (concatenate), or "max"
        """
        if model_names is None:
            model_names = [
                "all-MiniLM-L6-v2",      # Fast, lightweight
                "all-mpnet-base-v2",     # Slower, more accurate
            ]

        self.model_names = model_names
        self.use_ensemble = use_ensemble
        self.ensemble_strategy = ensemble_strategy
        self.models = []
        self.dimensions = []

        logger.info(f"Loading {len(model_names)} embedding models...")
        for model_name in model_names:
            try:
                model = SentenceTransformer(model_name)
                self.models.append(model)
                dim = model.get_sentence_embedding_dimension()
                self.dimensions.append(dim)
                logger.info(f"  ✓ {model_name} (dim={dim})")
            except Exception as e:
                logger.warning(f"  ✗ Failed to load {model_name}: {e}")

        if not self.models:
            raise ValueError("No embedding models loaded successfully")

        self.primary_model = self.models[0]
        self.primary_dimension = self.dimensions[0]
        logger.info(f"Ensemble initialized: {len(self.models)} models, strategy={ensemble_strategy}")

    def embed_text(self, text: str) -> np.ndarray:
        """Embed single text using ensemble or single model."""
        if not self.use_ensemble or len(self.models) == 1:
            return self.primary_model.encode(text, convert_to_numpy=True)

        embeddings = [model.encode(text, convert_to_numpy=True) for model in self.models]
        return self._combine_embeddings(embeddings)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embed multiple texts using ensemble."""
        if not self.use_ensemble or len(self.models) == 1:
            return self.primary_model.encode(texts, convert_to_numpy=True)

        all_embeddings = [model.encode(texts, convert_to_numpy=True) for model in self.models]

        # Combine embeddings for each text
        combined = []
        for i in range(len(texts)):
            text_embeddings = [model_embs[i] for model_embs in all_embeddings]
            combined_emb = self._combine_embeddings(text_embeddings)
            combined.append(combined_emb)

        return combined

    def _combine_embeddings(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """Combine multiple embeddings using specified strategy."""
        if self.ensemble_strategy == "mean":
            # Average embeddings
            combined = np.mean(embeddings, axis=0)
        elif self.ensemble_strategy == "concat":
            # Concatenate embeddings
            combined = np.concatenate(embeddings)
        elif self.ensemble_strategy == "max":
            # Element-wise maximum
            combined = np.max(embeddings, axis=0)
        else:
            combined = np.mean(embeddings, axis=0)

        # Normalize
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm

        return combined

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Embed text from list of chunk dictionaries."""
        try:
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embed_batch(texts)

            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding.tolist() if hasattr(embedding, 'tolist') else embedding

            logger.info(f"Embedded {len(chunks)} chunks using ensemble")
            return chunks
        except Exception as e:
            logger.error(f"Failed to embed chunks: {str(e)}")
            raise


class QueryExpander:
    """Expand queries with synonyms and variations for better retrieval."""

    def __init__(self):
        """Initialize query expander with synonym mappings."""
        self.synonyms = {
            'setup': ['installation', 'deploy', 'configure', 'initialize'],
            'issue': ['problem', 'bug', 'error', 'failure', 'incident'],
            'fix': ['resolve', 'solution', 'patch', 'remedy', 'correct'],
            'process': ['workflow', 'procedure', 'method', 'steps', 'flow'],
            'data': ['information', 'records', 'content', 'details'],
            'system': ['platform', 'application', 'service', 'infrastructure'],
            'user': ['person', 'account', 'profile', 'member'],
            'error': ['exception', 'fault', 'malfunction', 'issue', 'problem'],
            'update': ['upgrade', 'patch', 'modify', 'change', 'revision'],
            'delete': ['remove', 'erase', 'clear', 'purge', 'eliminate'],
        }

        self.acronym_expansions = {
            'api': 'application programming interface',
            'db': 'database',
            'ui': 'user interface',
            'ux': 'user experience',
            'hr': 'human resources',
            'it': 'information technology',
            'qa': 'quality assurance',
            'ops': 'operations',
            'eng': 'engineering',
            'sql': 'structured query language',
            'ssl': 'secure sockets layer',
            'auth': 'authentication',
        }

        logger.info("QueryExpander initialized")

    def expand(self, query: str, max_variations: int = 3) -> List[str]:
        """Generate query variations for ensemble retrieval.

        Args:
            query: Original query
            max_variations: Maximum number of variations to generate

        Returns:
            List of original + expanded query variations
        """
        variations = [query]

        # Expand acronyms
        expanded = self._expand_acronyms(query)
        if expanded != query:
            variations.append(expanded)

        # Add synonym variations
        synonymized = self._add_synonyms(query)
        variations.extend(synonymized[:max_variations - len(variations)])

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for v in variations:
            if v not in seen:
                seen.add(v)
                unique.append(v)

        return unique[:max_variations]

    def _expand_acronyms(self, query: str) -> str:
        """Expand acronyms in query."""
        expanded = query.lower()

        for acronym, expansion in self.acronym_expansions.items():
            pattern = rf'\b{acronym}\b'
            expanded = re.sub(pattern, expansion, expanded, flags=re.IGNORECASE)

        return expanded

    def _add_synonyms(self, query: str) -> List[str]:
        """Generate synonym-based query variations."""
        variations = []
        words = query.lower().split()

        for i, word in enumerate(words):
            if word in self.synonyms:
                for syn in self.synonyms[word]:
                    new_words = words.copy()
                    new_words[i] = syn
                    variations.append(' '.join(new_words))

        return variations


class AdaptiveWeightLearner:
    """Learn optimal weights for hybrid search based on user feedback."""

    def __init__(self, initial_dense_weight: float = 0.6, initial_sparse_weight: float = 0.4):
        """Initialize weight learner.

        Args:
            initial_dense_weight: Initial weight for dense search
            initial_sparse_weight: Initial weight for sparse search
        """
        self.dense_weight = initial_dense_weight
        self.sparse_weight = initial_sparse_weight
        self.feedback_samples = []
        self.min_samples = 10

        logger.info(
            f"AdaptiveWeightLearner initialized: "
            f"dense={initial_dense_weight}, sparse={initial_sparse_weight}"
        )

    def add_feedback(self, dense_score: float, sparse_score: float, relevance: bool):
        """Record user feedback for a result.

        Args:
            dense_score: Dense search score for this result
            sparse_score: Sparse (BM25) score for this result
            relevance: Whether user found this result relevant (True/False)
        """
        self.feedback_samples.append({
            'dense': dense_score,
            'sparse': sparse_score,
            'relevant': relevance
        })

        if len(self.feedback_samples) >= self.min_samples:
            self._update_weights()

    def _update_weights(self):
        """Update weights using collected feedback.

        Uses simple heuristic: increase weight for modality that
        correlates better with relevance.
        """
        try:
            relevant_samples = [s for s in self.feedback_samples if s['relevant']]
            irrelevant_samples = [s for s in self.feedback_samples if not s['relevant']]

            if not relevant_samples or not irrelevant_samples:
                return

            # Calculate average scores
            relevant_dense = np.mean([s['dense'] for s in relevant_samples])
            relevant_sparse = np.mean([s['sparse'] for s in relevant_samples])
            irrelevant_dense = np.mean([s['dense'] for s in irrelevant_samples])
            irrelevant_sparse = np.mean([s['sparse'] for s in irrelevant_samples])

            # Calculate separation (gap between relevant and irrelevant)
            dense_separation = relevant_dense - irrelevant_dense
            sparse_separation = relevant_sparse - irrelevant_sparse

            # Update weights based on which modality separates better
            total_sep = abs(dense_separation) + abs(sparse_separation)
            if total_sep > 0:
                self.dense_weight = abs(dense_separation) / total_sep
                self.sparse_weight = abs(sparse_separation) / total_sep

                logger.info(
                    f"Weights updated based on {len(self.feedback_samples)} samples: "
                    f"dense={self.dense_weight:.3f}, sparse={self.sparse_weight:.3f}"
                )

                # Reset samples after update
                self.feedback_samples = []
        except Exception as e:
            logger.warning(f"Failed to update weights: {e}")

    def get_weights(self) -> Dict[str, float]:
        """Get current weights."""
        return {
            'dense': self.dense_weight,
            'sparse': self.sparse_weight
        }
