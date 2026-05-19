"""
arXiv paper collector.
Queries the arXiv API and returns parsed paper metadata.
"""
import os
import hashlib
import urllib.parse
from datetime import datetime
from typing import Optional

import feedparser
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

ARXIV_API = "http://export.arxiv.org/api/query"


def load_sources_config() -> dict:
    path = os.path.join(CONFIG_DIR, "sources.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    """Query the arXiv API and return parsed items."""
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"

    feed = feedparser.parse(url)

    items = []
    for entry in feed.entries:
        arxiv_id = entry.id.split("/abs/")[-1]
        # Strip version suffix like v1, v2
        arxiv_id = arxiv_id.split("v")[0] if "v" in arxiv_id.split("/")[-1] else arxiv_id
        item_id = hashlib.md5(entry.id.encode()).hexdigest()[:12]

        authors = [a.get("name", "") for a in entry.get("authors", [])]

        published = entry.get("published", "")
        if published:
            try:
                published = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").isoformat()
            except ValueError:
                pass

        items.append({
            "id": item_id,
            "type": "paper",
            "title": entry.get("title", "").strip().replace("\n", " "),
            "url": entry.get("link", ""),
            "description": entry.get("summary", "").strip().replace("\n", " "),
            "source": "arXiv",
            "matched_query": query,
            "published_at": published,
            "authors": authors,
            "raw": entry,
        })

    return items


def collect_arxiv() -> list[dict]:
    """Main entry: collect arXiv papers for all configured queries."""
    config = load_sources_config()
    arxiv_config = config.get("arxiv", {})

    if not arxiv_config.get("enabled", False):
        print("[arxiv] arXiv source is disabled, skipping.")
        return []

    queries = arxiv_config.get("queries", [])
    max_results = arxiv_config.get("max_results_per_query", 10)

    all_items = []
    for query in queries:
        print(f"[arxiv] Searching: {query}")
        try:
            results = search_arxiv(query, max_results=max_results)
            all_items.extend(results)
            print(f"[arxiv]   -> {len(results)} results")
        except Exception as e:
            print(f"[arxiv] WARNING: Failed for query '{query}': {e}")

    return all_items


if __name__ == "__main__":
    items = collect_arxiv()
    print(f"Total arXiv items collected: {len(items)}")
