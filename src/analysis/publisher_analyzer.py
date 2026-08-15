import urllib.parse
from typing import Optional, List
from src.schemas.article_schema import PublisherAnalysis

class PublisherAnalyzer:
    HIGH_TRUST_EXTENSIONS = [".gov", ".edu", ".mil"]
    MED_TRUST_EXTENSIONS  = [".org", ".ac", ".int"]
    LOW_TRUST_EXTENSIONS  = [".xyz", ".click", ".info", ".biz", ".top", ".online", ".site"]

    KNOWN_HIGH_CREDIBILITY = [
        "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nytimes.com",
        "washingtonpost.com", "theguardian.com", "nature.com", "sciencedirect.com",
        "who.int", "cdc.gov", "nasa.gov", "nih.gov", "economist.com"
    ]

    KNOWN_UNRELIABLE = [
        "infowars.com", "naturalnews.com", "beforeitsnews.com", "worldnewsdailyreport.com",
        "thelastlineofdefense.org", "newslo.com", "theonion.com", "clickhole.com",
        "empirenews.net", "huzlers.com"
    ]

    def analyze(self, domain: Optional[str], uses_https: bool = False,
                outbound_links: Optional[List[str]] = None, publisher_name: Optional[str] = None) -> PublisherAnalysis:
        signals = []
        score = 0.5  # neutral baseline

        raw_domain = (domain or "").lower().replace("www.", "")

        # HTTPS check
        if uses_https:
            score += 0.05
            signals.append("✓ Uses HTTPS (secure)")
        else:
            score -= 0.1
            signals.append("✗ Does not use HTTPS")

        # Known high-credibility domain
        if any(trusted in raw_domain for trusted in self.KNOWN_HIGH_CREDIBILITY):
            score += 0.4
            signals.append(f"✓ Known high-credibility domain: {raw_domain}")
        elif any(bad in raw_domain for bad in self.KNOWN_UNRELIABLE):
            score -= 0.45
            signals.append(f"✗ Known unreliable/satire/misinformation domain: {raw_domain}")
            known_unreliable = True
        else:
            known_unreliable = False

        # Domain extension trust
        extension_trust = 0.5
        for ext in self.HIGH_TRUST_EXTENSIONS:
            if raw_domain.endswith(ext):
                extension_trust = 0.95
                score += 0.15
                signals.append(f"✓ High-trust domain extension: {ext}")
                break
        for ext in self.MED_TRUST_EXTENSIONS:
            if raw_domain.endswith(ext):
                extension_trust = 0.7
                score += 0.05
                signals.append(f"✓ Medium-trust domain extension: {ext}")
                break
        for ext in self.LOW_TRUST_EXTENSIONS:
            if raw_domain.endswith(ext):
                extension_trust = 0.2
                score -= 0.15
                signals.append(f"✗ Low-trust domain extension: {ext}")
                break

        # Outbound link quality
        outbound_link_quality = self._evaluate_outbound_links(outbound_links or [])
        if outbound_link_quality > 0.7:
            score += 0.05
            signals.append(f"✓ High-quality outbound links (score: {outbound_link_quality})")
        elif outbound_link_quality < 0.3:
            score -= 0.05
            signals.append(f"✗ Poor outbound link quality (score: {outbound_link_quality})")

        final_score = round(max(0.0, min(score, 1.0)), 3)

        return PublisherAnalysis(
            domain=raw_domain or publisher_name,
            uses_https=uses_https,
            extension_trust_score=extension_trust,
            outbound_link_quality=outbound_link_quality,
            known_unreliable=any(bad in raw_domain for bad in self.KNOWN_UNRELIABLE),
            publisher_credibility_score=final_score,
            signals=signals
        )

    def _evaluate_outbound_links(self, links: List[str]) -> float:
        if not links:
            return 0.5
        trusted_count = sum(
            1 for link in links
            if any(t in link for t in self.KNOWN_HIGH_CREDIBILITY + [".gov", ".edu"])
        )
        return round(trusted_count / len(links), 3)
