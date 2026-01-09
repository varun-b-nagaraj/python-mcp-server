from __future__ import annotations

from typing import Any

from ..google import gmail as gmail_client
from ..google import calendar as calendar_client
from ..storage.repo import Repository
from ..settings import Settings


def _trim(text: str | None, limit: int = 400) -> str:
    if not text:
        return ""
    cleaned = " ".join(text.split())
    return cleaned[:limit]


def summarize_email(settings: Settings, repo: Repository, message_id: str) -> dict[str, Any]:
    message = gmail_client.get_message(settings, repo, message_id)
    summary = _trim(message.get("text") or message.get("snippet") or "", 400)
    note = repo.add_note(source=f"gmail:{message_id}", summary=summary)
    return {
        "message_id": message_id,
        "summary": summary,
        "note_id": int(note.get("id", 0)),
    }


def meeting_brief(settings: Settings, repo: Repository, event_id: str) -> dict[str, Any]:
    event = calendar_client.get_event(settings, repo, event_id)
    attendees = [att.get("email") for att in event.get("attendees", []) if att.get("email")]
    purpose = event.get("summary")
    recent_emails: list[dict[str, Any]] = []
    if attendees:
        query = " OR ".join(f"from:{email} OR to:{email}" for email in attendees[:3])
        try:
            recent_emails = gmail_client.search(settings, repo, query, limit=5)
        except RuntimeError:
            recent_emails = []
    talking_points = []
    if purpose:
        talking_points.append(f"Clarify outcomes for {purpose}")
    if attendees:
        talking_points.append("Align on next steps and ownership")
    return {
        "event_id": event_id,
        "attendees": attendees,
        "purpose": purpose,
        "recent_emails": recent_emails,
        "talking_points": talking_points,
    }


def compose_email_reply(context: str, tone: str | None) -> dict[str, Any]:
    tone_hint = tone or "professional"
    body = (
        f"Thanks for the update.\n\n"
        f"{context.strip()}\n\n"
        f"Let me know the next steps.\n"
    )
    return {
        "subject": "Re:",
        "body": body,
        "tone": tone_hint,
    }
