"""
AuthenticityAnalyzer: Combines static author/domain signals with live
web corroboration via Tavily to produce a comprehensive authenticity score.
"""

import logging
from typing import Optional

from src.schemas.article_schema import AuthenticityAnalysis, ExtractedArticle
from src.verification.source_search import WebCorroborator
from src.verification.source_evaluator import SourceEvaluator
from src.llm.llm_analyzer import LLMAnalyzer

logger = logging.getLogger(__name__)

HIGH_REPUTATION_DOMAINS = [
    "reuters.com", "apnews.com", "bbc.com", "nytimes.com",
    "washingtonpost.com", "nature.com", "sciencedirect.com",
    "theguardian.com", "economist.com", "nasa.gov", "cdc.gov",
]


class AuthenticityAnalyzer:
    def __init__(
        self,
        llm_analyzer: Optional[LLMAnalyzer] = None,
        corroborator: Optional[WebCorroborator] = None,
        evaluator: Optional[SourceEvaluator] = None,
    ):
        self.llm_analyzer = llm_analyzer or LLMAnalyzer()
        self.evaluator = evaluator or SourceEvaluator()
        # Corroborator may fail if key is missing; we handle gracefully
        try:
            self.corroborator = corroborator or WebCorroborator()
        except Exception as e:
            logger.warning(f"WebCorroborator unavailable: {e}")
            self.corroborator = None

    def analyze(self, article: ExtractedArticle) -> AuthenticityAnalysis:
        author_verified = len(article.authors) > 0
        has_publish_date = article.publish_date is not None

        # Static domain reputation
        source_score = 0.5
        domain_clean = (article.domain or "").lower().replace("www.", "")
        if domain_clean and any(t in domain_clean for t in HIGH_REPUTATION_DOMAINS):
            source_score = 0.95
        elif domain_clean:
            source_score = 0.65

        # AI-generation likelihood via Ollama
        llm_res = self.llm_analyzer.analyze_authenticity(article.title, article.text)
        ai_likelihood = float(llm_res.get("ai_generated_likelihood", 0.15))

        # ── Live web corroboration via Tavily ─────────────────────────────────
        corroboration_score = 0.15
        trusted_sources_found = 0
        total_results_found = 0
        corroboration_verdict = "Not checked"
        top_trusted_sources = []
        search_query_used = ""

        if self.corroborator:
            try:
                logger.info(f"Running web corroboration for: {article.title[:60]}")
                corr_raw = self.corroborator.corroborate(article.title, article.text)
                eval_result = self.evaluator.evaluate(corr_raw)

                corroboration_score = eval_result["final_score"]
                trusted_sources_found = eval_result["tier1_count"] + eval_result["tier2_count"]
                total_results_found = corr_raw.get("total_results_found", 0)
                corroboration_verdict = eval_result["verdict_label"]
                top_trusted_sources = eval_result["top_trusted_sources"]
                search_query_used = corr_raw.get("search_query", "")

                logger.info(
                    f"Corroboration: score={corroboration_score}, "
                    f"trusted={trusted_sources_found}/{total_results_found}"
                )
            except Exception as e:
                logger.error(f"Corroboration failed: {e}")
                corroboration_verdict = f"Corroboration error: {e}"

        return AuthenticityAnalysis(
            author_verified=author_verified,
            source_reputation_score=source_score,
            has_publish_date=has_publish_date,
            ai_generated_likelihood=round(ai_likelihood, 3),
            corroboration_score=corroboration_score,
            trusted_sources_found=trusted_sources_found,
            total_results_found=total_results_found,
            corroboration_verdict=corroboration_verdict,
            top_trusted_sources=top_trusted_sources,
            search_query_used=search_query_used,
        )
