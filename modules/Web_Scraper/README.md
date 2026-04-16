# 🕸️ Web Scraping Pipeline

A production-ready, modular Python web scraping system that accepts a search query and returns **ranked, structured JSON results** from the most relevant pages on the internet.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│  query_handler  │  sanitise, validate, normalise input
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  search_engine  │  DuckDuckGo → top-N URLs (no API key needed)
└────────┬────────┘
         │ List[URL]
         ▼
┌─────────────────┐
│    scraper      │  httpx AsyncClient + semaphore + retry/back-off
└────────┬────────┘
         │ List[HTML]
         ▼
┌─────────────────┐
│ content_cleaner │  trafilatura → BS4 fallback → clean text + metadata
└────────┬────────┘
         │ List[ScrapedPage]
         ▼
┌──────────────────┐
│ relevance_scorer │  keyword coverage + density + domain authority + length
└────────┬─────────┘
         │ List[ScoredResult]
         ▼
    ScraperOutput (JSON)
```

## File Structure

```
scraper_project/
├── config.py            # All tuneable settings (timeouts, concurrency, etc.)
├── models.py            # Pydantic v2 data models
├── query_handler.py     # Input sanitisation & validation
├── search_engine.py     # DuckDuckGo URL discovery
├── scraper.py           # Async concurrent HTTP fetcher
├── content_cleaner.py   # HTML → clean structured data
├── relevance_scorer.py  # TF-like ranking algorithm
├── pipeline.py          # Async orchestrator
├── main.py              # CLI entry point + FastAPI app
└── requirements.txt
```

---

## Installation

```bash
# 1. Clone / copy the project directory
cd scraper_project

# 2. Create a virtual environment (uv recommended)
uv venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
uv pip install -r requirements.txt
# or: pip install -r requirements.txt
```

---

## Usage

### CLI — Interactive prompt
```bash
python main.py
# 🔍 Enter your search query: best laptops under 1 lakh in India
```

### CLI — Direct query
```bash
python main.py --query "best laptops under 1 lakh in India"
```

### CLI — Save results to file
```bash
python main.py --query "green hydrogen India 2024" --output results.json
```

### FastAPI server
```bash
uvicorn main:app --reload --port 8000

# POST
curl -X POST http://localhost:8000/scrape \
     -H "Content-Type: application/json" \
     -d '{"query": "best laptops under 1 lakh in India"}'

# GET
curl "http://localhost:8000/scrape?query=best+laptops+under+1+lakh+in+India"
```

### Programmatic (async)
```python
import asyncio
from pipeline import run_pipeline

async def main():
    result = await run_pipeline("best laptops under 1 lakh in India")
    print(result.model_dump_json(indent=2))

asyncio.run(main())
```

---

## Output Format

```json
{
  "query": "best laptops under 1 lakh in India",
  "total_scraped": 10,
  "total_returned": 5,
  "results": [
    {
      "url": "https://www.91mobiles.com/laptops/...",
      "title": "Best Laptops Under 1 Lakh in India 2024",
      "summary": "Looking for the best laptops under ₹1 lakh? Here are our top picks...",
      "content": "Full cleaned article text...",
      "score": 0.8731,
      "status": "success"
    }
  ]
}
```

---

## Configuration

All settings live in `config.py` — no environment variables needed for basic use:

| Setting | Default | Description |
|---|---|---|
| `max_search_results` | 10 | URLs fetched from DuckDuckGo |
| `concurrency_limit` | 5 | Max simultaneous HTTP connections |
| `request_timeout` | 15s | Per-request timeout |
| `max_retries` | 3 | Retry attempts with exponential back-off |
| `top_n_results` | 5 | Results returned to caller |
| `search_region` | `in-en` | DuckDuckGo region (India/English) |

---

## Extending

| Goal | Where to change |
|---|---|
| Switch search to SerpAPI | `search_engine.py` → replace `_search_duckduckgo()` |
| Add LLM summarisation | `content_cleaner.py` → replace `_make_summary()` |
| Persist results to DB | `pipeline.py` → add DB write after `score_and_rank()` |
| Add more scoring signals | `relevance_scorer.py` → add component to `_compute_score()` |
| Rate-limit per domain | `scraper.py` → add per-host semaphore map |

---

## Limitations & Production Hardening Checklist

- [ ] Add Redis-based URL cache to avoid re-scraping same pages
- [ ] Implement per-domain rate limiting (robots.txt compliance)
- [ ] Add Playwright/Pyppeteer for JS-rendered pages
- [ ] Integrate SerpAPI for more reliable search at scale
- [ ] Add structured logging (structlog / JSON logs)
- [ ] Add Prometheus metrics endpoint
- [ ] Containerise with Docker + Docker Compose
