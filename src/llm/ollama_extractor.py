"""
OllamaExtractor: Sends article text to local Ollama (qwen3:8b) and
parses the structured JSON response into OllamaAnalysis.

New: context-first approach — LLM first identifies article_context,
then filters extracted facts into relevant_facts and irrelevant_facts.
"""

import json
import logging
import re
from typing import Optional, List, Dict, Any

from src.schemas.article_schema import OllamaAnalysis, ArticleExtraction
from src.llm.ollama_client import OllamaClient
from src.llm.prompts import ARTICLE_ANALYSIS_PROMPT, CREDIBILITY_REASONING_PROMPT

logger = logging.getLogger(__name__)

MAX_TEXT_CHARS = 6000


class OllamaExtractor:
    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()

    # ── Primary analysis ──────────────────────────────────────────────────

    def analyze_article(self, article: ArticleExtraction) -> OllamaAnalysis:
        """
        Context-first analysis:
          1. LLM identifies the core context of the article
          2. Extracts ALL facts
          3. Filters them into relevant_facts (match context) and
             irrelevant_facts (don't match — potential padding/red flag)
          4. Extracts claims, search queries, language signals
        """
        text_snippet = article.text[:MAX_TEXT_CHARS]
        prompt = ARTICLE_ANALYSIS_PROMPT.format(
            title=article.title,
            text=text_snippet,
        )

        raw = self.client.generate(prompt, temperature=0.1)
        data = self._parse_json(raw)

        if not data or "article_context" not in data:
            logger.warning("Ollama returned invalid JSON for article analysis. Using fallback.")
            return self._fallback_analysis(article)

        analysis = OllamaAnalysis(
            article_context=str(data.get("article_context", "")),
            relevant_facts=self._list_field(data, "relevant_facts"),
            irrelevant_facts=self._list_field(data, "irrelevant_facts"),
            main_claims=self._list_field(data, "main_claims"),
            search_queries=self._list_field(data, "search_queries"),
            emotional_phrases=self._list_field(data, "emotional_phrases"),
            clickbait_elements=self._list_field(data, "clickbait_elements"),
            bias_indicators=self._list_field(data, "bias_indicators"),
            misleading_patterns=self._list_field(data, "misleading_patterns"),
            has_named_sources=bool(data.get("has_named_sources", False)),
            has_statistics=bool(data.get("has_statistics", False)),
            has_expert_quotes=bool(data.get("has_expert_quotes", False)),
            content_tone=str(data.get("content_tone", "neutral")),
            language_quality=str(data.get("language_quality", "normal")),
        )

        logger.info(
            f"  Context: '{analysis.article_context[:80]}'\n"
            f"  Relevant facts: {len(analysis.relevant_facts)} | "
            f"Irrelevant facts: {len(analysis.irrelevant_facts)}"
        )

        return analysis

    # ── Secondary reasoning pass ──────────────────────────────────────────

    def reason_about_credibility(
        self,
        article: ArticleExtraction,
        ollama_analysis: OllamaAnalysis,
        search_results_text: str,
    ) -> Dict[str, Any]:
        """
        Second Ollama call: given Tavily results, ask Ollama to reason about
        credibility and generate red flags / positive signals.
        Now includes article_context in the prompt for better reasoning.
        """
        claims_text = "\n".join(f"- {c}" for c in ollama_analysis.relevant_facts[:5])
        if not claims_text:
            claims_text = "\n".join(f"- {c}" for c in ollama_analysis.main_claims[:5])

        prompt = CREDIBILITY_REASONING_PROMPT.format(
            title=article.title,
            domain=article.domain or "unknown",
            article_context=ollama_analysis.article_context or "Not determined",
            claims=claims_text or "No specific facts extracted.",
            search_results=search_results_text[:3000],
        )

        raw = self.client.generate(prompt, temperature=0.1)
        data = self._parse_json(raw)

        if not data:
            return {
                "corroboration_assessment": "Could not assess — LLM unavailable.",
                "red_flags": [],
                "positive_signals": [],
                "overall_reasoning": "Automated analysis only — LLM reasoning unavailable.",
            }
        return data

    # ── Helpers ───────────────────────────────────────────────────────────

    def _parse_json(self, raw: str) -> Optional[Dict[str, Any]]:
        if not raw:
            return None
        # Strip <think>...</think> blocks from qwen3 chain-of-thought
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        # Try code-fenced JSON first
        for pattern in [r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```"]:
            m = re.search(pattern, raw, re.DOTALL)
            if m:
                raw = m.group(1).strip()
                break
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    pass
        logger.warning(f"Failed to parse JSON from LLM response. Raw snippet: {raw[:200]}")
        return None

    def _list_field(self, data: Dict, key: str) -> List[str]:
        val = data.get(key, [])
        if isinstance(val, list):
            return [str(v) for v in val if v]
        return []

    def _fallback_analysis(self, article: ArticleExtraction) -> OllamaAnalysis:
        """Heuristic-only fallback if Ollama is unavailable."""
        return OllamaAnalysis(
            article_context="",
            relevant_facts=[],
            irrelevant_facts=[],
            main_claims=[],
            search_queries=[article.title[:120]],
            emotional_phrases=[],
            clickbait_elements=[],
            bias_indicators=[],
            misleading_patterns=[],
            has_named_sources=False,
            has_statistics=False,
            has_expert_quotes=False,
            content_tone="neutral",
            language_quality="normal",
        )
