import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from src.schemas.article_schema import AdAnalysis

class AdAnalyzer:
    AD_CLASS_PATTERNS = [
        r'ad[-_]', r'\bads\b', r'banner', r'sponsor', r'google-ad',
        r'outbrain', r'taboola', r'advertisement', r'promo', r'promoted'
    ]

    AD_CLAIM_MARKERS = [
        "100%", "guaranteed", "proven", "miracle", "secret", "best ever",
        "lose weight", "earn money", "free", "limited time", "act now",
        "exclusive offer", "no risk", "click here"
    ]

    TRUSTED_ARTICLE_TOPICS = []  # populated dynamically

    def analyze_from_html(self, html_content: str, article_text: str, article_keywords: List[str] = None) -> AdAnalysis:
        """Full analysis from raw HTML — used when URL is available."""
        if not html_content:
            return self._neutral_baseline()

        soup = BeautifulSoup(html_content, 'html.parser')
        ad_elements = self._find_ad_elements(soup)
        num_ads = len(ad_elements)

        ad_types: List[str] = []
        ad_texts: List[str] = []
        ad_claims: List[str] = []

        for el in ad_elements:
            # Type classification
            tag = el.name.lower()
            if tag == 'iframe':
                ad_types.append("video/embed")
            elif tag == 'img':
                ad_types.append("image banner")
            elif el.find('video'):
                ad_types.append("video ad")
            else:
                ad_types.append("inline/text ad")

            # Extract text content from ad element
            el_text = el.get_text(separator=" ").lower().strip()
            if el_text:
                ad_texts.append(el_text)

            # Check for misleading claims in ads
            for marker in self.AD_CLAIM_MARKERS:
                if marker in el_text:
                    ad_claims.append(f"Ad claim: '{marker}' found")
                    break

        # Ad-to-topic relevance: keyword overlap between article keywords and ad text
        article_kw = set(article_keywords or article_text.lower().split()[:50])
        all_ad_text = " ".join(ad_texts).lower()
        ad_words = set(all_ad_text.split())
        overlap = article_kw.intersection(ad_words)
        topic_relevance = round(min(len(overlap) / (len(article_kw) + 1), 1.0), 3) if article_kw else 0.5

        # Ad ratio (estimated ad char coverage vs body text)
        text_len = max(len(article_text), 1)
        ad_text_len = sum(len(t) for t in ad_texts)
        ad_ratio = round(min(ad_text_len / text_len, 1.0), 3)

        # Penalty score
        penalty = self._compute_penalty(num_ads, ad_ratio, len(ad_claims))

        return AdAnalysis(
            num_ads=num_ads,
            ad_ratio=ad_ratio,
            ad_types_found=list(set(ad_types)),
            ad_topic_relevance=topic_relevance,
            claims_in_ads=len(ad_claims) > 0,
            ad_claim_examples=ad_claims[:3],
            ad_penalty_score=penalty
        )

    def analyze_from_article(self, article) -> AdAnalysis:
        """Lightweight analysis from ExtractedArticle metadata — no raw HTML required."""
        if article.ad_details:
            return self.analyze_from_html("", article.text)
        # Raw text mode — neutral baseline
        return self._neutral_baseline()

    def _find_ad_elements(self, soup: BeautifulSoup) -> list:
        found = list(soup.find_all('iframe'))
        for pattern in self.AD_CLASS_PATTERNS:
            compiled = re.compile(pattern, re.IGNORECASE)
            found += soup.find_all(class_=compiled)
            found += soup.find_all(id=compiled)
        return found

    def _compute_penalty(self, num_ads: int, ad_ratio: float, claim_count: int) -> float:
        penalty = 0.0
        if num_ads > 10:
            penalty += 0.4
        elif num_ads > 5:
            penalty += 0.25
        elif num_ads > 2:
            penalty += 0.1
        if ad_ratio > 0.3:
            penalty += 0.3
        elif ad_ratio > 0.1:
            penalty += 0.1
        if claim_count > 0:
            penalty += min(claim_count * 0.1, 0.3)
        return round(min(penalty, 1.0), 3)

    def _neutral_baseline(self) -> AdAnalysis:
        return AdAnalysis(
            num_ads=0, ad_ratio=0.0,
            ad_types_found=[], ad_topic_relevance=0.5,
            claims_in_ads=False, ad_claim_examples=[],
            ad_penalty_score=0.0
        )
