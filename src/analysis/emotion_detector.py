from textblob import TextBlob
from typing import Dict
from src.schemas.article_schema import EmotionAnalysis, ExtractedArticle

class EmotionDetector:
    EMOTION_VOCAB: Dict[str, list] = {
        "fear":    ["danger", "threat", "crisis", "attack", "collapse", "terrifying",
                    "catastrophic", "deadly", "emergency", "alarm", "panic", "disaster",
                    "warn", "warning", "urgent", "shocking"],
        "anger":   ["outrage", "betrayal", "corrupt", "disgusting", "shameful", "furious",
                    "absurd", "scandalous", "lie", "lied", "deception", "manipulation",
                    "unfair", "injustice", "enraged", "offensive"],
        "disgust": ["horrifying", "vile", "repulsive", "nauseating", "revolting",
                    "filthy", "sickening", "atrocious", "hideous", "gruesome"],
        "positive":["amazing", "incredible", "phenomenal", "revolutionary",
                    "breakthrough", "inspiring", "wonderful", "hopeful", "success"]
    }

    def analyze(self, article: ExtractedArticle) -> EmotionAnalysis:
        text = article.text
        if not text:
            return EmotionAnalysis(
                polarity=0.0, subjectivity=0.0,
                sensationalism_score=0.0, dominant_tone="neutral",
                emotion_breakdown={}
            )

        blob = TextBlob(text)
        polarity    = round(blob.sentiment.polarity, 3)
        subjectivity = round(blob.sentiment.subjectivity, 3)

        # Emotion breakdown
        words = text.lower().split()
        word_count = max(len(words), 1)
        breakdown: Dict[str, float] = {}
        total_emotional = 0
        for category, vocab in self.EMOTION_VOCAB.items():
            hits = sum(1 for w in words if w in vocab)
            breakdown[category] = round(min(hits / (word_count / 100.0 + 1.0) * 0.5, 1.0), 3)
            total_emotional += hits

        # Sensationalism = weighted average of negative categories + subjectivity
        neg_score = (breakdown.get("fear", 0) + breakdown.get("anger", 0) + breakdown.get("disgust", 0)) / 3.0
        sensationalism_score = round(min((neg_score * 0.6) + (subjectivity * 0.4), 1.0), 3)

        # Dominant tone
        if max(breakdown.values(), default=0) == 0 and abs(polarity) < 0.2:
            dominant_tone = "neutral / objective"
        elif breakdown.get("fear", 0) == max(breakdown.values()):
            dominant_tone = "fear-driven"
        elif breakdown.get("anger", 0) == max(breakdown.values()):
            dominant_tone = "anger-driven / confrontational"
        elif breakdown.get("disgust", 0) == max(breakdown.values()):
            dominant_tone = "disgust / outrage"
        elif polarity > 0.3:
            dominant_tone = "strongly positive / promotional"
        elif polarity < -0.3:
            dominant_tone = "strongly negative"
        elif subjectivity > 0.6:
            dominant_tone = "highly subjective / opinionated"
        else:
            dominant_tone = "neutral / objective"

        return EmotionAnalysis(
            polarity=polarity,
            subjectivity=subjectivity,
            sensationalism_score=sensationalism_score,
            dominant_tone=dominant_tone,
            emotion_breakdown=breakdown
        )
