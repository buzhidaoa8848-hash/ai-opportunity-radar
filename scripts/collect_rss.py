"""
RSS news collector.
Fetches and parses RSS feeds using feedparser.
"""
import os
import hashlib
from datetime import datetime

import feedparser
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_sources_config() -> dict:
    path = os.path.join(CONFIG_DIR, "sources.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_feed(name: str, url: str, max_items: int = 20) -> list[dict]:
    """Fetch and parse a single RSS feed."""
    feed = feedparser.parse(url)

    if feed.bozo and not feed.entries:
        raise Exception(f"Feed parse error: {feed.bozo_exception}")

    items = []
    for entry in feed.entries[:max_items]:
        link = entry.get("link", "")
        item_id = hashlib.md5((name + link).encode()).hexdigest()[:12]

        published = entry.get("published", "") or entry.get("updated", "")
        if published:
            try:
                # feedparser may return a struct_time or string
                if hasattr(published, "tm_year"):
                    published = datetime(*published[:6]).isoformat()
                else:
                    from email.utils import parsedate_to_datetime
                    published = parsedate_to_datetime(published).isoformat()
            except Exception:
                pass

        items.append({
            "id": item_id,
            "type": "news",
            "title": entry.get("title", "").strip(),
            "url": link,
            "description": entry.get("summary", "") or entry.get("description", ""),
            "source": name,
            "matched_query": name,
            "published_at": published,
            "raw": entry,
        })

    return items


def collect_rss() -> list[dict]:
    """Main entry: collect RSS items from all configured feeds."""
    config = load_sources_config()
    rss_config = config.get("rss", {})

    if not rss_config.get("enabled", False):
        print("[rss] RSS source is disabled, skipping.")
        return []

    feeds = rss_config.get("feeds", [])
    max_items = rss_config.get("max_items_per_feed", 20)

    all_items = []
    for feed_cfg in feeds:
        name = feed_cfg.get("name", "Unknown")
        url = feed_cfg.get("url", "")
        print(f"[rss] Fetching: {name}")
        try:
            results = fetch_feed(name, url, max_items=max_items)
            all_items.extend(results)
            print(f"[rss]   -> {len(results)} items")
        except Exception as e:
            print(f"[rss] WARNING: Failed to fetch '{name}': {e}")

    return all_items


if __name__ == "__main__":
    items = collect_rss()
    print(f"Total RSS items collected: {len(items)}")
