"""
pipeline.py — Async orchestrator: wires every module together.

Flow
----
query_handler → search_engine → scraper (async) → content_cleaner → relevance_scorer → JSON

This module is the single entry point for both CLI usage and future
FastAPI integration.  It is fully async and returns a ScraperOutput
Pydantic model that serialises directly to JSON.
"""

import asyncio
import logging
import time
from typing import List, Optional

from config import CONFIG
from content_cleaner import parse_page
from models import ScrapedPage, ScraperOutput, ScrapingStatus
from query_handler import process_query
from relevance_scorer import score_and_rank
from scraper import FetchResult, fetch_all_pages
from search_engine import fetch_search_urls

logger = logging.getLogger(__name__)


# ── Public API (async) ────────────────────────────────────────────────────────

async def run_pipeline(raw_query: str) -> ScraperOutput:
    """
    Full scraping pipeline — accepts a raw user query and returns
    a structured ScraperOutput ready for JSON serialisation.

    Parameters
    ----------
    raw_query : str
        Unvalidated string from the user / API caller.

    Returns
    -------
    ScraperOutput
        Pydantic model with ranked results.

    Raises
    ------
    ValueError
        If the query is invalid (propagated from query_handler).
    RuntimeError
        If the search layer completely fails.
    """
    t0 = time.perf_counter()

    # ── Step 1: Validate & clean query ───────────────────────────────────────
    logger.info("═══════════════════════════════════════════")
    logger.info("🚀  Pipeline start")
    query: str = process_query(raw_query)
    logger.info("📝  Query: '%s'", query)

    # ── Step 2: Discover URLs via DuckDuckGo ─────────────────────────────────
    urls: List[str] = fetch_search_urls(query)
    logger.info("🌐  URLs to scrape: %d", len(urls))

    # ── Step 3: Async-fetch all pages ─────────────────────────────────────────
    fetch_results: List[FetchResult] = await fetch_all_pages(urls)

    # ── Step 4: Parse HTML → ScrapedPage ─────────────────────────────────────
    pages: List[ScrapedPage] = []
    for url, html, status, error in fetch_results:
        if status == ScrapingStatus.SUCCESS and html:
            try:
                page = parse_page(url, html)
                pages.append(page)
            except Exception as exc:
                logger.warning("⚠️   parse_page failed for %s: %s", url, exc)
                pages.append(
                    ScrapedPage(
                        url=url,
                        status=ScrapingStatus.FAILED,
                        error=str(exc),
                    )
                )
        else:
            # Preserve failed/skipped/blocked pages for transparency
            pages.append(
                ScrapedPage(
                    url=url,
                    status=status,
                    error=error,
                )
            )

    successful = sum(1 for p in pages if p.status == ScrapingStatus.SUCCESS)
    logger.info("✅  Pages parsed successfully: %d / %d", successful, len(pages))

    # ── Step 5: Score & rank ──────────────────────────────────────────────────
    results = score_and_rank(query, pages)

    # ── Step 6: Build output envelope ─────────────────────────────────────────
    elapsed = time.perf_counter() - t0
    logger.info("🏁  Pipeline complete in %.2fs", elapsed)
    logger.info("═══════════════════════════════════════════")

    return ScraperOutput(
        query=query,
        total_scraped=len(pages),
        total_returned=len(results),
        results=results,
    )


# ── Sync convenience wrapper (for non-async callers) ─────────────────────────

def run_pipeline_sync(raw_query: str) -> ScraperOutput:
    """
    Synchronous wrapper around run_pipeline().
    Use this from plain scripts or pytest; use run_pipeline() from FastAPI.
    """
    return asyncio.run(run_pipeline(raw_query))
