from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..web import search as web_search_client
from ..web import fetch as web_fetch_client
from . import log_tool_call, response_ok, response_error


@mcp.tool()
def web_search(query: str, limit: int = 5) -> dict:
    """Perform a web search and return top results."""
    log_tool_call("web_search", {"query": query, "limit": limit})
    try:
        results = web_search_client.search(settings, query, limit=limit)
        return response_ok({"results": results})
    except Exception as exc:
        return response_error(f"web_search_failed:{exc}")


@mcp.tool()
def web_fetch(url: str) -> dict:
    """Fetch page content and extract readable text."""
    log_tool_call("web_fetch", {"url": url})
    try:
        result = web_fetch_client.fetch(settings, url)
        return response_ok(result)
    except Exception as exc:
        return response_error(f"web_fetch_failed:{exc}")
