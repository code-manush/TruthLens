from src.schemas.article_schema import ExtractedArticle

class TopicRelevanceAnalyzer:
    def analyze(self, article: ExtractedArticle) -> float:
        """Analyze title to body text term overlap score (0.0 to 1.0)."""
        if not article.title or not article.text:
            return 0.5

        title_words = set(re.findall(r'\w+', article.title.lower()))
        text_words = set(re.findall(r'\w+', article.text.lower()))

        # Remove short stopwords
        title_keywords = {w for w in title_words if len(w) > 3}
        if not title_keywords:
            return 1.0

        overlap = title_keywords.intersection(text_words)
        relevance_ratio = len(overlap) / len(title_keywords)
        return round(min(relevance_ratio, 1.0), 2)

import re
