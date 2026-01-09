from __future__ import annotations

from ..server import mcp


@mcp.prompt("meeting_prep")
def meeting_prep_prompt() -> str:
    return (
        "You are preparing a concise meeting brief.\n"
        "Tools to use: calendar_list_events, calendar://event/{id}, meeting_brief, gmail_search.\n"
        "Process: fetch event details, summarize attendees and purpose, pull recent related emails, suggest talking points.\n"
        "Output JSON schema: {\"event\": {..}, \"brief\": {..}, \"talking_points\": [..]}\n"
        "Do not create, update, or cancel events without approval."
    )
