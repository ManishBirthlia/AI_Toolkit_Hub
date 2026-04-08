import os
import sys
import time
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.Internet.GoogleTrends import GoogleTrends

import logging
logging.basicConfig(level=logging.INFO)


def test_google_trends():
    """Fetch top 5 Google Trends for India and print structured results."""
    print("=" * 60)
    print("  Google Trends — Top 5 Trending Topics")
    print("=" * 60)

    gt = GoogleTrends(geo="IN")

    start = time.time()
    try:
        trends = gt.fetch_trends(top_n=5, search_depth=3)
        elapsed = time.time() - start

        print(f"\nFetched {len(trends)} trends in {elapsed:.2f}s\n")

        for trend in trends:
            print(f"{'─' * 50}")
            print(f"  #{trend.rank}  {trend.title}")
            print(f"  Traffic : {trend.approximate_traffic}")
            print(f"  Date    : {trend.published}")
            print(f"  News URL: {trend.news_url}")

            if trend.search_results:
                print(f"  Web Results:")
                for hit in trend.search_results:
                    print(f"    • {hit.title}")
                    print(f"      {hit.url}")
                    print(f"      {hit.snippet[:120]}...")
            else:
                print(f"  (no web results found)")
            print()

    except Exception as e:
        print(f"\nError: {e}\n")


def test_google_trends_as_json():
    """Fetch trends and output as JSON (useful for piping to other tools)."""
    print("=" * 60)
    print("  Google Trends — JSON Output")
    print("=" * 60)

    gt = GoogleTrends(geo="US")

    try:
        data = gt.fetch_trends_as_dicts(top_n=5, search_depth=2)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\nError: {e}\n")


if __name__ == "__main__":
    test_google_trends()
    # Uncomment below to also see the raw JSON output:
    # test_google_trends_as_json()
