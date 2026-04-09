"""
browser.py — Web browsing tools for the Jarvis AI agent.

Provides helpers to perform web searches, open URLs in the default
browser, and scrape / read the text content of web pages.
"""

import webbrowser
import urllib.parse

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False
    print("[browser] ⚠  requests not installed — get_page_content() will not work.  "
          "pip install requests")

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False
    print("[browser] ⚠  beautifulsoup4 not installed — HTML parsing will be limited.  "
          "pip install beautifulsoup4")


# ── Public Tool Functions ────────────────────────────────────────────────────

def search_web(query: str, engine: str = "google") -> dict:
    """Open a web search in the default browser.

    Constructs the search URL and opens it via ``webbrowser.open()``.

    Args:
        query:  The search query string.
        engine: Search engine to use — 'google' (default), 'bing', or 'duckduckgo'.

    Returns:
        dict with the search URL opened on success.
    """
    try:
        encoded_query = urllib.parse.quote_plus(query)
        engines = {
            "google": f"https://www.google.com/search?q={encoded_query}",
            "bing": f"https://www.bing.com/search?q={encoded_query}",
            "duckduckgo": f"https://duckduckgo.com/?q={encoded_query}",
        }
        url = engines.get(engine.lower(), engines["google"])
        webbrowser.open(url)
        return {"success": True, "result": f"Opened search for '{query}' → {url}", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def open_url(url: str) -> dict:
    """Open a URL in the user's default web browser.

    Args:
        url: Full URL to open (must start with http:// or https://).

    Returns:
        dict confirming the URL was opened.
    """
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return {"success": True, "result": f"Opened {url}", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def get_page_content(url: str, max_chars: int = 5000) -> dict:
    """Fetch a web page and extract its visible text content.

    Uses ``requests`` to download the page and ``BeautifulSoup`` to strip
    HTML tags.  Falls back to raw text if BS4 is unavailable.

    Args:
        url:       Full URL to fetch.
        max_chars: Maximum number of characters to return (default 5000).

    Returns:
        dict with the extracted text in ``result``.
    """
    if not _REQUESTS_AVAILABLE:
        return {"success": False, "result": None,
                "error": "requests is not installed. Run: pip install requests"}

    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        if _BS4_AVAILABLE:
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove script / style noise
            for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
        else:
            # Crude fallback — just strip angle-bracket tags
            import re
            text = re.sub(r"<[^>]+>", "", resp.text)

        # Truncate to max_chars
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[…truncated]"

        return {"success": True, "result": text, "error": None}
    except requests.RequestException as exc:
        return {"success": False, "result": None, "error": f"HTTP error: {exc}"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "search_web",
            "description": "Open a web search in the default browser for the given query.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string."
                    },
                    "engine": {
                        "type": "string",
                        "enum": ["google", "bing", "duckduckgo"],
                        "description": "Search engine to use. Defaults to 'google'."
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "open_url",
            "description": "Open a URL in the user's default web browser.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to open (e.g. 'https://example.com')."
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "get_page_content",
            "description": "Fetch a web page and extract its visible text content, stripping HTML tags.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the page to fetch."
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters of text to return. Defaults to 5000."
                    }
                },
                "required": ["url"]
            }
        },
    ]
