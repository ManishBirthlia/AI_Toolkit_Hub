"""
config.py — Centralised configuration for the web scraping system.
All tuneable knobs live here so nothing is hard-coded elsewhere.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ScraperConfig:
    # ── Search ────────────────────────────────────────────────────────────────
    max_search_results: int = 10          # URLs retrieved from DuckDuckGo
    search_region: str = "in-en"         # DuckDuckGo region (India / English)
    search_safe_search: str = "moderate"

    # ── HTTP client ───────────────────────────────────────────────────────────
    request_timeout: float = 15.0        # seconds per request
    max_retries: int = 3
    retry_backoff_base: float = 1.5      # exponential back-off multiplier
    concurrency_limit: int = 5           # max simultaneous HTTP connections

    # ── Content extraction ────────────────────────────────────────────────────
    min_content_length: int = 150        # skip pages with fewer chars
    max_content_length: int = 15_000     # truncate very large pages

    # ── Relevance scoring ─────────────────────────────────────────────────────
    top_n_results: int = 5               # how many results to return

    # ── User-agent rotation ───────────────────────────────────────────────────
    user_agents: List[str] = field(default_factory=lambda: [
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15"
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
    ])

    # ── Blocklist — skip these domains entirely ───────────────────────────────
    blocked_domains: List[str] = field(default_factory=lambda: [
        "facebook.com", "instagram.com", "twitter.com", "x.com",
        "tiktok.com", "pinterest.com", "reddit.com",   # social-only noise
        "login.", "signup.", "accounts.",               # auth walls
    ])


# Singleton used everywhere
CONFIG = ScraperConfig()
