"""
query_handler.py — Accepts, sanitises, and validates a raw user query.

Design decisions
----------------
* No external deps — only stdlib re/unicodedata.
* Returns a clean string or raises ValueError with a human-readable message.
* The validator is intentionally strict: empty, too-short, or injection-like
  queries are rejected early so nothing wasteful hits the network.
"""

import re
import unicodedata
from typing import Optional


# ── Constants ─────────────────────────────────────────────────────────────────

_MIN_LENGTH: int = 3
_MAX_LENGTH: int = 300

# Characters that are meaningless noise or potential injection vectors
_STRIP_PATTERN = re.compile(r"[^\w\s\-\',.()/&@₹$%+:]", re.UNICODE)

# Detect sequences that look like shell / SQL injection attempts
_INJECTION_PATTERN = re.compile(
    r"(--|;|DROP\s+TABLE|SELECT\s+\*|<script|javascript:|eval\()",
    re.IGNORECASE,
)


# ── Public API ────────────────────────────────────────────────────────────────

def process_query(raw_input: Optional[str]) -> str:
    """
    Accept raw user input, sanitise it, and return a clean query string.

    Parameters
    ----------
    raw_input : str | None
        Whatever the user typed (could be None, empty, or junk).

    Returns
    -------
    str
        A clean, validated query string ready for the search layer.

    Raises
    ------
    ValueError
        If the query is empty, too short, too long, or looks malicious.
    """
    if not raw_input or not isinstance(raw_input, str):
        raise ValueError("Query must be a non-empty string.")

    # 1. Unicode normalise (NFKC collapses weird look-alike characters)
    normalised: str = unicodedata.normalize("NFKC", raw_input)

    # 2. Strip leading / trailing whitespace
    cleaned: str = normalised.strip()

    # 3. Collapse internal whitespace runs into single spaces
    cleaned = re.sub(r"\s+", " ", cleaned)

    # 4. Remove characters outside the allowed set
    cleaned = _STRIP_PATTERN.sub("", cleaned)

    # 5. Post-strip whitespace again (removing chars can leave gaps)
    cleaned = cleaned.strip()

    # 6. Length validation
    if len(cleaned) < _MIN_LENGTH:
        raise ValueError(
            f"Query is too short (minimum {_MIN_LENGTH} characters). "
            f"Got: '{cleaned}'"
        )
    if len(cleaned) > _MAX_LENGTH:
        raise ValueError(
            f"Query is too long (maximum {_MAX_LENGTH} characters). "
            f"Truncate and try again."
        )

    # 7. Injection / abuse detection
    if _INJECTION_PATTERN.search(cleaned):
        raise ValueError("Query contains disallowed patterns.")

    return cleaned


def prompt_user_for_query() -> str:
    """
    Interactive CLI helper — prompts the user until a valid query is entered.
    Not used when this module is called programmatically.
    """
    while True:
        try:
            raw = input("\n🔍  Enter your search query: ").strip()
            query = process_query(raw)
            print(f"✅  Query accepted: \"{query}\"")
            return query
        except ValueError as exc:
            print(f"⚠️   Invalid query — {exc}  Please try again.")
