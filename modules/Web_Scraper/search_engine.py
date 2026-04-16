"""
search_engine.py — Discovers relevant URLs for a query.

Architecture note
-----------------
We use the `duckduckgo_search` library (DDGS) which wraps DuckDuckGo's
internal API — no API key required, no rate-limit billing.

Alternatives considered:
  • SerpAPI / ValueSERP — reliable but paid ($50+/month for production volume)
  • Google Custom Search JSON API — 100 free queries/day, then paid
  • Bing Search API — $7/1 000 queries; needs Azure account
  • Direct scraping of Google SERP — heavily bot-protected; violates ToS

DDGS is the best zero-cost option for a self-hosted scraper.  For production
at scale, swap _search_duckduckgo() for a SerpAPI call — the interface is
identical.

Risk note on direct SERP scraping
----------------------------------
Scraping Google/Bing SERPs without an API violates their ToS, triggers
CAPTCHAs / IP bans, and is legally grey in some jurisdictions.  DDGS avoids
this — it uses DDG's lite endpoint which is permissive about programmatic use.
"""

import logging
import re
from typing import List
from urllib.parse import urlparse

from ddgs import DDGS

from config import CONFIG

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_blocked(url: str) -> bool:
    """Return True if a URL's domain matches the configured block list."""
    try:
        hostname = urlparse(url).hostname or ""
        return any(bad in hostname for bad in CONFIG.blocked_domains)
    except Exception:
        return True  # Malformed URL → skip


def _looks_like_url(value: str) -> bool:
    """Cheap check that the string is a plausible HTTP(S) URL."""
    return bool(re.match(r"^https?://", value, re.IGNORECASE))


# ── Core search function ──────────────────────────────────────────────────────

def fetch_search_urls(query: str) -> List[str]:
    """
    Use DuckDuckGo to retrieve the top-N URLs for *query*.

    Parameters
    ----------
    query : str
        A clean, validated search query.

    Returns
    -------
    List[str]
        Ordered list of unique HTTP(S) URLs (blocked domains excluded).
        May be shorter than CONFIG.max_search_results if DDG returns fewer.

    Raises
    ------
    RuntimeError
        If the search layer returns zero results (network issue, etc.).
    """
    logger.info("🔎  Searching DuckDuckGo for: '%s'", query)

    raw_results: list[dict] = []
    try:
        with DDGS() as ddgs:
            raw_results = list(
                ddgs.text(
                    query,
                    region=CONFIG.search_region,
                    safesearch=CONFIG.search_safe_search,
                    max_results=CONFIG.max_search_results * 2,  # over-fetch then filter
                )
            )
    except Exception as exc:
        logger.error("DuckDuckGo search failed: %s", exc)
        raise RuntimeError(f"Search engine error: {exc}") from exc

    if not raw_results:
        raise RuntimeError(
            "Search returned zero results. "
            "Check your internet connection or try a different query."
        )

    # Filter, deduplicate, and cap
    seen: set[str] = set()
    urls: List[str] = []

    for item in raw_results:
        url: str = item.get("href", "").strip()

        if not _looks_like_url(url):
            continue
        if _is_blocked(url):
            logger.debug("Blocked domain — skipping: %s", url)
            continue
        if url in seen:
            continue

        seen.add(url)
        urls.append(url)

        if len(urls) >= CONFIG.max_search_results:
            break

    logger.info("✅  %d usable URLs found", len(urls))
    for i, u in enumerate(urls, 1):
        logger.debug("  [%d] %s", i, u)

    return urls
