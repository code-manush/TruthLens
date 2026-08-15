"""
SourceEvaluator: Takes raw corroboration results from WebCorroborator
and produces a structured CorroborationResult with a final credibility
contribution score.
"""

import urllib.parse
from typing import List, Dict, Any

from src.verification.source_search import TRUSTED_DOMAINS


class SourceEvaluator:
    """
    Evaluates the quality of corroboration search results and returns a
    final corroboration credibility score plus a human-readable summary.
    """

    # Tier 1 — Premier wire services, flagship papers, official science/health agencies,
    # and top fact-checkers. Corroboration from any of these carries strong weight.
    TIER_1_DOMAINS = {
        # Wire services
        "reuters.com", "apnews.com", "afp.com", "bloomberg.com", "upi.com",
        "ansa.it", "dpa.com", "efe.com", "kyodonews.net", "yonhapnews.co.kr",
        # Top international newspapers
        "nytimes.com", "washingtonpost.com", "theguardian.com", "wsj.com",
        "ft.com", "economist.com", "bbc.com", "bbc.co.uk", "newyorker.com",
        "lemonde.fr", "spiegel.de", "thetimes.co.uk", "telegraph.co.uk",
        # Science / Health authorities
        "nature.com", "science.org", "nejm.org", "thelancet.com", "bmj.com",
        "cell.com", "pnas.org", "jamanetwork.com", "cochranelibrary.com",
        "who.int", "cdc.gov", "nih.gov", "fda.gov", "nasa.gov", "noaa.gov",
        "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
        # Top fact-checkers
        "snopes.com", "factcheck.org", "politifact.com", "fullfact.org",
        "africacheck.org", "boomlive.in", "altnews.in", "bellingcat.com",
        "icij.org", "poynter.org", "stopfake.org",
        # International organizations
        "un.org", "who.int", "unicef.org", "imf.org", "worldbank.org",
        "europa.eu", "nato.int", "oecd.org", "wto.org",
    }

    # Tier 2 — Trusted national outlets, broadcasters, academic institutions,
    # regional newspapers, and government portals.
    TIER_2_DOMAINS = {
        # Major broadcasters
        "npr.org", "pbs.org", "cbc.ca", "abc.net.au", "sbs.com.au",
        "dw.com", "france24.com", "rte.ie", "voanews.com", "rferl.org",
        "nhk.or.jp", "nhk.jp", "kbs.co.kr", "zdf.de", "ard.de",
        "raf.it", "rai.it", "rtve.es", "rfi.fr", "euronews.com",
        "yle.fi", "svt.se", "dr.dk", "nrk.no", "tv2.dk", "tv2.no",
        "ctvnews.ca", "globalnews.ca", "radio-canada.ca",
        # National newspapers
        "theatlantic.com", "time.com", "newsweek.com", "thehindu.com",
        "hindustantimes.com", "indianexpress.com", "ndtv.com", "livemint.com",
        "scroll.in", "thewire.in", "theprint.in", "thequint.com",
        "aljazeera.com", "aljazeera.net", "middleeasteye.net",
        "japantimes.co.jp", "asahi.com", "mainichi.jp", "yomiuri.co.jp",
        "scmp.com", "straitstimes.com", "koreaherald.com", "koreatimes.co.kr",
        "haaretz.com", "jpost.com", "dawn.com",
        "bostonglobe.com", "latimes.com", "chicagotribune.com",
        "seattletimes.com", "dallasnews.com", "houstonchronicle.com",
        "sfchronicle.com", "tampabay.com", "denverpost.com",
        "baltimoresun.com", "startribune.com", "oregonlive.com",
        "miamiherald.com", "smh.com.au", "theage.com.au",
        "globeandmail.com", "nationalpost.com", "thestar.com",
        "lemonde.fr", "lefigaro.fr", "elpais.com", "elmundo.es",
        "corriere.it", "repubblica.it", "faz.net", "sueddeutsche.de",
        # US TV networks
        "cbsnews.com", "nbcnews.com", "abcnews.go.com", "cnn.com", "cnbc.com",
        # Science / Health
        "scientificamerican.com", "newscientist.com", "discovermagazine.com",
        "sciencedaily.com", "phys.org", "quantamagazine.org", "statnews.com",
        "healthline.com", "mayoclinic.org", "hopkinsmedicine.org",
        "medicalnewstoday.com", "medscape.com", "webmd.com",
        "arxiv.org", "sciencedirect.com", "jstor.org", "plos.org",
        "eurekalert.org", "livescience.com", "iflscience.com",
        "technologyreview.com", "wired.com",
        # Academic / Think-tanks
        "harvard.edu", "mit.edu", "stanford.edu", "yale.edu",
        "princeton.edu", "columbia.edu", "cornell.edu", "upenn.edu",
        "uchicago.edu", "berkeley.edu", "cam.ac.uk", "ox.ac.uk",
        "rand.org", "cfr.org", "brookings.edu", "pewresearch.org",
        "ourworldindata.org", "statista.com", "gallup.com",
        "britannica.com", "wikipedia.org", "theconversation.com",
        # Government portals
        "gov.uk", "congress.gov", "whitehouse.gov", "state.gov",
        "india.gov.in", "pib.gov.in", "ec.europa.eu",
        "australia.gov.au", "canada.ca",
        # Fact-checkers (secondary)
        "logically.ai", "leadstories.com", "checkyourfact.com",
        "verifythis.com", "aap.com.au", "factly.in", "factchecker.in",
        "vishvasnews.com", "newsguardtech.com", "adfontesmedia.com",
        # Business / Finance
        "fortune.com", "forbes.com", "marketwatch.com", "businessinsider.com",
        "barrons.com", "investopedia.com", "axios.com", "thehill.com",
        "politico.com", "vox.com", "newrepublic.com", "foreignaffairs.com",
        # Investigative
        "propublica.org", "theintercept.com", "motherjones.com",
        "texastribune.org", "spotlightpa.org", "vtdigger.org",
    }

    def evaluate(self, corroboration_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the dict returned by WebCorroborator.corroborate() and returns:
          - final_score (0.0–1.0)  — weighted by source tier
          - tier1_count            — number of top-tier sources (Reuters, BBC etc.)
          - tier2_count            — number of secondary-tier sources
          - untrusted_count
          - verdict_label          — human-readable string
          - top_trusted_sources    — list of (domain, title) for display
        """
        matched = corroboration_result.get("matched_sources", [])
        base_score = corroboration_result.get("corroboration_score", 0.15)

        tier1, tier2, untrusted = [], [], []

        for src in matched:
            domain = src.get("domain", "")
            if any(t in domain for t in self.TIER_1_DOMAINS):
                tier1.append(src)
            elif any(t in domain for t in self.TIER_2_DOMAINS):
                tier2.append(src)
            elif src.get("trusted"):
                tier2.append(src)  # Other trusted domains → tier 2
            else:
                untrusted.append(src)

        # Weighted score boost from tier presence
        tier_boost = 0.0
        if len(tier1) >= 1:
            tier_boost += 0.15
        if len(tier1) >= 2:
            tier_boost += 0.10
        if len(tier2) >= 1:
            tier_boost += 0.05

        final_score = round(min(base_score + tier_boost, 1.0), 3)

        # Verdict label
        if len(tier1) >= 2:
            verdict_label = f"Strongly corroborated by {len(tier1)} top-tier sources"
        elif len(tier1) == 1:
            verdict_label = f"Corroborated by 1 top-tier source + {len(tier2)} secondary sources"
        elif len(tier2) >= 2:
            verdict_label = f"Partially corroborated by {len(tier2)} secondary trusted sources"
        elif len(tier2) == 1:
            verdict_label = "Weakly corroborated — only 1 secondary source found"
        else:
            verdict_label = "Not corroborated — no trusted sources found covering this story"

        top_trusted = [
            {"domain": s["domain"], "title": s["title"], "url": s["url"]}
            for s in (tier1 + tier2)[:5]
        ]

        return {
            "final_score": final_score,
            "tier1_count": len(tier1),
            "tier2_count": len(tier2),
            "untrusted_count": len(untrusted),
            "verdict_label": verdict_label,
            "top_trusted_sources": top_trusted,
        }

    def evaluate_url(self, url: str) -> float:
        """Backward-compatible single URL evaluation (used by legacy code)."""
        domain = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
        if any(t in domain for t in self.TIER_1_DOMAINS):
            return 0.95
        if any(t in domain for t in self.TIER_2_DOMAINS):
            return 0.80
        if any(td in domain for td in TRUSTED_DOMAINS):
            return 0.65
        return 0.35
