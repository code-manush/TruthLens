"""
ArticlePipeline: Orchestrates the full 4-step detection pipeline.

  Step 1 — ArticleExtractor   : Extract clean text from URL (trafilatura)
  Step 2 — OllamaExtractor    : Analyze facts, claims, clickbait (qwen3:8b)
  Step 3 — TavilyCorroborator : Search 50 articles across trusted sources
  Step 4 — ScorecardGenerator : Build final credibility scorecard
"""

import logging
from typing import Optional

from src.schemas.article_schema import ArticleInput, CredibilityScorecard
from src.extraction.article_extractor import ArticleExtractor
from src.llm.ollama_extractor import OllamaExtractor
from src.verification.tavily_corroborator import TavilyCorroborator
from src.scoring.scorecard import ScorecardGenerator

logger = logging.getLogger(__name__)


class ArticlePipeline:
    def __init__(
        self,
        extractor: Optional[ArticleExtractor] = None,
        ollama_extractor: Optional[OllamaExtractor] = None,
        corroborator: Optional[TavilyCorroborator] = None,
        scorecard_generator: Optional[ScorecardGenerator] = None,
    ):
        self.extractor      = extractor or ArticleExtractor()
        self.ollama         = ollama_extractor or OllamaExtractor()
        self.corroborator   = corroborator or TavilyCorroborator()
        self.scorer         = scorecard_generator or ScorecardGenerator()

    def run(self, article_input: ArticleInput) -> CredibilityScorecard:

        # ── Step 1: Extract article text ───────────────────────────────────
        logger.info("Step 1/4 — Extracting article text...")
        article = self.extractor.extract(article_input)
        logger.info(f"  Extracted: '{article.title[:60]}' ({article.word_count} words)")

        if not article.text or article.word_count < 30:
            raise ValueError(
                f"Could not extract article text from the provided source.\n"
                f"  Title: '{article.title}'\n"
                f"  Words: {article.word_count}\n"
                f"Please check that the URL is valid and publicly accessible."
            )

        # ── Step 2: Ollama analysis ────────────────────────────────────────
        logger.info("Step 2/4 — Analyzing with Ollama (qwen3:8b)...")
        ollama_analysis = self.ollama.analyze_article(article)
        logger.info(
            f"  Relevant facts: {len(ollama_analysis.relevant_facts)} | "
            f"Irrelevant facts: {len(ollama_analysis.irrelevant_facts)} | "
            f"Claims: {len(ollama_analysis.main_claims)} | "
            f"Queries: {len(ollama_analysis.search_queries)}"
        )

        # ── Step 3: Tavily corroboration ───────────────────────────────────
        logger.info("Step 3/4 — Searching internet for corroborating sources (Tavily)...")
        corroboration = self.corroborator.corroborate(
            search_queries=ollama_analysis.search_queries,
            article_title=article.title,
        )
        logger.info(
            f"  Found: {corroboration.total_sources_found} sources | "
            f"Trusted: {corroboration.trusted_sources_count} "
            f"(Tier1={corroboration.tier1_count}, Tier2={corroboration.tier2_count})"
        )

        # ── Step 3b: Ollama reasoning pass (with Tavily evidence) ──────────
        logger.info("Step 3b/4 — Ollama reasoning over corroboration evidence...")
        search_results_text = self.corroborator.format_results_for_llm(corroboration)
        llm_reasoning = self.ollama.reason_about_credibility(
            article, ollama_analysis, search_results_text
        )

        # ── Step 4: Generate scorecard ─────────────────────────────────────
        logger.info("Step 4/4 — Generating credibility scorecard...")
        scorecard = self.scorer.generate(article, ollama_analysis, corroboration, llm_reasoning)
        logger.info(
            f"  Verdict: {scorecard.verdict} | "
            f"Score: {scorecard.overall_score}/100 [{scorecard.credibility_rating}]"
        )

        return scorecard
