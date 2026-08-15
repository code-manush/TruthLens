"""
Unified schemas for the Article Credibility Detection Pipeline.

Flow:
  URL  ->  ArticleExtraction
       ->  OllamaAnalysis
       ->  CorroborationResult
       ->  CredibilityScorecard  (final output)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ── 1. Input ────────────────────────────────────────────────────────────────

class ArticleInput(BaseModel):
    """Input provided by the user to analyze."""
    url: Optional[str] = None
    raw_text: Optional[str] = None
    title: Optional[str] = None
    publisher: Optional[str] = None

class AdProfile(BaseModel):
    """Profile of the ads detected on the webpage."""
    total_ad_slots: int = 0
    has_clickbait_ads: bool = False
    clickbait_networks_found: List[str] = Field(default_factory=list)
    ad_density: float = 0.0  # ratio of ads per 100 words


# ── 2. Raw Extraction (from URL / text) ────────────────────────────────────

class ArticleExtraction(BaseModel):
    url: Optional[str] = None
    title: str
    text: str
    authors: List[str] = Field(default_factory=list)
    publish_date: Optional[datetime] = None
    domain: Optional[str] = None
    publisher: Optional[str] = None
    uses_https: bool = False
    word_count: int = 0
    ad_profile: AdProfile = Field(default_factory=AdProfile)
    # kept for legacy compatibility
    meta_keywords: List[str] = Field(default_factory=list)
    meta_description: Optional[str] = None
    outbound_links: List[str] = Field(default_factory=list)
    # backward compat alias fields
    top_image: Optional[str] = None
    num_ads_estimated: int = 0
    ad_ratio: float = 0.0
    ad_details: List[Dict[str, Any]] = Field(default_factory=list)


# Keep old name as alias so existing code doesn't break
ExtractedArticle = ArticleExtraction


# ── 3. Ollama Analysis ──────────────────────────────────────────────────────

class OllamaAnalysis(BaseModel):
    """Structured output from Ollama (qwen3:8b) after reading the article."""

    # Step 1: Core context — what is this article ACTUALLY about?
    article_context: str = Field(default="",
        description="1-2 sentence summary of the core topic of the article")

    # Step 2: Context-filtered facts
    relevant_facts: List[str] = Field(default_factory=list,
        description="Verifiable facts that are directly related to the core context")
    irrelevant_facts: List[str] = Field(default_factory=list,
        description="Facts/statements that are unrelated to the core context of the article")

    # What the article claims / asserts
    main_claims: List[str] = Field(default_factory=list,
        description="Major assertions or conclusions the article makes")

    # Headline / topic signals for Tavily search
    search_queries: List[str] = Field(default_factory=list,
        description="3-5 focused search queries derived from the article for Tavily")

    # Language quality signals
    emotional_phrases: List[str] = Field(default_factory=list,
        description="Emotionally charged, sensational, or fear-inducing phrases")
    clickbait_elements: List[str] = Field(default_factory=list,
        description="Clickbait techniques: curiosity gaps, exaggeration, ALL CAPS misuse, etc.")

    # Bias / misleading flags
    bias_indicators: List[str] = Field(default_factory=list,
        description="One-sided language, absolutist statements, propaganda phrases")
    misleading_patterns: List[str] = Field(default_factory=list,
        description="Patterns that suggest misinformation: miracle cures, hidden secrets, etc.")

    # Content quality summary
    has_named_sources: bool = False
    has_statistics: bool = False
    has_expert_quotes: bool = False
    content_tone: str = "neutral"    # neutral / fear / anger / positive / sensational
    language_quality: str = "normal" # normal / poor / professional


# ── 4. Single Corroborating Source ─────────────────────────────────────────

class CorroboratingSource(BaseModel):
    url: str
    title: str
    domain: str
    snippet: str = ""
    trusted: bool = False
    tier: int = 0          # 1 = top-tier (Reuters/BBC), 2 = secondary, 0 = unknown
    search_query: str = "" # which query found this result
    relevance_score: float = 0.0


# ── 5. Corroboration Result (from Tavily) ──────────────────────────────────

class CorroborationResult(BaseModel):
    total_sources_found: int = 0
    trusted_sources_count: int = 0
    tier1_count: int = 0
    tier2_count: int = 0
    corroboration_score: float = Field(default=0.15, ge=0.0, le=1.0)
    verdict_label: str = "Not checked"
    top_sources: List[CorroboratingSource] = Field(default_factory=list)
    search_queries_used: List[str] = Field(default_factory=list)


# ── 6. Final Scorecard ──────────────────────────────────────────────────────

class DimensionScore(BaseModel):
    name: str
    score: float           # 0–100
    weight: float          # 0–1
    contribution: float    # score * weight
    summary: str = ""


class CredibilityScorecard(BaseModel):
    # Article metadata
    url: Optional[str] = None
    title: str
    domain: Optional[str] = None
    publisher: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    publish_date: Optional[datetime] = None

    # Final verdict
    overall_score: float = Field(..., ge=0.0, le=100.0)
    credibility_rating: str    # HIGH / MODERATE / LOW / UNRELIABLE
    verdict: str               # REAL / LIKELY REAL / LIKELY FAKE / FAKE
    verdict_summary: str

    # Dimension breakdown
    dimensions: List[DimensionScore] = Field(default_factory=list)

    # What the extractor found
    ad_profile: AdProfile = Field(default_factory=AdProfile)

    # What Ollama extracted
    article_context: str = ""
    relevant_facts: List[str] = Field(default_factory=list)
    irrelevant_facts: List[str] = Field(default_factory=list)
    main_claims: List[str] = Field(default_factory=list)
    emotional_phrases: List[str] = Field(default_factory=list)
    clickbait_elements: List[str] = Field(default_factory=list)
    bias_indicators: List[str] = Field(default_factory=list)
    misleading_patterns: List[str] = Field(default_factory=list)
    content_tone: str = "neutral"

    # Corroboration
    corroboration: CorroborationResult

    # Signals
    red_flags: List[str] = Field(default_factory=list)
    positive_signals: List[str] = Field(default_factory=list)
