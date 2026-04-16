"""
content_cleaner.py — HTML → clean structured data.

Extraction strategy (layered fallback)
---------------------------------------
1. trafilatura   — best-in-class boilerplate-removal; beats readability & BS4
                   on recall for article/blog/product pages.
2. BeautifulSoup — fallback when trafilatura returns nothing (thin pages,
                   JS-rendered stubs, unusual markup).
3. Empty string  — last resort; the relevance scorer will give the page a
                   low score and it will likely be filtered out.

Why trafilatura?
- Removes nav bars, sidebars, ads, cookie banners, footers natively.
- Returns clean UTF-8 text without HTML tags.
- Has its own HTML fetch capability but we supply pre-fetched HTML
  (html= parameter) to avoid a second request.
"""

import logging
import re
import textwrap
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import trafilatura
from bs4 import BeautifulSoup, Tag

from models import PageMetadata, ScrapedPage, ScrapingStatus

logger = logging.getLogger(__name__)


# ── Main entry point ──────────────────────────────────────────────────────────

def parse_page(url: str, html: str) -> ScrapedPage:
    """
    Parse raw HTML into a structured ScrapedPage.

    Parameters
    ----------
    url  : str   Original URL (needed for resolving relative links).
    html : str   Raw HTML response body.

    Returns
    -------
    ScrapedPage
    """
    soup = _get_soup(html)

    title      = _extract_title(soup)
    headings   = _extract_headings(soup)
    metadata   = _extract_metadata(soup)
    images     = _extract_images(soup, url)
    links      = _extract_internal_links(soup, url)
    content    = _extract_content(html, soup)
    summary    = _make_summary(content)
    word_count = len(content.split())

    return ScrapedPage(
        url=url,
        title=title,
        headings=headings,
        content=content,
        summary=summary,
        metadata=metadata,
        images=images,
        internal_links=links,
        status=ScrapingStatus.SUCCESS,
        word_count=word_count,
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _get_soup(html: str) -> BeautifulSoup:
    """Parse HTML with lxml (fast) and fall back to html.parser."""
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def _extract_title(soup: BeautifulSoup) -> str:
    """Return the best available page title."""
    # Prefer og:title (often cleaner than <title>)
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return _clean_text(og["content"])

    tag = soup.find("title")
    if tag:
        return _clean_text(tag.get_text())

    # Fall back to first H1
    h1 = soup.find("h1")
    if h1:
        return _clean_text(h1.get_text())

    return ""


def _extract_headings(soup: BeautifulSoup) -> List[str]:
    """Return all H1–H3 headings as a flat list (deduplicated, order-preserved)."""
    seen: set[str] = set()
    headings: List[str] = []

    for tag_name in ("h1", "h2", "h3"):
        for tag in soup.find_all(tag_name):
            text = _clean_text(tag.get_text())
            if text and text not in seen and len(text) > 3:
                seen.add(text)
                headings.append(text)

    return headings[:20]  # cap so the model payload stays sane


def _extract_metadata(soup: BeautifulSoup) -> PageMetadata:
    """Extract common <meta> fields into a PageMetadata object."""

    def _meta(name: Optional[str] = None, prop: Optional[str] = None) -> Optional[str]:
        """Helper to pull a <meta> value by name or property attribute."""
        if name:
            tag = soup.find("meta", attrs={"name": name})
        elif prop:
            tag = soup.find("meta", property=prop)
        else:
            return None
        return _clean_text(tag["content"]) if tag and tag.get("content") else None

    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href") if canonical_tag else None

    return PageMetadata(
        description=_meta(name="description") or _meta(prop="og:description"),
        keywords=_meta(name="keywords"),
        author=_meta(name="author"),
        og_title=_meta(prop="og:title"),
        og_image=_meta(prop="og:image"),
        canonical=canonical,
    )


def _extract_images(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    Return absolute URLs of the top content images.
    Skips icons, tracking pixels (<10px), and data URIs.
    """
    images: List[str] = []
    for img in soup.find_all("img", src=True):
        src: str = img["src"].strip()

        # Skip data URIs and empty values
        if not src or src.startswith("data:"):
            continue

        # Skip tiny images (likely icons/trackers)
        width  = _int_attr(img, "width")
        height = _int_attr(img, "height")
        if width and width < 50:
            continue
        if height and height < 50:
            continue

        abs_url = urljoin(base_url, src)
        if abs_url.startswith("http"):
            images.append(abs_url)

        if len(images) >= 10:
            break

    return images


def _extract_internal_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Return up to 15 internal links (same domain) as absolute URLs."""
    base_domain = urlparse(base_url).netloc
    links: List[str] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href: str = a["href"].strip()
        abs_url = urljoin(base_url, href)

        if not abs_url.startswith("http"):
            continue

        parsed = urlparse(abs_url)
        if parsed.netloc != base_domain:
            continue  # external link

        clean = abs_url.split("#")[0]  # strip fragments
        if clean in seen:
            continue

        seen.add(clean)
        links.append(clean)

        if len(links) >= 15:
            break

    return links


def _extract_content(html: str, soup: BeautifulSoup) -> str:
    """
    Layered content extraction: trafilatura → BeautifulSoup fallback.
    """
    # ── Layer 1: trafilatura ──────────────────────────────────────────────────
    try:
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=False,  # favour recall for varied page types
        )
        if extracted and len(extracted.strip()) > 100:
            return _normalise_whitespace(extracted)
    except Exception as exc:
        logger.debug("trafilatura failed: %s", exc)

    # ── Layer 2: BeautifulSoup fallback ───────────────────────────────────────
    logger.debug("Falling back to BeautifulSoup content extraction")
    return _bs4_extract(soup)


def _bs4_extract(soup: BeautifulSoup) -> str:
    """
    Remove boilerplate tags, then grab all visible paragraph text.
    Not as good as trafilatura but works on many thin pages.
    """
    # Remove clearly non-content tags
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "noscript", "iframe",
                     "button", "select", "input"]):
        tag.decompose()

    # Prefer <article> or <main> if present
    main_tag: Optional[Tag] = soup.find("article") or soup.find("main")
    container: BeautifulSoup | Tag = main_tag if main_tag else soup

    paragraphs: List[str] = []
    for p in container.find_all(["p", "li", "td", "h1", "h2", "h3", "h4"]):
        text = _clean_text(p.get_text())
        if len(text) > 30:  # ignore stub lines
            paragraphs.append(text)

    return _normalise_whitespace("\n".join(paragraphs))


def _make_summary(content: str, max_chars: int = 400) -> str:
    """
    Return the first ~400 chars of content wrapped at word boundaries.
    This is a cheap heuristic summary; the pipeline can swap in an LLM call here.
    """
    if not content:
        return ""
    snippet = content[:max_chars]
    # Don't cut in the middle of a word
    last_space = snippet.rfind(" ")
    if last_space > max_chars // 2:
        snippet = snippet[:last_space]
    return snippet.strip() + ("…" if len(content) > max_chars else "")


# ── Text utilities ────────────────────────────────────────────────────────────

def _clean_text(text: Optional[str]) -> str:
    """Strip tags, collapse whitespace, remove zero-width chars."""
    if not text:
        return ""
    # Remove zero-width and non-printable chars
    text = re.sub(r"[\u200b\u200c\u200d\ufeff\u00ad]", "", text)
    return _normalise_whitespace(text)


def _normalise_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines into single spaces/newlines."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _int_attr(tag: Tag, attr: str) -> Optional[int]:
    """Safely read an integer HTML attribute (width/height)."""
    try:
        return int(tag.get(attr, 0))
    except (ValueError, TypeError):
        return None
