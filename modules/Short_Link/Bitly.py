from typing import Optional
import requests

from utils.config import get_api_key
from utils.helpers import is_valid_url
from utils.logger import get_logger

logger = get_logger(__name__)

_API_BASE = "https://api-ssl.bitly.com/v4"


class BitlyShortener:
    """Bitly provider for URL shortening, expansion, and analytics."""

    def __init__(self) -> None:
        self.api_key = get_api_key("BITLY_API_KEY")
        self._headers = {"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json"}
        self._group_guid: Optional[str] = None
        logger.info("BitlyShortener initialized.")

    def _get_group_guid(self) -> str:
        if self._group_guid:
            return self._group_guid
        try:
            resp = requests.get(f"{_API_BASE}/user", headers=self._headers, timeout=10)
            resp.raise_for_status()
            self._group_guid = resp.json().get("default_group_guid", "")
            return self._group_guid
        except Exception as e:
            raise RuntimeError(f"Could not fetch Bitly account info: {e}") from e

    def shorten(self, url: str, title: Optional[str] = None,
                domain: str = "bit.ly") -> dict:
        """Shorten a long URL to a Bitlink.

        Args:
            url: The long URL to shorten.
            title: Optional human-readable title.
            domain: Domain to use. Defaults to 'bit.ly'.

        Returns:
            Dict with 'short_url', 'long_url', 'id', 'created_at'.

        Raises:
            ValueError: If url is empty or invalid.
            RuntimeError: If the API call fails.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")
        if not is_valid_url(url):
            raise ValueError(f"Invalid URL: '{url}'. Must start with http:// or https://")

        payload: dict = {"long_url": url, "domain": domain,
                         "group_guid": self._get_group_guid()}
        if title:
            payload["title"] = title

        try:
            resp = requests.post(f"{_API_BASE}/shorten", json=payload,
                                 headers=self._headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return {"short_url": data.get("link", ""), "long_url": data.get("long_url", url),
                    "id": data.get("id", ""), "created_at": data.get("created_at", "")}
        except requests.HTTPError as e:
            raise RuntimeError(f"Bitly shortening failed: {e}") from e

    def expand(self, short_url: str) -> str:
        """Expand a Bitly short URL back to its original long URL."""
        if not short_url or not short_url.strip():
            raise ValueError("short_url cannot be empty.")
        bitlink_id = short_url.replace("https://", "").replace("http://", "")
        try:
            resp = requests.get(f"{_API_BASE}/expand",
                                params={"bitlink_id": bitlink_id},
                                headers=self._headers, timeout=10)
            resp.raise_for_status()
            return resp.json().get("long_url", "")
        except requests.HTTPError as e:
            raise RuntimeError(f"Bitly expand failed: {e}") from e

    def get_clicks(self, short_url: str, unit: str = "day", units: int = 30) -> dict:
        """Retrieve click analytics for a Bitlink."""
        if not short_url or not short_url.strip():
            raise ValueError("short_url cannot be empty.")
        valid_units = {"minute", "hour", "day", "week", "month"}
        if unit not in valid_units:
            raise ValueError(f"unit must be one of {valid_units}.")
        bitlink_id = short_url.replace("https://", "").replace("http://", "")
        try:
            resp = requests.get(f"{_API_BASE}/bitlinks/{bitlink_id}/clicks",
                                params={"unit": unit, "units": units},
                                headers=self._headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {"total_clicks": sum(i.get("clicks", 0)
                                        for i in data.get("link_clicks", [])),
                    "link_clicks": data.get("link_clicks", [])}
        except requests.HTTPError as e:
            raise RuntimeError(f"Bitly analytics failed: {e}") from e

    def list_bitlinks(self, size: int = 50) -> list[dict]:
        """List Bitlinks in the account's default group."""
        try:
            resp = requests.get(f"{_API_BASE}/groups/{self._get_group_guid()}/bitlinks",
                                params={"size": min(size, 100)},
                                headers=self._headers, timeout=15)
            resp.raise_for_status()
            return [{"id": l.get("id", ""), "link": l.get("link", ""),
                     "long_url": l.get("long_url", ""), "title": l.get("title", ""),
                     "created_at": l.get("created_at", ""), "clicks": l.get("clicks", 0)}
                    for l in resp.json().get("links", [])]
        except requests.HTTPError as e:
            raise RuntimeError(f"Bitly list failed: {e}") from e
