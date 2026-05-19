"""
Rule-based item scoring.
Scores each collected item and assigns a KEEP/WATCH/IGNORE level.
"""
import os
import re
from typing import Any

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_config(filename: str) -> dict:
    path = os.path.join(CONFIG_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_keyword_set(keywords_config: dict) -> set[str]:
    """Flatten all keyword categories into a single set of lowercase tokens."""
    tokens = set()
    for category, kws in keywords_config.items():
        for kw in kws:
            tokens.add(kw.lower())
    return tokens


def _text_contains_keywords(text: str, keywords: set[str]) -> int:
    """Count how many keywords appear in the given text (case-insensitive)."""
    text_lower = text.lower()
    count = 0
    for kw in keywords:
        if kw in text_lower:
            count += 1
    return count


def _score_relevance(item: dict, keywords: set[str], boost_cfg: dict) -> float:
    """Score relevance (0-10) based on keyword matches in title + description."""
    title = item.get("title", "")
    desc = item.get("description", "")
    combined = f"{title} {desc}"

    base_hits = _text_contains_keywords(combined, keywords)
    score = min(base_hits * 2.0, 8.0)

    # Extra boost for high-value keywords
    for kw in boost_cfg.get("high", []):
        if kw.lower() in combined.lower():
            score += 1.0
    for kw in boost_cfg.get("medium", []):
        if kw.lower() in combined.lower():
            score += 0.5

    return min(score, 10.0)


def _score_trend(item: dict) -> float:
    """Score trend (0-10) based on popularity signals."""
    score = 5.0  # neutral baseline

    stars = item.get("stars", 0)
    if stars >= 5000:
        score += 4.0
    elif stars >= 1000:
        score += 3.0
    elif stars >= 500:
        score += 2.0
    elif stars >= 100:
        score += 1.0

    source = item.get("source", "")
    if source == "arXiv":
        score += 1.0  # research papers have baseline trend value
    elif source == "Hacker News":
        score += 1.5

    return min(score, 10.0)


def _score_actionability(item: dict) -> float:
    """Score actionability (0-10) — can I do something with this?"""
    score = 4.0
    combined = f"{item.get('title', '')} {item.get('description', '')}".lower()

    actionable_keywords = [
        "open source", "github", "tutorial", "code", "repo",
        "intern", "hackathon", "competition", "startup", "apply",
        "dataset", "benchmark", "framework", "library", "tool",
        "实习", "招聘", "hiring",
    ]
    for kw in actionable_keywords:
        if kw in combined:
            score += 0.5

    # GitHub repos are inherently actionable (you can clone, study, fork)
    if item.get("type") == "github":
        score += 1.5
    # arXiv papers: you can read, cite, reproduce
    if item.get("type") == "paper":
        score += 1.0

    return min(score, 10.0)


def _score_portfolio(item: dict) -> float:
    """Score portfolio fit (0-10) — does this align with my research/career areas?"""
    score = 3.0
    combined = f"{item.get('title', '')} {item.get('description', '')}".lower()

    portfolio_keywords = [
        "agent", "rag", "ai coding", "claude code", "mcp",
        "multimodal", "depression", "small sample", "domain generalization",
        "affective computing", "medical ai", "emotion",
        "quant", "backtesting", "factor model",
        "intern", "startup", "hackathon", "competition",
        "实习", "创业",
    ]
    for kw in portfolio_keywords:
        if kw in combined:
            score += 0.8

    # Bonus for GitHub projects that are agent/rag/ai-coding related
    if item.get("type") == "github":
        agent_keywords = ["agent", "rag", "ai coding", "claude code", "mcp", "tool use"]
        if any(kw in combined for kw in agent_keywords):
            score += 1.5

    # Bonus for arXiv papers in multimodal/depression/domain-generalization areas
    if item.get("type") == "paper":
        research_keywords = ["multimodal", "depression", "small sample", "domain generalization", "affective"]
        if any(kw in combined for kw in research_keywords):
            score += 1.5

    return min(score, 10.0)


def _score_novelty(item: dict) -> float:
    """Score novelty (0-10) — is this fresh/emerging?"""
    score = 5.0
    title = item.get("title", "").lower()
    desc = item.get("description", "").lower()
    combined = f"{title} {desc}"

    novelty_keywords = [
        "new", "novel", "state-of-the-art", "breakthrough",
        "first", "introducing", "announcing", "released",
        "2025", "2026", "latest",
        "sota", "benchmark", "outperforms",
    ]
    for kw in novelty_keywords:
        if kw in combined:
            score += 0.5

    return min(score, 10.0)


def deduplicate(items: list[dict]) -> list[dict]:
    """Deduplicate items by URL, keeping the first occurrence."""
    seen_urls = set()
    unique = []
    for item in items:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(item)
        elif not url:
            unique.append(item)
    return unique


def score_items(items: list[dict]) -> list[dict]:
    """Score all items and assign KEEP/WATCH/IGNORE levels."""
    keywords_config = load_config("keywords.yaml")
    scoring_config = load_config("scoring.yaml")

    keywords = _build_keyword_set(keywords_config)
    weights = scoring_config.get("weights", {})
    boost_cfg = scoring_config.get("boost_keywords", {})
    thresholds = scoring_config.get("thresholds", {})

    keep_threshold = thresholds.get("keep", 8)
    watch_threshold = thresholds.get("watch", 5)

    # Deduplicate first
    items = deduplicate(items)
    print(f"[score] After dedup: {len(items)} items")

    for item in items:
        relevance = _score_relevance(item, keywords, boost_cfg)
        trend = _score_trend(item)
        actionability = _score_actionability(item)
        portfolio = _score_portfolio(item)
        novelty = _score_novelty(item)

        final_score = (
            relevance * weights.get("relevance", 0.30)
            + actionability * weights.get("actionability", 0.25)
            + trend * weights.get("trend", 0.20)
            + portfolio * weights.get("portfolio", 0.15)
            + novelty * weights.get("novelty", 0.10)
        )

        if final_score >= keep_threshold:
            level = "KEEP"
        elif final_score >= watch_threshold:
            level = "WATCH"
        else:
            level = "IGNORE"

        # Round to 1 decimal
        final_score = round(final_score, 1)
        relevance = round(relevance, 1)
        trend = round(trend, 1)
        actionability = round(actionability, 1)
        portfolio = round(portfolio, 1)
        novelty = round(novelty, 1)

        item["final_score"] = final_score
        item["level"] = level
        item["score_detail"] = {
            "relevance": relevance,
            "trend": trend,
            "actionability": actionability,
            "portfolio": portfolio,
            "novelty": novelty,
        }

    return items


if __name__ == "__main__":
    import json
    # Quick test with sample data
    sample = [
        {
            "id": "test1",
            "type": "github",
            "title": "awesome-ai-agents/agent-framework",
            "url": "https://github.com/example/agent-framework",
            "description": "An open-source multi-agent framework with RAG and tool use",
            "source": "GitHub",
            "matched_query": "llm agent",
            "stars": 2500,
            "language": "Python",
            "updated_at": "2026-05-15T10:00:00",
            "raw": {},
        },
        {
            "id": "test2",
            "type": "paper",
            "title": "Small Sample Multimodal Learning for Depression Detection from Speech and Text",
            "url": "https://arxiv.org/abs/2605.12345",
            "description": "We propose a novel domain generalization approach for multimodal depression detection with limited samples.",
            "source": "arXiv",
            "matched_query": "multimodal depression detection",
            "published_at": "2026-05-10T00:00:00",
            "authors": ["Zhang", "Li", "Wang"],
            "raw": {},
        },
    ]
    scored = score_items(sample)
    print(json.dumps(scored, indent=2, ensure_ascii=False))
