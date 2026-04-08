"""
Google Trends module — fetches the latest trending topics and enriches
them with web search results for structured consumption.

Uses the public Google Trends RSS feed (no API key required) and
DuckDuckGo for follow-up searches.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
from ddgs import DDGS

from utils.logger import get_logger

logger = get_logger(__name__)

# Google Trends Daily RSS — returns the latest trending searches
_TRENDS_RSS_URL = "https://trends.google.com/trending/rss?geo={geo}"


@dataclass
class SearchHit:
    """A single web search result."""
    title: str
    url: str
    snippet: str


@dataclass
class TrendItem:
    """Structured representation of a single trending topic."""
    rank: int
    title: str
    approximate_traffic: str
    published: str
    news_url: str
    search_results: List[SearchHit] = field(default_factory=list)


class GoogleTrends:
    """Fetch the latest Google Trends and enrich each with web search data.

    Example:
        >>> gt = GoogleTrends(geo="US")
        >>> trends = gt.fetch_trends(top_n=5, search_depth=3)
        >>> for t in trends:
        ...     print(t.title, t.approximate_traffic)
    """

    def __init__(self, geo: str = "US") -> None:
        """
        Args:
            geo: Two-letter country code for regional trends (e.g. "US", "IN", "GB").
        """
        self.geo = geo.upper()
        self._rss_url = _TRENDS_RSS_URL.format(geo=self.geo)
        logger.info(f"GoogleTrends initialized | geo='{self.geo}'")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_trends(self, top_n: int = 5, search_depth: int = 3) -> List[TrendItem]:
        """Fetch the top N trending topics, then search the web for each.

        Args:
            top_n: Number of trending topics to return (max ~20 from feed).
            search_depth: How many web search results to fetch per trend.

        Returns:
            List of TrendItem dataclasses, each enriched with search_results.

        Raises:
            RuntimeError: If the RSS feed cannot be fetched.
        """
        logger.info(f"Fetching top {top_n} trends for geo='{self.geo}'...")
        raw_trends = self._fetch_rss(top_n)

        for trend in raw_trends:
            trend.search_results = self._search_topic(trend.title, limit=search_depth)

        logger.info(f"Enriched {len(raw_trends)} trends with web search results.")
        return raw_trends

    def fetch_trends_as_dicts(self, top_n: int = 5, search_depth: int = 3) -> List[Dict[str, Any]]:
        """Same as fetch_trends but returns plain dicts (JSON-serialisable)."""
        return [asdict(t) for t in self.fetch_trends(top_n, search_depth)]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _fetch_rss(self, top_n: int) -> List[TrendItem]:
        """Parse the Google Trends RSS feed into TrendItem objects."""
        try:
            resp = requests.get(self._rss_url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch Google Trends RSS: {e}") from e

        # The feed uses the 'ht' namespace for traffic data
        ns = {"ht": "https://trends.google.com/trending/rss"}
        root = ET.fromstring(resp.text)
        items = root.findall(".//item")

        trends: List[TrendItem] = []
        for rank, item in enumerate(items[:top_n], start=1):
            title = (item.findtext("title") or "").strip()

            traffic_el = item.find("ht:approx_traffic", ns)
            traffic = traffic_el.text.strip() if traffic_el is not None and traffic_el.text else "N/A"

            pub_date = (item.findtext("pubDate") or "").strip()
            # Try to normalise to a cleaner date string
            try:
                pub_dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                pub_date = pub_dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                pass

            link = (item.findtext("link") or "").strip()

            trends.append(TrendItem(
                rank=rank,
                title=title,
                approximate_traffic=traffic,
                published=pub_date,
                news_url=link,
            ))
            logger.debug(f"Trend #{rank}: {title} ({traffic})")

        return trends

    def _search_topic(self, query: str, limit: int = 3) -> List[SearchHit]:
        """Search the web for a trending topic using DuckDuckGo."""
        hits: List[SearchHit] = []
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=limit)
                if results:
                    for r in results:
                        hits.append(SearchHit(
                            title=r.get("title", ""),
                            url=r.get("href", ""),
                            snippet=r.get("body", ""),
                        ))
        except Exception as e:
            logger.warning(f"Web search failed for '{query}': {e}")

        return hits
