
"""
WebCorroborator: Uses Tavily to search for corroborating news articles
from trusted sources on the internet, then scrapes and scores their content
using trafilatura for clean text extraction.
"""

import urllib.parse
import logging
from typing import List, Dict, Any, Optional

import trafilatura
from tavily import TavilyClient

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Curated master list of globally trusted news and fact-checking domains
TRUSTED_DOMAINS = [
    # International Wire Services
    "reuters.com", "apnews.com", "afp.com", "bloomberg.com",

    # Major International Broadcasters / Papers
    "bbc.com", "bbc.co.uk", "theguardian.com", "nytimes.com",
    "washingtonpost.com", "economist.com", "ft.com", "wsj.com",
    "theatlantic.com", "npr.org", "pbs.org", "abc.net.au",

    # Science / Health / Research
    "nature.com", "science.org", "sciencedirect.com", "pubmed.ncbi.nlm.nih.gov",
    "who.int", "cdc.gov", "nih.gov", "nasa.gov", "arxiv.org",

    # Fact-Checking organisations
    "snopes.com", "factcheck.org", "politifact.com", "fullfact.org",

    # Government / Academic
    "un.org", "europa.eu", "gov.uk", "congress.gov",
]


class WebCorroborator:
    """
    Searches the web via Tavily for articles similar to the input,
    filters results by trusted domains, and returns a corroboration score.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.tavily_api_key
        if not key:
            raise ValueError("Tavily API key not set. Add TAVILY_API_KEY to .env")
        self.client = TavilyClient(api_key=key)

    # ── Public API ────────────────────────────────────────────────────────────

    def corroborate(self, title: str, text: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for news articles covering the same event/topic.

        Returns a dict with:
          - corroboration_score (0.0–1.0)
          - trusted_sources_found (int)
          - total_results_found (int)
          - matched_sources (list of dicts with url, title, snippet, domain, trusted)
          - search_query (str)
        """
        query = self._build_query(title, text)
        raw_results = self._tavily_search(query, max_results)

        if not raw_results:
            return self._empty_result(query)

        matched = self._classify_results(raw_results)
        trusted_count = sum(1 for r in matched if r["trusted"])
        score = self._compute_score(trusted_count, len(matched))

        return {
            "corroboration_score": score,
            "trusted_sources_found": trusted_count,
            "total_results_found": len(matched),
            "matched_sources": matched,
            "search_query": query,
        }

    def scrape_article_text(self, url: str) -> Optional[str]:
        """Use trafilatura to scrape clean article text from a URL."""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        return None

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _build_query(self, title: str, text: str) -> str:
        """Build a focused search query from the article title + key noun phrases."""
        # Use the title as the primary query; append first 80 chars of text for context
        title_clean = title.strip().strip('"').strip("'")
        context = text[:80].strip().replace("\n", " ")
        return f"{title_clean} {context}"[:200]

    def _tavily_search(self, query: str, max_results: int) -> List[Dict]:
        """Call Tavily news search and return raw results."""
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                topic="news",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
            )
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []

    def _classify_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Tag each result as trusted or not and normalize fields."""
        classified = []
        for r in results:
            url = r.get("url", "")
            domain = self._extract_domain(url)
            trusted = any(td in domain for td in TRUSTED_DOMAINS)
            classified.append({
                "url": url,
                "title": r.get("title", ""),
                "snippet": r.get("content", "")[:300],
                "domain": domain,
                "trusted": trusted,
                "score": r.get("score", 0.0),
            })
        return classified

    def _compute_score(self, trusted_count: int, total: int) -> float:
        """
        Score logic:
        - 3+ trusted sources → 0.90
        - 2 trusted sources  → 0.75
        - 1 trusted source   → 0.55
        - 0 trusted sources  → proportional penalty based on total results
        """
        if trusted_count >= 3:
            return round(min(0.70 + (trusted_count * 0.05), 1.0), 3)
        elif trusted_count == 2:
            return 0.75
        elif trusted_count == 1:
            return 0.55
        else:
            # No trusted sources — penalise based on how many untrusted ones exist
            if total == 0:
                return 0.15   # Story found nowhere — very suspicious
            elif total <= 2:
                return 0.25   # Story barely found
            else:
                return 0.35   # Found on many sites, but none trusted

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower().replace("www.", "")
        except Exception:
            return url

    def _empty_result(self, query: str) -> Dict[str, Any]:
        return {
            "corroboration_score": 0.15,
            "trusted_sources_found": 0,
            "total_results_found": 0,
            "matched_sources": [],
            "search_query": query,
        }
