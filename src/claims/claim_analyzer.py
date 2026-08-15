from typing import List, Dict, Any
from src.schemas.article_schema import Claim

class ClaimAnalyzer:
    def analyze_claim_density(self, claims: List[Claim], text_word_count: int) -> Dict[str, Any]:
        count = len(claims)
        density = count / (text_word_count / 100.0) if text_word_count > 0 else 0.0
        return {
            "claim_count": count,
            "claim_density_per_100_words": round(density, 2)
        }
