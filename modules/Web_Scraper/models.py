"""
models.py — Pydantic v2 data models.
Single source of truth for data shapes flowing through the pipeline.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


# ── Enumerations ──────────────────────────────────────────────────────────────

class ScrapingStatus(str, Enum):
    SUCCESS   = "success"
    FAILED    = "failed"
    SKIPPED   = "skipped"
    TIMEOUT   = "timeout"
    BLOCKED   = "blocked"


# ── Per-page models ───────────────────────────────────────────────────────────

class PageMetadata(BaseModel):
    """Metadata extracted from <head> tags."""
    description: Optional[str] = None
    keywords:    Optional[str] = None
    author:      Optional[str] = None
    og_title:    Optional[str] = None
    og_image:    Optional[str] = None
    canonical:   Optional[str] = None


class ScrapedPage(BaseModel):
    """Raw extraction result for a single URL — before scoring."""
    url:         str
    title:       str                       = ""
    headings:    List[str]                 = Field(default_factory=list)
    content:     str                       = ""
    summary:     str                       = ""
    metadata:    PageMetadata              = Field(default_factory=PageMetadata)
    images:      List[str]                 = Field(default_factory=list)
    internal_links: List[str]              = Field(default_factory=list)
    status:      ScrapingStatus            = ScrapingStatus.SUCCESS
    error:       Optional[str]             = None
    word_count:  int                       = 0

    @field_validator("content", mode="before")
    @classmethod
    def truncate_content(cls, v: str) -> str:
        """Hard-cap stored content to avoid huge payloads."""
        return v[:15_000] if v else ""


class ScoredResult(BaseModel):
    """Final result enriched with a relevance score — what we return to callers."""
    url:     str
    title:   str
    summary: str
    content: str
    score:   float = Field(ge=0.0, le=1.0)
    status:  ScrapingStatus = ScrapingStatus.SUCCESS


# ── Top-level output ──────────────────────────────────────────────────────────

class ScraperOutput(BaseModel):
    """The JSON envelope returned by the entire pipeline."""
    query:          str
    total_scraped:  int
    total_returned: int
    results:        List[ScoredResult]
