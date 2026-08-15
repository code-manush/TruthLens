"""
ArticleExtractor: Extracts clean article text from a URL.

Strategy:
  1. Resolve redirects and find canonical URL (handles MSN, Google News, etc.)
  2. Try trafilatura (best at clean content extraction)
  3. Try newspaper3k (fallback)
  4. Try BeautifulSoup (last resort)
"""

import urllib.parse
import logging
import re
from typing import Optional, Tuple

import trafilatura
import requests
from bs4 import BeautifulSoup

try:
    from newspaper import Article as NewspaperArticle
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

from src.schemas.article_schema import ArticleInput, ArticleExtraction, AdProfile

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# News aggregators that redirect to the actual article
AGGREGATOR_DOMAINS = {"msn.com", "news.google.com", "flipboard.com", "feedly.com"}


class ArticleExtractor:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    # ── Public entry point ────────────────────────────────────────────────

    def extract(self, article_input: ArticleInput) -> ArticleExtraction:
        if article_input.url:
            return self.extract_from_url(article_input.url, publisher=article_input.publisher)
        elif article_input.raw_text:
            return self.extract_from_raw_text(
                article_input.raw_text,
                title=article_input.title,
                publisher=article_input.publisher
            )
        raise ValueError("ArticleInput must provide either a url or raw_text.")

    # ── URL extraction ────────────────────────────────────────────────────

    def extract_from_url(self, url: str, publisher: Optional[str] = None) -> ArticleExtraction:
        # Step 1: Resolve the real URL (follow redirects, handle aggregators)
        resolved_url = self._resolve_url(url)
        if resolved_url != url:
            logger.info(f"  Resolved: {url[:60]} -> {resolved_url[:60]}")

        domain = urllib.parse.urlparse(resolved_url).netloc.lower().replace("www.", "")
        uses_https = resolved_url.startswith("https://")

        # Step 2: Try trafilatura
        # We need the raw HTML for ad analysis before trafilatura strips it
        raw_html = ""
        try:
            resp = requests.get(resolved_url, headers=HEADERS, timeout=self.timeout)
            resp.raise_for_status()
            raw_html = resp.text
        except Exception as e:
            logger.warning(f"  Failed to fetch raw HTML for ad analysis: {e}")

        title, text, authors, publish_date = self._try_trafilatura_html(raw_html, resolved_url)

        # Step 3: Fallback to newspaper3k
        if not text and NEWSPAPER_AVAILABLE:
            logger.info(f"  trafilatura empty, trying newspaper3k...")
            title, text, authors, publish_date = self._try_newspaper(resolved_url, title)

        # Step 4: Fallback to BeautifulSoup
        if not text:
            logger.info(f"  newspaper3k empty, trying BeautifulSoup...")
            title, text = self._try_beautifulsoup(resolved_url, title)

        # Calculate word count first, then use it in checks
        word_count = len(text.split()) if text else 0

        # Step 5: Analyze Ads on the raw HTML
        ad_profile = self._analyze_ads(raw_html, word_count)
        if ad_profile.total_ad_slots > 0:
            logger.info(f"  Ads detected: {ad_profile.total_ad_slots} slots | Density: {ad_profile.ad_density:.2f} per 100 words")
            if ad_profile.has_clickbait_ads:
                logger.info(f"  Clickbait networks found: {', '.join(ad_profile.clickbait_networks_found)}")

        # Check if this is a JS-only site that returned no usable content
        JS_ONLY_DOMAINS = {"msn.com", "news.google.com", "flipboard.com"}
        if word_count < 30 and any(js in domain for js in JS_ONLY_DOMAINS):
            raise ValueError(
                f"'{domain}' renders content with JavaScript — Python scrapers cannot read it.\n\n"
                f"  MSN, Google News, and Flipboard are NEWS AGGREGATORS that link to original articles.\n"
                f"  Please copy the URL of the ORIGINAL ARTICLE from the source publisher instead.\n\n"
                f"  TIP: On MSN, click the article, then look for 'View Original' or check the\n"
                f"  address bar after the page fully loads — it often redirects to the real source."
            )

        return ArticleExtraction(
            url=resolved_url,
            title=title or "Untitled Article",
            text=text or "",
            authors=authors,
            publish_date=publish_date,
            domain=domain,
            publisher=publisher or domain,
            uses_https=uses_https,
            word_count=word_count,
            ad_profile=ad_profile,
        )


    # ── Raw text ──────────────────────────────────────────────────────────

    def extract_from_raw_text(
        self,
        raw_text: str,
        title: Optional[str] = None,
        publisher: Optional[str] = None
    ) -> ArticleExtraction:
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        if not title and lines:
            title = lines[0]
            raw_text = "\n\n".join(lines[1:]) if len(lines) > 1 else raw_text
        return ArticleExtraction(
            url=None,
            title=title or "Untitled Article",
            text=raw_text,
            domain="raw_input",
            publisher=publisher,
            uses_https=False,
            word_count=len(raw_text.split()),
        )

    # ── URL resolution (handles MSN / aggregators) ────────────────────────

    def _resolve_url(self, url: str) -> str:
        """
        Follow redirects to get the final destination URL.
        For MSN, also tries to extract the canonical source URL from the page HTML.
        """
        try:
            resp = requests.get(url, headers=HEADERS, timeout=self.timeout,
                                allow_redirects=True)
            final_url = resp.url

            # Check if we landed on an aggregator — try to find the real source
            final_domain = urllib.parse.urlparse(final_url).netloc.lower().replace("www.", "")
            if any(agg in final_domain for agg in AGGREGATOR_DOMAINS):
                real_url = self._extract_canonical_url(resp.text, final_url)
                if real_url and real_url != final_url:
                    logger.info(f"  Aggregator detected ({final_domain}). Real source: {real_url[:70]}")
                    return real_url

            return final_url
        except Exception as e:
            logger.warning(f"  URL resolution failed: {e}. Using original URL.")
            return url

    def _extract_canonical_url(self, html: str, base_url: str) -> Optional[str]:
        """
        Extract the real source URL from an aggregator page.
        Looks for: og:url, canonical link, or redirects embedded in the page.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # 1. og:url meta tag (most reliable)
            og_url = soup.find("meta", property="og:url")
            if og_url and og_url.get("content"):
                candidate = og_url["content"].strip()
                if candidate.startswith("http") and "msn.com" not in candidate:
                    return candidate

            # 2. canonical link tag
            canonical = soup.find("link", rel="canonical")
            if canonical and canonical.get("href"):
                candidate = canonical["href"].strip()
                if candidate.startswith("http") and "msn.com" not in candidate:
                    return candidate

            # 3. MSN-specific: data-original-url attribute in article body
            for tag in soup.find_all(attrs={"data-original-url": True}):
                candidate = tag["data-original-url"]
                if candidate.startswith("http"):
                    return candidate

            # 4. Look for an outbound link that looks like the source article
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and "msn.com" not in href:
                    # Match links that look like article URLs (not ads/nav)
                    if re.search(r"/(article|news|story|post|world|tech|business)/", href):
                        return href

        except Exception as e:
            logger.warning(f"  Canonical URL extraction error: {e}")

        return None

    # ── Extraction backends ───────────────────────────────────────────────

    def _try_trafilatura_html(self, html: str, url: str) -> Tuple:
        if not html:
            # Fallback to fetching it directly via trafilatura if requests failed
            return self._try_trafilatura(url)
        try:
            metadata = trafilatura.extract_metadata(html)
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                favor_recall=True,
                no_fallback=False,
            )
            title = metadata.title if metadata else None
            authors = []
            if metadata and metadata.author:
                authors = [a.strip() for a in metadata.author.split(",")]
            publish_date = metadata.date if metadata else None
            return title, text, authors, publish_date
        except Exception as e:
            logger.warning(f"  trafilatura (HTML) failed: {e}")
            return None, None, [], None

    def _try_trafilatura(self, url: str) -> Tuple:
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None, None, [], None
            return self._try_trafilatura_html(downloaded, url)
        except Exception as e:
            logger.warning(f"  trafilatura fetch failed: {e}")
            return None, None, [], None

    def _try_newspaper(self, url: str, fallback_title: Optional[str] = None) -> Tuple:
        try:
            art = NewspaperArticle(url)
            art.download()
            art.parse()
            title = art.title or fallback_title
            text = art.text
            authors = art.authors
            publish_date = art.publish_date
            return title, text, authors, publish_date
        except Exception as e:
            logger.warning(f"  newspaper3k failed: {e}")
            return fallback_title, None, [], None

    def _try_beautifulsoup(self, url: str, fallback_title: Optional[str] = None) -> Tuple:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            title = fallback_title
            if not title:
                # Try og:title first, then <title>
                og_title = soup.find("meta", property="og:title")
                if og_title and og_title.get("content"):
                    title = og_title["content"].strip()
                elif soup.title:
                    title = soup.title.string.strip()

            # Extract paragraphs from main content areas first
            content_tags = soup.find_all(
                ["article", "main", "div"],
                class_=re.compile(r"(article|content|story|body|text)", re.I)
            )
            paragraphs = []
            if content_tags:
                for tag in content_tags[:2]:
                    paragraphs += [p.get_text(separator=" ").strip()
                                   for p in tag.find_all("p") if p.get_text().strip()]
            if not paragraphs:
                paragraphs = [p.get_text(separator=" ").strip()
                              for p in soup.find_all("p") if p.get_text().strip()]

            text = "\n\n".join(paragraphs)
            return title or "Untitled", text
        except Exception as e:
            logger.warning(f"  BeautifulSoup fallback failed: {e}")
            return fallback_title or "Untitled", ""

    # ── Ad Analysis ───────────────────────────────────────────────────────

    def _analyze_ads(self, html: str, word_count: int) -> AdProfile:
        """
        Parses raw HTML to detect standard ad slots and clickbait networks.
        """
        if not html:
            return AdProfile()

        soup = BeautifulSoup(html, "html.parser")
        ad_count = 0
        clickbait_networks = set()

        # 1. Standard ad slots (Google AdSense, generic ad containers)
        ad_count += len(soup.find_all("ins", class_="adsbygoogle"))
        ad_count += len(soup.find_all(class_=re.compile(r"(ad-container|advertisement|ad-slot|ad_unit)", re.I)))
        ad_count += len(soup.find_all(id=re.compile(r"(ad-container|advertisement|ad-slot|ad_unit)", re.I)))

        # 2. Clickbait / Chumbox networks (scripts and iframes)
        clickbait_patterns = {
            "taboola": re.compile(r"taboola\.com", re.I),
            "outbrain": re.compile(r"outbrain\.com", re.I),
            "mgid": re.compile(r"mgid\.com", re.I),
            "revcontent": re.compile(r"revcontent\.com", re.I)
        }

        for script in soup.find_all("script", src=True):
            src = script["src"]
            for network, pattern in clickbait_patterns.items():
                if pattern.search(src):
                    clickbait_networks.add(network)
                    ad_count += 1

        for iframe in soup.find_all("iframe", src=True):
            src = iframe["src"]
            for network, pattern in clickbait_patterns.items():
                if pattern.search(src):
                    clickbait_networks.add(network)
                    ad_count += 1
        
        # Deduplicate network list
        networks_list = list(clickbait_networks)
        
        # Calculate ad density (ads per 100 words)
        ad_density = 0.0
        if word_count > 0:
            ad_density = round((ad_count / word_count) * 100, 2)
            
        return AdProfile(
            total_ad_slots=ad_count,
            has_clickbait_ads=len(networks_list) > 0,
            clickbait_networks_found=networks_list,
            ad_density=ad_density
        )
