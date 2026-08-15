import math
from typing import List

class SimpleEmbeddingModel:
    """Frequency-based embedding model for offline/lightweight similarity retrieval."""
    def embed_text(self, text: str) -> List[float]:
        # Generate 128-dimensional vector representation based on word hashes
        words = text.lower().split()
        vector = [0.0] * 128
        for word in words:
            # Map words to vector bins using hash algorithm
            idx = abs(hash(word)) % 128
            vector[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [round(v / norm, 4) for v in vector]

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1)) or 1.0
        norm2 = math.sqrt(sum(b * b for b in vec2)) or 1.0
        return dot / (norm1 * norm2)
