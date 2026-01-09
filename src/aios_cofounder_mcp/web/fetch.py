from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from ..settings import Settings


def fetch(settings: Settings, url: str) -> dict[str, str | None]:
    headers = {"User-Agent": settings.web_user_agent}
    with httpx.Client(timeout=settings.web_timeout_seconds, headers=headers, follow_redirects=True) as client:
        response = client.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))
    return {
        "url": url,
        "title": soup.title.get_text(strip=True) if soup.title else None,
        "text": text,
    }
