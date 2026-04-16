"""
relevance_scorer.py — Rank scraped pages against the user query.

Scoring model
-------------
A lightweight, dependency-free relevance score [0.0 – 1.0] composed of:

  Component                        Weight
  ─────────────────────────────── ──────
  Title keyword coverage             30%
  Heading keyword coverage           20%
  Content keyword density (TF-like)  30%
  Domain authority heuristic         10%
  Content length adequacy            10%

All components are normalised to [0, 1] before weighting.

Why not a full TF-IDF?
  For a small result set (≤10 pages) the overhead of a vectoriser is
  unnecessary; this custom scorer is faster and fully interpretable.
  For larger corpora, swap in sklearn TfidfVectorizer + cosine_similarity.
"""

import logging
import math
import re
from typing import List, Set

from config import CONFIG
from models import ScrapedPage, ScoredResult, ScrapingStatus

logger = logging.getLogger(__name__)


# ── Known high-authority TLDs / domains (simple lookup) ──────────────────────
# Used as a proxy for domain authority since we don't have Moz/Ahrefs data.
_HIGH_AUTHORITY_DOMAINS: Set[str] = {
    # Major Indian e-commerce / tech portals
    "amazon.in", "flipkart.com", "myntra.com", "snapdeal.com",
    "nykaa.com", "croma.com", "reliancedigital.in", "vijaysales.com",
    # Review / comparison sites
    "91mobiles.com", "gadgets360.com", "ndtv.com", "techradar.com",
    "tomsguide.com", "rtings.com", "gsmarena.com",
    # General high-authority
    "wikipedia.org", "reddit.com", "quora.com",
    "forbes.com", "businessinsider.com",
}

_MEDIUM_AUTHORITY_DOMAINS: Set[str] = {
    "medium.com", "wordpress.com", "blogspot.com",
    "github.com", "stackoverflow.com",
}


# ── Public API ────────────────────────────────────────────────────────────────

def score_and_rank(
    query: str,
    pages: List[ScrapedPage],
) -> List[ScoredResult]:
    """
    Score each page against the query and return top-N results sorted by score.

    Parameters
    ----------
    query : str
        The clean user query.
    pages : List[ScrapedPage]
        Parsed pages (only SUCCESS status are scored; others get score=0).

    Returns
    -------
    List[ScoredResult]
        Top-N results, descending by score, ready for JSON serialisation.
    """
    keywords: List[str] = _tokenise(query)
    logger.info("📊  Scoring %d pages against %d keywords", len(pages), len(keywords))

    scored: List[ScoredResult] = []

    for page in pages:
        if page.status != ScrapingStatus.SUCCESS or not page.content:
            # Pass failed pages through with score 0 — pipeline can filter them
            scored.append(
                ScoredResult(
                    url=page.url,
                    title=page.title or page.url,
                    summary=page.summary,
                    content=page.content,
                    score=0.0,
                    status=page.status,
                )
            )
            continue

        score = _compute_score(keywords, page)
        logger.debug("  score=%.3f  %s", score, page.url[:70])

        scored.append(
            ScoredResult(
                url=page.url,
                title=page.title or page.url,
                summary=page.summary,
                content=page.content,
                score=round(score, 4),
                status=page.status,
            )
        )

    # Sort descending, keep top-N
    scored.sort(key=lambda r: r.score, reverse=True)
    top_n = scored[: CONFIG.top_n_results]

    logger.info(
        "🏆  Top result: score=%.3f  %s",
        top_n[0].score if top_n else 0,
        top_n[0].url[:70] if top_n else "—",
    )
    return top_n


# ── Scoring components ────────────────────────────────────────────────────────

def _compute_score(keywords: List[str], page: ScrapedPage) -> float:
    """Weighted composite score for one page."""
    title_score   = _keyword_coverage(keywords, _tokenise(page.title))
    heading_score = _keyword_coverage(
        keywords,
        _tokenise(" ".join(page.headings)),
    )
    content_score = _content_density(keywords, page.content)
    domain_score  = _domain_authority(page.url)
    length_score  = _length_score(page.word_count)

    composite = (
        0.30 * title_score
        + 0.20 * heading_score
        + 0.30 * content_score
        + 0.10 * domain_score
        + 0.10 * length_score
    )
    return min(composite, 1.0)


def _keyword_coverage(query_kws: List[str], text_tokens: List[str]) -> float:
    """
    Fraction of query keywords found in *text_tokens*.
    Returns 0 if either list is empty.
    """
    if not query_kws or not text_tokens:
        return 0.0
    text_set = set(text_tokens)
    hits = sum(1 for kw in query_kws if kw in text_set)
    return hits / len(query_kws)


def _content_density(keywords: List[str], content: str) -> float:
    """
    TF-like keyword density capped at 1.0.

    Computes: min(1, Σ tf(kw, content) × log(1 + count))
    where tf = raw count / total_words.
    """
    if not keywords or not content:
        return 0.0

    words = _tokenise(content)
    if not words:
        return 0.0

    total = len(words)
    score = 0.0
    for kw in keywords:
        count = words.count(kw)
        if count:
            tf = count / total
            # Diminishing returns: log-compress high-frequency terms
            score += tf * math.log(1 + count)

    # Normalise: if every keyword appears once, score ≈ len(kws)/total*log2
    # We cap at 1.0
    return min(score * 10, 1.0)   # ×10 empirical scaling for typical page lengths


def _domain_authority(url: str) -> float:
    """
    Heuristic domain authority score [0.0 – 1.0] based on domain lookup.
    """
    from urllib.parse import urlparse
    try:
        hostname = urlparse(url).hostname or ""
        # Strip www.
        domain = hostname.removeprefix("www.")
    except Exception:
        return 0.2

    if domain in _HIGH_AUTHORITY_DOMAINS:
        return 1.0
    if domain in _MEDIUM_AUTHORITY_DOMAINS:
        return 0.6
    if domain.endswith(".gov.in") or domain.endswith(".edu.in"):
        return 0.9
    if domain.endswith(".gov") or domain.endswith(".edu"):
        return 0.85
    return 0.3   # unknown domain — neutral-low prior


def _length_score(word_count: int) -> float:
    """
    Reward pages with substantive content.
    Very short pages (<100 words) score 0; rich pages (>600 words) score 1.
    """
    if word_count < 100:
        return 0.0
    if word_count >= 600:
        return 1.0
    return (word_count - 100) / 500   # linear ramp


# ── Tokeniser ─────────────────────────────────────────────────────────────────

# Common English/Hindi stop words to ignore during keyword matching
_STOP_WORDS: Set[str] = {
    "a", "an", "the", "and", "or", "of", "in", "on", "at", "to", "for",
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "shall", "can", "not", "no", "nor", "so", "yet", "both",
    "with", "as", "by", "from", "up", "about", "into", "through", "this",
    "that", "these", "those", "it", "its", "i", "me", "my", "you", "your",
    "he", "she", "we", "they", "their", "our", "what", "which", "who",
    # Hindi transliterations common in Indian queries
    "mein", "ka", "ke", "ki", "hai", "ho", "hain",
}


def _tokenise(text: str) -> List[str]:
    """
    Lowercase, strip punctuation, split into tokens, remove stop words.
    """
    if not text:
        return []
    tokens = re.findall(r"[a-z0-9₹]+", text.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]
