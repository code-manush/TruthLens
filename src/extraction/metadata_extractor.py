import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup

from src.schemas.article_schema import ExtractedArticle

class MetadataExtractor:
    AD_CLASS_OR_ID_PATTERNS = [
        r'ad[-_]', r'ads[-_]', r'banner', r'sponsor', r'google-ad',
        r'outbrain', r'taboola', r'advertisement', r'promo', r'promoted'
    ]

    def analyze_ad_density(self, html_content: str, text_length: int) -> Dict[str, Any]:
        if not html_content or text_length == 0:
            return {"num_ads_estimated": 0, "ad_ratio": 0.0}

        soup = BeautifulSoup(html_content, 'html.parser')
        ad_count = len(soup.find_all('iframe'))

        for pattern in self.AD_CLASS_OR_ID_PATTERNS:
            compiled = re.compile(pattern, re.IGNORECASE)
            ad_count += len(soup.find_all(class_=compiled))
            ad_count += len(soup.find_all(id=compiled))

        word_count = max(text_length // 5, 1)
        ad_ratio = min(round(ad_count / (word_count / 500.0), 3), 1.0)
        return {"num_ads_estimated": ad_count, "ad_ratio": ad_ratio}

    def extract_outbound_links(self, html_content: str, base_domain: str = "") -> List[str]:
        if not html_content:
            return []
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and base_domain not in href:
                links.append(href)
        return list(set(links))[:20]  # cap at 20 unique outbound links

    def enrich_metadata(self, article: ExtractedArticle, html_content: str = "") -> ExtractedArticle:
        ad_metrics = self.analyze_ad_density(html_content, len(article.text))
        article.num_ads_estimated = ad_metrics["num_ads_estimated"]
        article.ad_ratio = ad_metrics["ad_ratio"]

        # Extract outbound links
        if html_content:
            article.outbound_links = self.extract_outbound_links(html_content, article.domain or "")

        # HTTPS detection
        if article.url:
            article.uses_https = article.url.startswith("https://")

        return article
