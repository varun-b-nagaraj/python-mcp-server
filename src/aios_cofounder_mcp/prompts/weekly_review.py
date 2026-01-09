from __future__ import annotations

from ..server import mcp


@mcp.prompt("weekly_review")
def weekly_review_prompt() -> str:
    return (
        "You are preparing a weekly review summary.\n"
        "Tools to use: gmail_search, calendar_list_events, assistant://notes, assistant://audit.\n"
        "Process: summarize key email threads, upcoming meetings, and notable actions.\n"
        "Output JSON schema: {\"summary\": \"...\", \"highlights\": [..], \"risks\": [..], \"next_actions\": [..]}\n"
        "Do not perform any external actions."
    )
