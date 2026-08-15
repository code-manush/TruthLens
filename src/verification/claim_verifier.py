"""
ClaimVerifier: Uses Tavily to search for live evidence for/against each
extracted claim, then uses Ollama (qwen3:8b) to reason over the evidence
and return a verdict.
"""

import logging
from typing import List, Optional

from tavily import TavilyClient

from src.schemas.article_schema import Claim
from src.config.settings import settings
from src.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

CLAIM_VERIFY_SYSTEM_PROMPT = """You are a meticulous fact-checker. You will be given a claim made in a news article and a set of search results from trusted news sources.

Your job:
1. Read the claim carefully.
2. Read the search result snippets.
3. Decide if the search results SUPPORT, CONTRADICT, or are UNVERIFIED with respect to the claim.

Rules:
- Only mark SUPPORTED if at least one result clearly confirms the claim with specific details.
- Mark CONTRADICTED if any result directly disputes or refutes the claim with evidence.
- Mark UNVERIFIED if results are vague, unrelated, or insufficient.
- Do NOT make up information. Base your verdict ONLY on the provided snippets.

Respond ONLY in this exact JSON format:
{
  "verdict": "SUPPORTED" | "CONTRADICTED" | "UNVERIFIED",
  "confidence": <float 0.0 to 1.0>,
  "reasoning": "<one sentence explanation>"
}"""


class ClaimVerifier:
    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        ollama_client: Optional[OllamaClient] = None,
    ):
        key = tavily_api_key or settings.tavily_api_key
        self.tavily = TavilyClient(api_key=key) if key else None
        self.llm = ollama_client or OllamaClient()

    def verify_claims(self, claims: List[Claim]) -> List[Claim]:
        """Verify each claim using live Tavily search + Ollama reasoning."""
        verified = []
        for claim in claims:
            try:
                evidence_snippets = self._search_evidence(claim.statement)
                result = self._llm_verdict(claim.statement, evidence_snippets)
                claim.verdict = result.get("verdict", "UNVERIFIED")
                claim.confidence = float(result.get("confidence", 0.5))
                claim.supporting_evidence = evidence_snippets[:3]
            except Exception as e:
                logger.warning(f"Claim verification failed for '{claim.statement[:50]}': {e}")
                claim.verdict = "UNVERIFIED"
                claim.confidence = 0.3
            verified.append(claim)
        return verified

    def _search_evidence(self, statement: str) -> List[str]:
        """Search Tavily for evidence snippets related to the claim."""
        if not self.tavily:
            return []
        try:
            response = self.tavily.search(
                query=statement,
                search_depth="basic",
                topic="news",
                max_results=5,
                include_answer=False,
            )
            snippets = []
            for r in response.get("results", []):
                content = r.get("content", "").strip()
                source = r.get("url", "")
                if content:
                    snippets.append(f"[{source}] {content[:250]}")
            return snippets
        except Exception as e:
            logger.error(f"Tavily claim search error: {e}")
            return []

    def _llm_verdict(self, statement: str, snippets: List[str]) -> dict:
        """Ask Ollama to reason over evidence snippets and return a verdict."""
        if not snippets:
            return {"verdict": "UNVERIFIED", "confidence": 0.2, "reasoning": "No evidence found online"}

        evidence_block = "\n".join(f"- {s}" for s in snippets)
        prompt = (
            f"CLAIM: {statement}\n\n"
            f"SEARCH EVIDENCE:\n{evidence_block}\n\n"
            "Based ONLY on the above evidence, provide your verdict in JSON."
        )
        result = self.llm.generate_json(prompt, system_prompt=CLAIM_VERIFY_SYSTEM_PROMPT)
        # Validate keys
        if "verdict" not in result or result["verdict"] not in ("SUPPORTED", "CONTRADICTED", "UNVERIFIED"):
            result["verdict"] = "UNVERIFIED"
        result.setdefault("confidence", 0.4)
        return result
