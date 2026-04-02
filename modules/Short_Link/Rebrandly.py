from typing import Optional
import requests

from utils.config import get_api_key
from utils.helpers import is_valid_url
from utils.logger import get_logger

logger = get_logger(__name__)

_API_BASE = "https://api.rebrandly.com/v1"


class RebrandlyShortener:
    """Rebrandly provider for branded URL shortening with custom domains."""

    def __init__(self) -> None:
        self.api_key = get_api_key("REBRANDLY_API_KEY")
        self._headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        logger.info("RebrandlyShortener initialized.")

    def shorten(self, url: str, slug: Optional[str] = None,
                domain: Optional[str] = None, title: Optional[str] = None,
                tags: Optional[list[str]] = None) -> dict:
        """Create a branded short link via Rebrandly.

        Args:
            url: The destination (long) URL.
            slug: Optional custom slug (e.g. 'summer-sale').
            domain: Custom domain (e.g. 'go.yourbrand.com').
            title: Optional human-readable title.
            tags: Optional list of tag name strings.

        Returns:
            Dict with 'short_url', 'short_link', 'long_url', 'id', 'slug',
            'domain', 'created_at'.

        Raises:
            ValueError: If url is empty or invalid.
            RuntimeError: If the API call fails.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")
        if not is_valid_url(url):
            raise ValueError(f"Invalid URL: '{url}'.")

        payload: dict = {"destination": url}
        if slug:
            payload["slashtag"] = slug
        if domain:
            payload["domain"] = {"fullName": domain}
        if title:
            payload["title"] = title

        try:
            resp = requests.post(f"{_API_BASE}/links", json=payload,
                                 headers=self._headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            short_link = data.get("shortUrl", "")
            result = {"short_url": f"https://{short_link}" if short_link else "",
                      "short_link": short_link, "long_url": data.get("destination", url),
                      "id": data.get("id", ""), "slug": data.get("slashtag", ""),
                      "domain": data.get("domain", {}).get("fullName", ""),
                      "created_at": data.get("createdAt", "")}
            if tags:
                self._add_tags(data.get("id", ""), tags)
            return result
        except requests.HTTPError as e:
            raise RuntimeError(f"Rebrandly shortening failed: {e}") from e

    def _add_tags(self, link_id: str, tag_names: list[str]) -> None:
        for tag_name in tag_names:
            try:
                resp = requests.post(f"{_API_BASE}/tags", json={"name": tag_name},
                                     headers=self._headers, timeout=10)
                if resp.ok:
                    tag_id = resp.json().get("id", "")
                    if tag_id:
                        requests.post(f"{_API_BASE}/links/{link_id}/tags/{tag_id}",
                                      headers=self._headers, timeout=10)
            except Exception as e:
                logger.warning(f"Rebrandly tag '{tag_name}' failed: {e}")

    def get_link(self, link_id: str) -> dict:
        """Retrieve details of a Rebrandly link by ID."""
        if not link_id or not link_id.strip():
            raise ValueError("link_id cannot be empty.")
        try:
            resp = requests.get(f"{_API_BASE}/links/{link_id}",
                                headers=self._headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            raise RuntimeError(f"Rebrandly get_link failed: {e}") from e

    def get_clicks(self, link_id: str) -> int:
        """Get total click count for a Rebrandly link."""
        return self.get_link(link_id).get("clicks", 0)

    def list_links(self, limit: int = 25, order_by: str = "createdAt",
                   order_dir: str = "desc") -> list[dict]:
        """List branded links in the account."""
        if order_dir not in ("asc", "desc"):
            raise ValueError("order_dir must be 'asc' or 'desc'.")
        try:
            resp = requests.get(f"{_API_BASE}/links",
                                params={"limit": min(limit, 25), "orderBy": order_by,
                                        "orderDir": order_dir},
                                headers=self._headers, timeout=15)
            resp.raise_for_status()
            return [{"id": l.get("id", ""),
                     "short_url": f"https://{l.get('shortUrl', '')}",
                     "long_url": l.get("destination", ""), "slug": l.get("slashtag", ""),
                     "title": l.get("title", ""), "clicks": l.get("clicks", 0),
                     "created_at": l.get("createdAt", "")} for l in resp.json()]
        except requests.HTTPError as e:
            raise RuntimeError(f"Rebrandly list_links failed: {e}") from e

    def delete_link(self, link_id: str) -> bool:
        """Delete a Rebrandly link permanently."""
        if not link_id or not link_id.strip():
            raise ValueError("link_id cannot be empty.")
        try:
            resp = requests.delete(f"{_API_BASE}/links/{link_id}",
                                   headers=self._headers, timeout=10)
            resp.raise_for_status()
            return True
        except requests.HTTPError as e:
            raise RuntimeError(f"Rebrandly delete_link failed: {e}") from e
