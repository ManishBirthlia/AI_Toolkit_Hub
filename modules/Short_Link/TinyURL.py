from typing import Optional
import requests

from utils.helpers import is_valid_url
from utils.logger import get_logger

logger = get_logger(__name__)

_API_BASE = "https://api.tinyurl.com"


class TinyURLShortener:
    """TinyURL provider. Free unauthenticated tier available (no API key required)."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key
        self._authenticated = bool(api_key)
        self._headers = {"Content-Type": "application/json"}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"
        logger.info(f"TinyURLShortener initialized | authenticated={self._authenticated}")

    def shorten(self, url: str, alias: Optional[str] = None,
                domain: str = "tinyurl.com",
                tags: Optional[list[str]] = None,
                expires_at: Optional[str] = None) -> dict:
        """Shorten a URL using TinyURL.

        Args:
            url: The long URL to shorten.
            alias: Optional custom alias (requires API key).
            domain: Domain to use. Defaults to 'tinyurl.com'.
            tags: Optional list of tags (requires API key).
            expires_at: Optional expiry datetime in ISO 8601 (requires API key).

        Returns:
            Dict with 'short_url', 'long_url', 'alias', 'domain'.

        Raises:
            ValueError: If url is empty, invalid, or alias requested without key.
            RuntimeError: If the API call fails.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")
        if not is_valid_url(url):
            raise ValueError(f"Invalid URL: '{url}'.")
        if alias and not self._authenticated:
            raise ValueError("Custom aliases require a TinyURL API key.")

        if not self._authenticated:
            return self._shorten_free(url)

        payload: dict = {"url": url, "domain": domain}
        if alias:
            payload["alias"] = alias
        if tags:
            payload["tags"] = tags
        if expires_at:
            payload["expires_at"] = expires_at

        try:
            resp = requests.post(f"{_API_BASE}/create", json=payload,
                                 headers=self._headers, timeout=15)
            resp.raise_for_status()
            data = resp.json().get("data", {})
            return {"short_url": data.get("tiny_url", ""), "long_url": data.get("url", url),
                    "alias": data.get("alias", ""), "domain": data.get("domain", domain)}
        except requests.HTTPError as e:
            raise RuntimeError(f"TinyURL shortening failed: {e}") from e

    def _shorten_free(self, url: str) -> dict:
        try:
            resp = requests.get("https://tinyurl.com/api-create.php",
                                params={"url": url}, timeout=15)
            resp.raise_for_status()
            short_url = resp.text.strip()
            if not short_url.startswith("http"):
                raise RuntimeError(f"TinyURL unexpected response: {short_url}")
            return {"short_url": short_url, "long_url": url,
                    "alias": short_url.split("/")[-1], "domain": "tinyurl.com"}
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"TinyURL free shortening failed: {e}") from e
