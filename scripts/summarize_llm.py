"""
LLM-powered item summarizer.
Uses OpenAI-compatible API to generate human-readable insights for each item.
Gracefully degrades if no LLM API key is configured.
"""
import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


def _call_llm(prompt: str) -> Optional[str]:
    """Call the OpenAI-compatible chat completions endpoint."""
    if not LLM_API_KEY:
        return None

    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI opportunity analyst. Be concise."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 300,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[llm] WARNING: LLM call failed: {e}")
        return None


def summarize_item(item: dict) -> dict:
    """Generate LLM summary for a single item. Returns None fields if LLM unavailable."""
    title = item.get("title", "")
    desc = item.get("description", "")
    item_type = item.get("type", "")
    source = item.get("source", "")

    prompt = f"""Analyze this {item_type} from {source}:

Title: {title}
Description: {desc}

Provide a concise analysis. Return exactly 3 lines:
Line 1 — Why it matters (max 100 chars)
Line 2 — Connection to me: a builder/researcher interested in AI agents, multimodal learning, quant finance, and career opportunities (max 80 chars)
Line 3 — Suggested action (max 100 chars)

Format:
why: <text>
connection: <text>
action: <text>"""

    result = {
        "why_it_matters": "",
        "connection_to_me": "",
        "suggested_action": "",
    }

    response = _call_llm(prompt)
    if response is None:
        return result

    for line in response.split("\n"):
        line = line.strip()
        if line.lower().startswith("why:"):
            result["why_it_matters"] = line[4:].strip()
        elif line.lower().startswith("connection:"):
            result["connection_to_me"] = line[11:].strip()
        elif line.lower().startswith("action:"):
            result["suggested_action"] = line[7:].strip()

    return result


def summarize_items(items: list[dict], top_n: int = 10) -> None:
    """Add LLM summaries to the top N items in place."""
    if not LLM_API_KEY:
        print("[llm] No LLM_API_KEY configured — using rule-based fallback.")
        return

    ranked = sorted(items, key=lambda x: x.get("final_score", 0), reverse=True)
    print(f"[llm] Generating summaries for top {top_n} items...")

    for i, item in enumerate(ranked[:top_n]):
        print(f"[llm]   Summarizing ({i + 1}/{top_n}): {item.get('title', '')[:60]}...")
        summary = summarize_item(item)
        item["why_it_matters"] = summary["why_it_matters"]
        item["connection_to_me"] = summary["connection_to_me"]
        item["suggested_action"] = summary["suggested_action"]


def _rule_fallback(item: dict) -> dict:
    """Generate rule-based summary when LLM is unavailable."""
    title = item.get("title", "")
    desc = item.get("description", "")
    item_type = item.get("type", "")
    source = item.get("source", "")
    score = item.get("final_score", 0)
    stars = item.get("stars", 0)

    if item_type == "github":
        why = f"GitHub project with {stars} stars — potential tool or reference implementation."
        connection = f"Aligns with your interest in building with open-source AI tools."
        if "agent" in (title + desc).lower():
            action = "Clone the repo and study the agent architecture."
        elif "rag" in (title + desc).lower():
            action = "Evaluate if this RAG approach fits your knowledge base project."
        else:
            action = "Star the repo and review the README for applicability."
    elif item_type == "paper":
        why = f"arXiv paper from {source} — may advance your research area."
        connection = "Relevant to your multimodal / affective computing research track."
        if "depression" in (title + desc).lower():
            action = "Add to literature review for multimodal depression detection."
        elif "small sample" in (title + desc).lower():
            action = "Review methodology for your small-sample learning research."
        else:
            action = "Read abstract and decide whether to include in your survey."
    else:
        why = f"News item from {source} — may signal a trend or opportunity."
        connection = "Keeps you informed on AI industry developments."
        if "hacker news" in source.lower():
            action = "Check HN comments for community insights and discussion."
        else:
            action = "Skim the article for actionable takeaways."

    return {
        "why_it_matters": why,
        "connection_to_me": connection,
        "suggested_action": action,
    }


def apply_fallback_summaries(items: list[dict], top_n: int = 10) -> None:
    """Apply rule-based summaries to top N items that lack LLM summaries."""
    ranked = sorted(items, key=lambda x: x.get("final_score", 0), reverse=True)
    for item in ranked[:top_n]:
        if not item.get("why_it_matters"):
            summary = _rule_fallback(item)
            item["why_it_matters"] = summary["why_it_matters"]
            item["connection_to_me"] = summary["connection_to_me"]
            item["suggested_action"] = summary["suggested_action"]


if __name__ == "__main__":
    # Quick test
    item = {
        "type": "github",
        "title": "langchain-ai/langgraph",
        "description": "Build resilient language agents as graphs.",
        "source": "GitHub",
        "final_score": 8.5,
        "stars": 15000,
    }
    result = summarize_item(item)
    print("LLM result:", result)
    print("Fallback:", _rule_fallback(item))
