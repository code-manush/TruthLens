import re
from typing import List, Optional
from src.schemas.article_schema import Claim
from src.llm.llm_analyzer import LLMAnalyzer

class ClaimExtractor:
    def __init__(self, llm_analyzer: Optional[LLMAnalyzer] = None):
        self.llm_analyzer = llm_analyzer or LLMAnalyzer()

    def extract_heuristic_claims(self, text: str) -> List[Claim]:
        """Extract claim candidates using regex sentence matching for numbers, stats, and quotes."""
        sentences = re.split(r'(?<=[.!?]) +', text)
        claims = []

        for stmt in sentences:
            stmt_clean = stmt.strip()
            # Match sentences with percentages, large numbers, quotes, or strong claim keywords
            if (re.search(r'\b\d+(?:\.\d+)?%?\b', stmt_clean) or '"' in stmt_clean or 
                any(kw in stmt_clean.lower() for kw in ["found that", "announced", "according to", "study shows", "discovered"])):
                if len(stmt_clean) > 20:
                    claims.append(Claim(statement=stmt_clean, confidence=0.6))
            if len(claims) >= 5:
                break
        return claims

    def extract_claims(self, text: str) -> List[Claim]:
        """Extract claims using LLM with fallback to heuristic extraction."""
        llm_claims_data = self.llm_analyzer.extract_claims(text)
        claims = []

        for data in llm_claims_data:
            if isinstance(data, dict) and "statement" in data:
                claims.append(Claim(
                    statement=data["statement"],
                    speaker_or_source=data.get("speaker_or_source"),
                    confidence=0.75
                ))

        if not claims:
            claims = self.extract_heuristic_claims(text)

        return claims
