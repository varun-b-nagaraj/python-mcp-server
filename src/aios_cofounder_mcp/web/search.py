from __future__ import annotations

from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..settings import Settings


def search(settings: Settings, query: str, limit: int = 5) -> list[dict[str, Any]]:
    url = "https://duckduckgo.com/html/"
    headers = {"User-Agent": settings.web_user_agent}
    with httpx.Client(timeout=settings.web_timeout_seconds, headers=headers, follow_redirects=True) as client:
        response = client.get(url, params={"q": query})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results: list[dict[str, Any]] = []
    for result in soup.select(".result"):
        link = result.select_one("a.result__a")
        snippet = result.select_one(".result__snippet")
        if not link:
            continue
        results.append(
            {
                "title": link.get_text(strip=True),
                "url": link.get("href"),
                "snippet": snippet.get_text(strip=True) if snippet else None,
            }
        )
        if len(results) >= limit:
            break
    return results
