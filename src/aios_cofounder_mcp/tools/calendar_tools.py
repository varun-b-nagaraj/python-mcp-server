from __future__ import annotations

from typing import Any

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..google import calendar as calendar_client
from ..approvals import ensure_approval
from ..audit import log_action
from . import log_tool_call, response_ok, response_error


_repo = Repository(settings.db_url)


@mcp.tool()
def calendar_list_events(start: str, end: str) -> dict:
    """List calendar events in a time range."""
    log_tool_call("calendar_list_events", {"start": start, "end": end})
    try:
        events = calendar_client.list_events(settings, _repo, start, end)
        return response_ok({"events": events})
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def calendar_find_free_slots(duration_minutes: int, window_start: str, window_end: str) -> dict:
    """Find available time slots in a range."""
    log_tool_call(
        "calendar_find_free_slots",
        {
            "duration_minutes": duration_minutes,
            "window_start": window_start,
            "window_end": window_end,
        },
    )
    try:
        slots = calendar_client.find_free_slots(settings, _repo, duration_minutes, window_start, window_end)
        return response_ok(slots)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def calendar_create_event(
    title: str,
    start: str,
    end: str,
    attendees: list[str],
    approval_id: int | None = None,
) -> dict:
    """Create a calendar event (requires approval)."""
    log_tool_call(
        "calendar_create_event",
        {"title": title, "start": start, "end": end, "attendees": attendees, "approval_id": approval_id},
    )
    approval = ensure_approval(
        repo=_repo,
        action="calendar_create_event",
        payload={"title": title, "start": start, "end": end, "attendees": attendees},
        approval_id=approval_id,
    )
    if not approval.ok:
        return response_error("approval_required", status=approval.status, approval_id=approval.approval_id)
    try:
        event = calendar_client.create_event(settings, _repo, title, start, end, attendees)
        log_action(_repo, "calendar_create_event", {"title": title, "start": start, "end": end}, event)
        return response_ok(event)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def calendar_update_event(event_id: str, changes: dict[str, Any], approval_id: int | None = None) -> dict:
    """Update event details (requires approval)."""
    log_tool_call(
        "calendar_update_event",
        {"event_id": event_id, "changes": changes, "approval_id": approval_id},
    )
    approval = ensure_approval(
        repo=_repo,
        action="calendar_update_event",
        payload={"event_id": event_id, "changes": changes},
        approval_id=approval_id,
    )
    if not approval.ok:
        return response_error("approval_required", status=approval.status, approval_id=approval.approval_id)
    try:
        event = calendar_client.update_event(settings, _repo, event_id, changes)
        log_action(_repo, "calendar_update_event", {"event_id": event_id, "changes": changes}, event)
        return response_ok(event)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def calendar_cancel_event(event_id: str, approval_id: int | None = None) -> dict:
    """Cancel an event (requires approval)."""
    log_tool_call("calendar_cancel_event", {"event_id": event_id, "approval_id": approval_id})
    approval = ensure_approval(
        repo=_repo,
        action="calendar_cancel_event",
        payload={"event_id": event_id},
        approval_id=approval_id,
    )
    if not approval.ok:
        return response_error("approval_required", status=approval.status, approval_id=approval.approval_id)
    try:
        result = calendar_client.cancel_event(settings, _repo, event_id)
        log_action(_repo, "calendar_cancel_event", {"event_id": event_id}, result)
        return response_ok(result)
    except RuntimeError as exc:
        return response_error(str(exc))
