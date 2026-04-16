"""
scraper.py — Async, concurrent HTTP fetcher with retry / back-off logic.

Design decisions
----------------
* httpx.AsyncClient — modern async HTTP with HTTP/2 support.
* asyncio.Semaphore — limits concurrent connections to CONFIG.concurrency_limit
  to avoid hammering servers or getting IP-banned.
* Exponential back-off on transient failures (5xx, connection errors).
* Rotating User-Agent headers drawn from CONFIG.user_agents.
* Per-URL error isolation — one bad URL never kills the whole batch.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import httpx

from config import CONFIG
from models import ScrapingStatus

logger = logging.getLogger(__name__)


# ── Typing alias ──────────────────────────────────────────────────────────────

# (url, html_content | None, status, error_message | None)
FetchResult = Tuple[str, Optional[str], ScrapingStatus, Optional[str]]


# ── Low-level fetch (single URL, with retry) ─────────────────────────────────

async def _fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> FetchResult:
    """
    Fetch a single URL with exponential back-off retry.

    Protected by *semaphore* to bound concurrency.
    """
    async with semaphore:
        last_error: str = ""
        status = ScrapingStatus.FAILED

        for attempt in range(1, CONFIG.max_retries + 1):
            try:
                headers = {
                    "User-Agent": random.choice(CONFIG.user_agents),
                    "Accept": (
                        "text/html,application/xhtml+xml,"
                        "application/xml;q=0.9,*/*;q=0.8"
                    ),
                    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }

                response = await client.get(
                    url,
                    headers=headers,
                    follow_redirects=True,
                    timeout=CONFIG.request_timeout,
                )

                # Bot-block detection (Cloudflare, etc.)
                if response.status_code in (403, 429, 503):
                    logger.warning(
                        "⛔  [%s] HTTP %d — likely blocked (attempt %d/%d)",
                        _short_url(url), response.status_code, attempt, CONFIG.max_retries,
                    )
                    last_error = f"HTTP {response.status_code}"
                    status = ScrapingStatus.BLOCKED

                    if attempt < CONFIG.max_retries:
                        await asyncio.sleep(
                            CONFIG.retry_backoff_base ** attempt + random.uniform(0, 0.5)
                        )
                    continue

                response.raise_for_status()

                # Check content type — skip PDFs, images, etc.
                content_type: str = response.headers.get("content-type", "")
                if "text/html" not in content_type and "text/plain" not in content_type:
                    logger.info("⏭   [%s] Non-HTML content-type: %s", _short_url(url), content_type)
                    return url, None, ScrapingStatus.SKIPPED, f"Non-HTML: {content_type}"

                html = response.text
                logger.info(
                    "✅  [%s] Fetched %d bytes (attempt %d)",
                    _short_url(url), len(html), attempt,
                )
                return url, html, ScrapingStatus.SUCCESS, None

            except httpx.TimeoutException:
                last_error = "Request timed out"
                status = ScrapingStatus.TIMEOUT
                logger.warning(
                    "⏱   [%s] Timeout (attempt %d/%d)",
                    _short_url(url), attempt, CONFIG.max_retries,
                )

            except httpx.TooManyRedirects:
                return url, None, ScrapingStatus.FAILED, "Too many redirects"

            except httpx.RequestError as exc:
                last_error = f"Request error: {exc}"
                status = ScrapingStatus.FAILED
                logger.warning(
                    "❌  [%s] %s (attempt %d/%d)",
                    _short_url(url), exc, attempt, CONFIG.max_retries,
                )

            except Exception as exc:
                last_error = f"Unexpected error: {exc}"
                status = ScrapingStatus.FAILED
                logger.exception("💥  [%s] Unexpected exception", _short_url(url))

            # Back-off before retry
            if attempt < CONFIG.max_retries:
                delay = CONFIG.retry_backoff_base ** attempt + random.uniform(0, 0.3)
                logger.debug("   Retrying in %.1fs…", delay)
                await asyncio.sleep(delay)

        return url, None, status, last_error


# ── Batch fetch (all URLs) ────────────────────────────────────────────────────

async def fetch_all_pages(urls: List[str]) -> List[FetchResult]:
    """
    Concurrently fetch all URLs and return a list of FetchResult tuples.

    Parameters
    ----------
    urls : List[str]
        List of validated HTTP(S) URLs.

    Returns
    -------
    List[FetchResult]
        One entry per URL — successes and failures alike.
    """
    semaphore = asyncio.Semaphore(CONFIG.concurrency_limit)

    # Build a single shared client (connection pooling, HTTP/2)
    async with httpx.AsyncClient(
        http2=True,
        verify=True,
        limits=httpx.Limits(
            max_connections=CONFIG.concurrency_limit + 2,
            max_keepalive_connections=CONFIG.concurrency_limit,
            keepalive_expiry=10,
        ),
    ) as client:
        tasks = [
            _fetch_with_retry(client, url, semaphore)
            for url in urls
        ]
        results: List[FetchResult] = await asyncio.gather(*tasks, return_exceptions=False)

    success_count = sum(1 for _, html, status, _ in results if status == ScrapingStatus.SUCCESS)
    logger.info(
        "📦  Batch complete — %d/%d pages fetched successfully",
        success_count, len(urls),
    )
    return results


# ── Utility ───────────────────────────────────────────────────────────────────

def _short_url(url: str, max_len: int = 60) -> str:
    """Truncate a URL for log readability."""
    return url if len(url) <= max_len else url[:max_len] + "…"
