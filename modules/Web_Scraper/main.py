"""
main.py — CLI entry point + FastAPI app (ready to mount).

CLI usage
---------
    python main.py
    python main.py --query "best laptops under 1 lakh in India"
    python main.py --query "..." --output results.json

FastAPI usage
-------------
    uvicorn main:app --reload
    # Then POST /scrape  {"query": "best laptops under 1 lakh in India"}
    # Or  GET  /scrape?query=best+laptops+under+1+lakh+in+India
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# ── Logging setup (do this before importing project modules) ──────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

# ── Project imports ───────────────────────────────────────────────────────────
import os
import sys

# Ensure current directory is in sys.path for direct script execution
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import ScraperOutput
from pipeline import run_pipeline, run_pipeline_sync
from query_handler import prompt_user_for_query


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI app  (import only when running as an API server)
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    app = FastAPI(
        title="Web Scraper API",
        description=(
            "Accepts a search query, scrapes the most relevant pages, "
            "and returns structured JSON results ranked by relevance."
        ),
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # tighten for production
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # ── Request / response models ─────────────────────────────────────────────

    class ScrapeRequest(BaseModel):
        query: str

        model_config = {"json_schema_extra": {"example": {"query": "best laptops under 1 lakh in India"}}}

    # ── Routes ────────────────────────────────────────────────────────────────

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @app.post("/scrape", response_model=ScraperOutput, summary="Scrape via POST body")
    async def scrape_post(req: ScrapeRequest) -> ScraperOutput:
        """
        Accept a JSON body `{"query": "..."}` and return ranked scraping results.
        """
        try:
            return await run_pipeline(req.query)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception as exc:
            logging.getLogger(__name__).exception("Unhandled pipeline error")
            raise HTTPException(status_code=500, detail="Internal scraper error")

    @app.get("/scrape", response_model=ScraperOutput, summary="Scrape via query string")
    async def scrape_get(
        query: str = Query(..., description="Search query", min_length=3, max_length=300)
    ) -> ScraperOutput:
        """
        GET convenience endpoint: `/scrape?query=best+laptops+under+1+lakh+in+India`
        """
        try:
            return await run_pipeline(query)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))

except ImportError:
    # FastAPI not installed — CLI-only mode
    app = None  # type: ignore[assignment]


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def _cli() -> None:
    """Command-line interface for the scraper."""
    parser = argparse.ArgumentParser(
        prog="scraper",
        description="Web scraping pipeline — returns structured JSON results.",
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="Search query (skips interactive prompt if provided)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional path to write JSON output (e.g. results.json)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True)",
    )
    args = parser.parse_args()

    # Get query from args or prompt interactively
    raw_query: str = args.query if args.query else prompt_user_for_query()

    print(f"\n⏳  Running scraping pipeline for: \"{raw_query}\"\n")

    try:
        result: ScraperOutput = run_pipeline_sync(raw_query)
    except ValueError as exc:
        print(f"❌  Query error: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(f"❌  Pipeline error: {exc}", file=sys.stderr)
        sys.exit(2)

    # Serialise
    indent = 2 if args.pretty else None
    json_output: str = result.model_dump_json(indent=indent)

    # Print to stdout
    print("\n" + "═" * 60)
    print("📋  RESULTS")
    print("═" * 60)
    print(json_output)

    # Optionally write to file
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json_output, encoding="utf-8")
        print(f"\n💾  Results saved to: {output_path.resolve()}")

    # Quick summary to stderr
    print(
        f"\n✅  Done — {result.total_returned} results returned "
        f"(scraped {result.total_scraped} pages total)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    _cli()
