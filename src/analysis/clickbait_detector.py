import re
import unicodedata
from typing import List, Optional
from src.schemas.article_schema import TitleAnalysis
from src.llm.llm_analyzer import LLMAnalyzer

class ClickbaitDetector:
    CLICKBAIT_KEYWORDS = [
        "shocking", "you won't believe", "mind-blowing", "secret", "incredible",
        "miracle", "what happened next", "top 10", "reasons why", "will change your life",
        "exposed", "breaking", "urgent", "warning", "bombshell", "jaw-dropping",
        "unbelievable", "stunning", "outrageous", "exclusive", "they don't want you to know"
    ]

    EMOTIONAL_TRIGGER_WORDS = {
        "fear":    ["danger", "threat", "crisis", "attack", "collapse", "terrifying",
                    "catastrophic", "deadly", "emergency", "alarm", "panic", "disaster"],
        "anger":   ["outrage", "betrayal", "corrupt", "disgusting", "shameful", "furious",
                    "absurd", "scandalous", "lie", "lied", "deception", "manipulation"],
        "disgust": ["horrifying", "vile", "repulsive", "nauseating", "revolting",
                    "filthy", "sickening", "atrocious"],
        "hype":    ["amazing", "incredible", "unbelievable", "phenomenal", "revolutionary",
                    "game-changer", "epic", "legendary", "mind-blowing"]
    }

    def __init__(self, llm_analyzer: Optional[LLMAnalyzer] = None):
        self.llm_analyzer = llm_analyzer or LLMAnalyzer()

    def _count_emojis(self, text: str) -> int:
        return sum(1 for c in text if unicodedata.category(c) in ("So", "Sm") or ord(c) > 0x1F300)

    def _find_emotional_words(self, title: str) -> List[str]:
        title_lower = title.lower()
        found = []
        for category, words in self.EMOTIONAL_TRIGGER_WORDS.items():
            for w in words:
                if w in title_lower:
                    found.append(w)
        return found

    def analyze_title(self, title: str, text: str = "") -> TitleAnalysis:
        title_lower = title.lower()
        score = 0.0
        reasons = []

        # Clickbait keyword detection
        matched_kw = [kw for kw in self.CLICKBAIT_KEYWORDS if kw in title_lower]
        if matched_kw:
            score += 0.35
            reasons.append(f"Clickbait phrase(s) detected: {', '.join(matched_kw)}")

        # ALL CAPS ratio
        alpha_chars = [c for c in title if c.isalpha()]
        if alpha_chars and (sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)) > 0.4:
            score += 0.25
            reasons.append("Excessive uppercase lettering in headline")

        # Punctuation stacking
        if re.search(r'[!?]{1,}', title):
            score += 0.15
            reasons.append("Exclamation/question marks in title")

        # Numbered list bait
        if re.search(r'\b\d+\s+(reasons?|things?|ways?|facts?|tips?|tricks?)\b', title_lower):
            score += 0.15
            reasons.append("Numbered list clickbait pattern")

        # Curiosity gap phrasing
        if re.search(r'\b(what|who|why|how).{0,30}(next|shocked|surprised|happened)\b', title_lower):
            score += 0.15
            reasons.append("Curiosity gap phrasing detected")

        # Emoji detection
        emoji_count = self._count_emojis(title)
        if emoji_count > 0:
            score += min(emoji_count * 0.05, 0.2)
            reasons.append(f"{emoji_count} emoji(s) found in title")

        # Emotional words
        emotional_words = self._find_emotional_words(title)
        if emotional_words:
            score += min(len(emotional_words) * 0.1, 0.25)
            reasons.append(f"Emotional trigger words: {', '.join(emotional_words)}")

        # Blend with LLM
        llm_res = self.llm_analyzer.analyze_clickbait(title, text[:500])
        llm_score = llm_res.get("clickbait_score", 0.3)
        llm_reasons = llm_res.get("reasons", [])

        final_score = round(min((score * 0.6) + (llm_score * 0.4), 1.0), 3)
        combined_reasons = list(set(reasons + llm_reasons))

        return TitleAnalysis(
            clickbait_score=final_score,
            emoji_count=emoji_count,
            emotional_word_count=len(emotional_words),
            emotional_words_found=emotional_words,
            clickbait_reasons=combined_reasons
        )

    # backward-compatible alias
    def analyze(self, article) -> TitleAnalysis:
        return self.analyze_title(article.title, article.text)
