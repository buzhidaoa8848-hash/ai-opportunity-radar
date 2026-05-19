"""
GitHub repository collector.
Searches GitHub for repositories matching configured queries.
"""
import os
import hashlib
from datetime import datetime
from typing import Optional

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_sources_config() -> dict:
    path = os.path.join(CONFIG_DIR, "sources.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def search_github(
    query: str,
    max_results: int = 10,
    token: Optional[str] = None,
) -> list[dict]:
    """Search GitHub repositories API for a given query."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": max_results,
    }

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for repo in data.get("items", []):
        item_id = hashlib.md5(repo["html_url"].encode()).hexdigest()[:12]
        items.append({
            "id": item_id,
            "type": "github",
            "title": repo.get("full_name", ""),
            "url": repo.get("html_url", ""),
            "description": repo.get("description") or "",
            "source": "GitHub",
            "matched_query": query,
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language") or "",
            "updated_at": repo.get("updated_at", ""),
            "raw": repo,
        })

    return items


def collect_github() -> list[dict]:
    """Main entry: collect GitHub repos for all configured queries."""
    config = load_sources_config()
    gh_config = config.get("github", {})

    if not gh_config.get("enabled", False):
        print("[github] GitHub source is disabled, skipping.")
        return []

    token = os.getenv("GITHUB_TOKEN") or None
    queries = gh_config.get("queries", [])
    max_results = gh_config.get("max_results_per_query", 10)

    all_items = []
    for query in queries:
        print(f"[github] Searching: {query}")
        try:
            results = search_github(query, max_results=max_results, token=token)
            all_items.extend(results)
            print(f"[github]   -> {len(results)} results")
        except requests.HTTPError as e:
            print(f"[github] WARNING: HTTP error for query '{query}': {e}")
        except requests.RequestException as e:
            print(f"[github] WARNING: Request failed for query '{query}': {e}")

    return all_items


if __name__ == "__main__":
    items = collect_github()
    print(f"Total GitHub items collected: {len(items)}")
