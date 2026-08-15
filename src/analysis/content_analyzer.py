import re
from typing import List, Dict
from src.schemas.article_schema import ContentAnalysis, ExtractedArticle

class ContentAnalyzer:
    # One-sided/absolutist language → bias
    BIAS_PHRASES = [
        r"\balways\b", r"\bnever\b", r"\ball\b.{0,10}\b(agree|know|believe|say)\b",
        r"\beveryone knows\b", r"\bnobody (believes|thinks|says)\b",
        r"\bonly\b.{0,15}\bpeople\b", r"\bthe left\b", r"\bthe right\b",
        r"\bliberal media\b", r"\bfake news\b", r"\bdeep state\b",
        r"\bclearly\b.{0,20}\b(wrong|bad|evil|corrupt)\b",
        r"\bproved (once and for all)\b", r"\bundeniably\b"
    ]

    # Misleading info patterns
    MISLEADING_PATTERNS = [
        r"\bscientists? (baffled|shocked|stunned)\b",
        r"\bdoctors? (hate|don't want you)\b",
        r"\bgovernment (hiding|concealing|covering up)\b",
        r"\bthey don't want you to know\b",
        r"\bsecret (cure|remedy|trick|method)\b",
        r"\b100% (proven|guaranteed|effective)\b",
        r"\bno side effects\b",
        r"\bmiracle\b.{0,20}\b(cure|solution|pill)\b",
        r"\bstudy proves?\b.{0,30}\bwithout doubt\b",
        r"\bunveiled: the truth\b"
    ]

    # Emotional body language
    EMOTION_VOCAB = [
        "shocking", "horrifying", "devastating", "panic", "furious", "outrage",
        "scandal", "explosive", "terrifying", "chaotic", "unbelievable", "disgusting",
        "dangerous", "alarming", "catastrophic", "urgent", "deadly"
    ]

    def analyze(self, article: ExtractedArticle) -> ContentAnalysis:
        text = article.text or ""
        text_lower = text.lower()
        words = text_lower.split()
        word_count = max(len(words), 1)

        # Bias detection
        bias_hits = []
        for pattern in self.BIAS_PHRASES:
            if re.search(pattern, text_lower):
                bias_hits.append(pattern.replace(r"\b", "").strip())
        bias_score = round(min(len(bias_hits) / 5.0, 1.0), 3)

        # Misleading info detection
        misleading_hits = []
        for pattern in self.MISLEADING_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                misleading_hits.append(match.group(0))
        misleading_score = round(min(len(misleading_hits) / 4.0, 1.0), 3)

        # Emotional body language score
        emotional_hits = [w for w in words if w in self.EMOTION_VOCAB]
        emotional_body_score = round(min(len(emotional_hits) / (word_count / 50.0 + 1.0) * 0.5, 1.0), 3)

        # Emotion breakdown (reuse simplified counts)
        emotion_category_breakdown = {
            "fear": round(sum(1 for w in words if w in ["panic", "deadly", "catastrophic", "dangerous", "alarming"]) / (word_count / 100.0 + 1), 3),
            "anger": round(sum(1 for w in words if w in ["outrage", "furious", "scandal", "disgusting"]) / (word_count / 100.0 + 1), 3),
            "disgust": round(sum(1 for w in words if w in ["horrifying", "disgusting", "revolting"]) / (word_count / 100.0 + 1), 3),
            "hype": round(sum(1 for w in words if w in ["unbelievable", "shocking", "explosive", "terrifying"]) / (word_count / 100.0 + 1), 3),
        }

        return ContentAnalysis(
            bias_score=bias_score,
            misleading_info_score=misleading_score,
            emotional_body_score=emotional_body_score,
            bias_indicators=[p.replace(r"\b", "").replace("\\b", "").strip() for p in bias_hits[:5]],
            misleading_indicators=misleading_hits[:5],
            emotion_category_breakdown=emotion_category_breakdown
        )
