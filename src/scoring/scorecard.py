"""
ScorecardGenerator: Combines all analysis outputs into the final
CredibilityScorecard with a REAL/FAKE verdict and full dimension breakdown.
"""

from typing import List, Dict, Any

from src.schemas.article_schema import (
    ArticleExtraction, OllamaAnalysis, CorroborationResult,
    CredibilityScorecard, DimensionScore
)
from src.verification.tavily_corroborator import KNOWN_UNRELIABLE


class ScorecardGenerator:
    """
    Weights (must sum to 1.0):
      corroboration  35% — live web evidence is the strongest signal
      content        25% — what Ollama found: bias, misleading, clickbait
      source_trust   20% — domain of the original article
      language       10% — emotional language, sensationalism
      metadata        10% — author, date, HTTPS, named sources
    """
    WEIGHTS = {
        "corroboration": 0.35,
        "content":       0.25,
        "source_trust":  0.20,
        "language":      0.10,
        "metadata":      0.10,
    }

    def generate(
        self,
        article: ArticleExtraction,
        ollama: OllamaAnalysis,
        corr: CorroborationResult,
        llm_reasoning: Dict[str, Any],
    ) -> CredibilityScorecard:

        # ── Dimension 1: Corroboration ─────────────────────────────────────
        corr_score = round(corr.corroboration_score * 100, 1)

        # ── Dimension 2: Content quality ───────────────────────────────────────
        # Deductions for bad content signals
        bias_penalty        = min(len(ollama.bias_indicators) * 12, 40)
        misleading_penalty  = min(len(ollama.misleading_patterns) * 18, 54)
        clickbait_penalty   = min(len(ollama.clickbait_elements) * 10, 30)
        # IRRELEVANT FACTS PENALTY: each off-context fact deducts 5 points
        irrelevant_penalty  = min(len(ollama.irrelevant_facts) * 5, 30)

        # AD QUALITY PENALTY
        ad_prof = article.ad_profile
        clickbait_ad_penalty = 10 if ad_prof.has_clickbait_ads else 0
        ad_density_penalty = 0
        if ad_prof.ad_density > 1.0: # more than 1 ad per 100 words
            ad_density_penalty = min(int((ad_prof.ad_density - 1.0) * 5), 15)
        
        content_raw = 100 - bias_penalty - misleading_penalty - clickbait_penalty - irrelevant_penalty - clickbait_ad_penalty - ad_density_penalty
        # Bonuses for good signals
        if ollama.has_named_sources:  content_raw += 8
        if ollama.has_statistics:     content_raw += 5
        if ollama.has_expert_quotes:  content_raw += 8
        if ollama.language_quality == "professional": content_raw += 5
        content_score = round(max(0, min(content_raw, 100)), 1)
        content_summary = (
            f"{len(ollama.bias_indicators)} bias, "
            f"{len(ollama.misleading_patterns)} misleading, "
            f"{len(ollama.clickbait_elements)} clickbait, "
            f"{len(ollama.irrelevant_facts)} irrelevant fact(s)"
        )
        if ad_prof.total_ad_slots > 0:
            content_summary += f", {ad_prof.total_ad_slots} ads"

        # ── Dimension 3: Source trust ───────────────────────────────────────
        domain = (article.domain or "").lower().replace("www.", "")
        if any(t in domain for t in ["reuters.com", "apnews.com", "bbc.com",
                                      "bbc.co.uk", "nature.com", "nasa.gov",
                                      "cdc.gov", "nih.gov", "who.int"]):
            source_raw = 95
        elif any(t in domain for t in ["theguardian.com", "nytimes.com",
                                        "washingtonpost.com", "economist.com",
                                        "npr.org", "bloomberg.com", "wsj.com"]):
            source_raw = 82
        elif any(t in domain for t in KNOWN_UNRELIABLE):
            source_raw = 5
        elif domain.endswith(".gov") or domain.endswith(".edu"):
            source_raw = 88
        elif domain.endswith(".org"):
            source_raw = 60
        elif domain in ("raw_input", "", "unknown"):
            source_raw = 45  # neutral for unknown
        else:
            source_raw = 50
        # HTTPS bonus
        if article.uses_https:
            source_raw = min(source_raw + 5, 100)
        source_score = round(float(source_raw), 1)

        # ── Dimension 4: Language / sensationalism ─────────────────────────
        emotional_count = len(ollama.emotional_phrases)
        tone_penalty = {
            "fear": 20, "anger": 18, "sensational": 22,
            "promotional": 10, "positive": 0, "neutral": 0
        }.get(ollama.content_tone, 0)
        language_raw = 100 - min(emotional_count * 8, 40) - tone_penalty
        language_score = round(max(0, min(language_raw, 100)), 1)

        # ── Dimension 5: Metadata ──────────────────────────────────────────
        meta_raw = 50  # baseline for unknown
        if article.authors:       meta_raw += 20
        if article.publish_date:  meta_raw += 15
        if ollama.has_named_sources: meta_raw += 15
        metadata_score = round(min(meta_raw, 100), 1)

        # ── Weighted overall ───────────────────────────────────────────────
        overall = round(
            corr_score    * self.WEIGHTS["corroboration"] +
            content_score * self.WEIGHTS["content"] +
            source_score  * self.WEIGHTS["source_trust"] +
            language_score * self.WEIGHTS["language"] +
            metadata_score * self.WEIGHTS["metadata"],
            1
        )
        overall = max(0.0, min(100.0, overall))

        # Hard overrides
        if any(t in domain for t in KNOWN_UNRELIABLE):
            overall = min(overall, 18.0)
        if corr.tier1_count == 0 and corr.tier2_count == 0 and len(ollama.misleading_patterns) >= 2:
            overall = min(overall, 32.0)

        # ── Ratings and verdict ────────────────────────────────────────────
        if overall >= 75: rating = "HIGH";       verdict = "REAL"
        elif overall >= 55: rating = "MODERATE"; verdict = "LIKELY REAL"
        elif overall >= 35: rating = "LOW";      verdict = "LIKELY FAKE"
        else:               rating = "UNRELIABLE"; verdict = "FAKE"

        SUMMARIES = {
            "REAL":        "This article is credible and authentic. Multiple trusted news outlets independently corroborate the story, and the content quality is high.",
            "LIKELY REAL": "This article is mostly credible with some minor concerns — limited corroboration, slight sensationalism, or unverified secondary claims.",
            "LIKELY FAKE": "This article shows multiple credibility red flags — poor corroboration from trusted sources, biased language, or misleading patterns detected.",
            "FAKE":        "This article is highly likely to be fake or misinformation. It failed critical checks: no trusted sources cover the story, and the content shows signs of deliberate manipulation.",
        }

        # ── Build dimension list ───────────────────────────────────────────
        dims = [
            DimensionScore(name="Corroboration",  score=corr_score,    weight=0.35, contribution=round(corr_score*0.35,1),    summary=corr.verdict_label),
            DimensionScore(name="Content Quality",score=content_score,  weight=0.25, contribution=round(content_score*0.25,1),  summary=content_summary),
            DimensionScore(name="Source Trust",   score=source_score,   weight=0.20, contribution=round(source_score*0.20,1),   summary=f"Domain: {domain or 'unknown'}"),
            DimensionScore(name="Language",       score=language_score, weight=0.10, contribution=round(language_score*0.10,1), summary=f"Tone: {ollama.content_tone} | {emotional_count} emotional phrase(s)"),
            DimensionScore(name="Metadata",       score=metadata_score, weight=0.10, contribution=round(metadata_score*0.10,1), summary=f"Author: {'yes' if article.authors else 'no'} | Date: {'yes' if article.publish_date else 'no'}"),
        ]

        # ── Red flags and positive signals ────────────────────────────────
        red_flags    = list(llm_reasoning.get("red_flags", []))
        pos_signals  = list(llm_reasoning.get("positive_signals", []))

        # Auto red flags
        if corr.trusted_sources_count == 0:
            red_flags.insert(0, "No trusted news outlet found covering this story on the internet")
        if len(ollama.misleading_patterns) >= 2:
            red_flags.append(f"Misleading language patterns detected: {', '.join(ollama.misleading_patterns[:2])}")
        if len(ollama.clickbait_elements) >= 2:
            red_flags.append(f"Clickbait techniques found: {', '.join(ollama.clickbait_elements[:2])}")
        if len(ollama.irrelevant_facts) >= 2:
            red_flags.append(
                f"{len(ollama.irrelevant_facts)} off-context fact(s) detected — article contains "
                f"statements unrelated to its core topic (padding/filler content)"
            )
        if ad_prof.has_clickbait_ads:
            networks_str = ", ".join(ad_prof.clickbait_networks_found)
            red_flags.append(f"Low-tier 'chumbox' ad networks detected ({networks_str}) — common on clickbait sites")
        if ad_prof.ad_density > 1.5:
            red_flags.append(f"Highly aggressive ad density ({ad_prof.ad_density:.1f} ads per 100 words)")

        # Auto positive signals
        if corr.tier1_count >= 2:
            pos_signals.insert(0, f"{corr.tier1_count} top-tier outlets (Reuters/BBC-level) independently reporting the same story")
        if ollama.has_named_sources:
            pos_signals.append("Article cites named sources or institutions")
        if ollama.has_expert_quotes:
            pos_signals.append("Article includes direct quotes from named experts")

        return CredibilityScorecard(
            url=article.url,
            title=article.title,
            domain=article.domain,
            publisher=article.publisher,
            authors=article.authors,
            publish_date=article.publish_date,
            overall_score=overall,
            credibility_rating=rating,
            verdict=verdict,
            verdict_summary=SUMMARIES[verdict],
            dimensions=dims,
            ad_profile=ad_prof,
            article_context=ollama.article_context,
            relevant_facts=ollama.relevant_facts,
            irrelevant_facts=ollama.irrelevant_facts,
            main_claims=ollama.main_claims,
            emotional_phrases=ollama.emotional_phrases,
            clickbait_elements=ollama.clickbait_elements,
            bias_indicators=ollama.bias_indicators,
            misleading_patterns=ollama.misleading_patterns,
            content_tone=ollama.content_tone,
            corroboration=corr,
            red_flags=red_flags[:6],
            positive_signals=pos_signals[:6],
        )
