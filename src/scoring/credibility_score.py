"""
CredibilityScorer: Produces the final 0-100 score and REAL/FAKE verdict
across 7 dimensions: title, content, emotion, claims, ads, publisher,
and web corroboration (the most powerful new signal).
"""

from typing import Tuple, Dict
from src.schemas.article_schema import AnalysisResult, ExtractedArticle


class CredibilityScorer:
    # Weights must sum to 1.0
    WEIGHTS = {
        "title":           0.10,   # clickbait + emoji + emotional title
        "content":         0.20,   # bias + misleading info + emotional body
        "emotion":         0.08,   # sensationalism
        "claims":          0.17,   # claim verification via Tavily + Ollama
        "ads":             0.05,   # ad density + claims in ads
        "publisher":       0.15,   # domain trust, HTTPS, link quality
        "corroboration":   0.25,   # live web search — most impactful dimension
    }

    def calculate_score(
        self,
        article: ExtractedArticle,
        analysis: AnalysisResult,
    ) -> Tuple[float, str, str, str, Dict[str, float]]:
        """
        Returns:
          overall_score (0-100), credibility_rating, real_or_fake,
          summary_verdict, dimension_scores
        """

        # ── Dimension 1: Title ─────────────────────────────────────────────────
        title_score = round((1.0 - analysis.title_analysis.clickbait_score) * 100.0, 1)

        # ── Dimension 2: Content ───────────────────────────────────────────────
        content_penalty = (
            analysis.content_analysis.bias_score * 0.4 +
            analysis.content_analysis.misleading_info_score * 0.4 +
            analysis.content_analysis.emotional_body_score * 0.2
        )
        content_score = round((1.0 - content_penalty) * 100.0, 1)

        # ── Dimension 3: Emotion ───────────────────────────────────────────────
        emotion_score = round((1.0 - analysis.emotion.sensationalism_score) * 100.0, 1)

        # ── Dimension 4: Claim Verification ────────────────────────────────────
        if analysis.claims:
            supported = sum(1 for c in analysis.claims if c.verdict == "SUPPORTED")
            contradicted = sum(1 for c in analysis.claims if c.verdict == "CONTRADICTED")
            raw = (supported - contradicted * 0.5) / len(analysis.claims)
            claim_score = round(max(0.0, min(raw * 100.0, 100.0)), 1)
        else:
            claim_score = 55.0  # neutral baseline

        # ── Dimension 5: Ads ───────────────────────────────────────────────────
        ad_score = round((1.0 - analysis.ad_analysis.ad_penalty_score) * 100.0, 1)

        # ── Dimension 6: Publisher ─────────────────────────────────────────────
        publisher_score = round(analysis.publisher.publisher_credibility_score * 100.0, 1)

        # ── Dimension 7: Web Corroboration (Tavily) ────────────────────────────
        corroboration_score = round(analysis.authenticity.corroboration_score * 100.0, 1)

        dimension_scores = {
            "title":         title_score,
            "content":       content_score,
            "emotion":       emotion_score,
            "claims":        claim_score,
            "ads":           ad_score,
            "publisher":     publisher_score,
            "corroboration": corroboration_score,
        }

        # ── Weighted Overall Score ─────────────────────────────────────────────
        overall = round(
            title_score         * self.WEIGHTS["title"] +
            content_score       * self.WEIGHTS["content"] +
            emotion_score       * self.WEIGHTS["emotion"] +
            claim_score         * self.WEIGHTS["claims"] +
            ad_score            * self.WEIGHTS["ads"] +
            publisher_score     * self.WEIGHTS["publisher"] +
            corroboration_score * self.WEIGHTS["corroboration"],
            1
        )
        overall = max(0.0, min(100.0, overall))

        # ── Hard overrides ─────────────────────────────────────────────────────
        if analysis.publisher.known_unreliable:
            overall = min(overall, 22.0)
        # If corroboration is zero AND content is bad, enforce a cap
        if corroboration_score < 20.0 and content_score < 40.0:
            overall = min(overall, 35.0)

        # ── Ratings ────────────────────────────────────────────────────────────
        if overall >= 78:
            rating = "HIGH"
        elif overall >= 58:
            rating = "MODERATE"
        elif overall >= 38:
            rating = "LOW"
        else:
            rating = "UNRELIABLE"

        if overall >= 72:
            real_or_fake = "REAL"
        elif overall >= 52:
            real_or_fake = "LIKELY REAL"
        elif overall >= 35:
            real_or_fake = "LIKELY FAKE"
        else:
            real_or_fake = "FAKE"

        verdicts = {
            "REAL": (
                "The article is credible and authentic. Multiple trusted sources corroborate "
                "the story, the language is balanced, and claims are supported by evidence."
            ),
            "LIKELY REAL": (
                "The article is mostly credible with minor concerns — slight clickbait, "
                "limited corroboration, or a few unverified secondary claims."
            ),
            "LIKELY FAKE": (
                "The article shows multiple red flags: bias, misleading patterns, poor "
                "corroboration from trusted sources, or unreliable publisher signals."
            ),
            "FAKE": (
                "This article is highly likely to be fake or misinformation. Critical failures "
                "detected: known unreliable domain, blatant misleading patterns, or zero "
                "corroboration from any trusted news outlet."
            ),
        }
        summary_verdict = verdicts[real_or_fake]

        return overall, rating, real_or_fake, summary_verdict, dimension_scores
