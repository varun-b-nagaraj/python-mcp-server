from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..assistant import service as assistant_service
from ..assistant.models import EmailSummary, MeetingBrief, DraftEmail
from . import log_tool_call, response_ok, response_error


_repo = Repository(settings.db_url)


@mcp.tool()
def summarize_email(message_id: str) -> dict:
    """Summarize an email and store assistant memory."""
    log_tool_call("summarize_email", {"message_id": message_id})
    try:
        summary = assistant_service.summarize_email(settings, _repo, message_id)
        return response_ok(EmailSummary(**summary).model_dump())
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def meeting_brief(event_id: str) -> dict:
    """Prepare a meeting brief."""
    log_tool_call("meeting_brief", {"event_id": event_id})
    try:
        brief = assistant_service.meeting_brief(settings, _repo, event_id)
        return response_ok(MeetingBrief(**brief).model_dump())
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def compose_email_reply(context: str, tone: str | None = None) -> dict:
    """Generate an email reply draft (never sends)."""
    log_tool_call("compose_email_reply", {"context": context, "tone": tone})
    draft = assistant_service.compose_email_reply(context, tone)
    return response_ok(DraftEmail(**draft).model_dump())
