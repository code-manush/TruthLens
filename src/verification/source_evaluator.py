"""
SourceEvaluator: Takes raw corroboration results from WebCorroborator
and produces a structured CorroborationResult with a final credibility
contribution score.
"""

import urllib.parse
from typing import List, Dict, Any

from src.verification.source_search import TRUSTED_DOMAINS


class SourceEvaluator:
    """
    Evaluates the quality of corroboration search results and returns a
    final corroboration credibility score plus a human-readable summary.
    """

    TIER_1_DOMAINS = {
        "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
        "nature.com", "who.int", "cdc.gov", "nasa.gov",
    }
    TIER_2_DOMAINS = {
        "theguardian.com", "nytimes.com", "washingtonpost.com",
        "bloomberg.com", "economist.com", "npr.org", "pbs.org",
        "snopes.com", "factcheck.org", "politifact.com",
    }

    def evaluate(self, corroboration_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the dict returned by WebCorroborator.corroborate() and returns:
          - final_score (0.0–1.0)  — weighted by source tier
          - tier1_count            — number of top-tier sources (Reuters, BBC etc.)
          - tier2_count            — number of secondary-tier sources
          - untrusted_count
          - verdict_label          — human-readable string
          - top_trusted_sources    — list of (domain, title) for display
        """
        matched = corroboration_result.get("matched_sources", [])
        base_score = corroboration_result.get("corroboration_score", 0.15)

        tier1, tier2, untrusted = [], [], []

        for src in matched:
            domain = src.get("domain", "")
            if any(t in domain for t in self.TIER_1_DOMAINS):
                tier1.append(src)
            elif any(t in domain for t in self.TIER_2_DOMAINS):
                tier2.append(src)
            elif src.get("trusted"):
                tier2.append(src)  # Other trusted domains → tier 2
            else:
                untrusted.append(src)

        # Weighted score boost from tier presence
        tier_boost = 0.0
        if len(tier1) >= 1:
            tier_boost += 0.15
        if len(tier1) >= 2:
            tier_boost += 0.10
        if len(tier2) >= 1:
            tier_boost += 0.05

        final_score = round(min(base_score + tier_boost, 1.0), 3)

        # Verdict label
        if len(tier1) >= 2:
            verdict_label = f"Strongly corroborated by {len(tier1)} top-tier sources"
        elif len(tier1) == 1:
            verdict_label = f"Corroborated by 1 top-tier source + {len(tier2)} secondary sources"
        elif len(tier2) >= 2:
            verdict_label = f"Partially corroborated by {len(tier2)} secondary trusted sources"
        elif len(tier2) == 1:
            verdict_label = "Weakly corroborated — only 1 secondary source found"
        else:
            verdict_label = "Not corroborated — no trusted sources found covering this story"

        top_trusted = [
            {"domain": s["domain"], "title": s["title"], "url": s["url"]}
            for s in (tier1 + tier2)[:5]
        ]

        return {
            "final_score": final_score,
            "tier1_count": len(tier1),
            "tier2_count": len(tier2),
            "untrusted_count": len(untrusted),
            "verdict_label": verdict_label,
            "top_trusted_sources": top_trusted,
        }

    def evaluate_url(self, url: str) -> float:
        """Backward-compatible single URL evaluation (used by legacy code)."""
        domain = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
        if any(t in domain for t in self.TIER_1_DOMAINS):
            return 0.95
        if any(t in domain for t in self.TIER_2_DOMAINS):
            return 0.80
        if any(td in domain for td in TRUSTED_DOMAINS):
            return 0.65
        return 0.35
