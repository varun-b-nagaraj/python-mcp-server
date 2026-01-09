from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..google import gmail as gmail_client
from ..approvals import ensure_approval
from ..audit import log_action
from . import log_tool_call, response_ok, response_error


_repo = Repository(settings.db_url)


@mcp.tool()
def gmail_search(query: str, limit: int = 10) -> dict:
    """Search Gmail messages and return metadata."""
    log_tool_call("gmail_search", {"query": query, "limit": limit})
    try:
        results = gmail_client.search(settings, _repo, query, limit)
        return response_ok({"messages": results})
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def gmail_get_message(message_id: str) -> dict:
    """Return full email content (plain text preferred)."""
    log_tool_call("gmail_get_message", {"message_id": message_id})
    try:
        message = gmail_client.get_message(settings, _repo, message_id)
        return response_ok(message)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def gmail_get_thread(thread_id: str) -> dict:
    """Return all messages in a thread."""
    log_tool_call("gmail_get_thread", {"thread_id": thread_id})
    try:
        thread = gmail_client.get_thread(settings, _repo, thread_id)
        return response_ok(thread)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def gmail_create_draft(to: str, subject: str, body: str, thread_id: str | None = None) -> dict:
    """Create an email draft only."""
    log_tool_call(
        "gmail_create_draft",
        {"to": to, "subject": subject, "body": body, "thread_id": thread_id},
    )
    try:
        draft = gmail_client.create_draft(settings, _repo, to, subject, body, thread_id)
        log_action(_repo, "gmail_create_draft", {"to": to, "subject": subject, "thread_id": thread_id}, draft)
        return response_ok(draft)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def gmail_apply_labels(
    labels: list[str],
    message_id: str | None = None,
    message_ids: list[str] | None = None,
    approval_id: int | None = None,
) -> dict:
    """Apply labels to one or more messages."""
    log_tool_call(
        "gmail_apply_labels",
        {
            "labels": labels,
            "message_id": message_id,
            "message_ids": message_ids,
            "approval_id": approval_id,
        },
    )
    ids = [message_id] if message_id else []
    if message_ids:
        ids = message_ids
    if not ids:
        return response_error("message_id_required")

    approval = ensure_approval(
        repo=_repo,
        action="gmail_apply_labels",
        payload={"message_ids": ids, "labels": labels},
        approval_id=approval_id,
    )
    if not approval.ok:
        return response_error(
            error="approval_required",
            status=approval.status,
            approval_id=approval.approval_id,
        )
    try:
        result = gmail_client.apply_labels(settings, _repo, ids, labels)
        log_action(_repo, "gmail_apply_labels", {"message_ids": ids, "labels": labels}, result)
        return response_ok(result)
    except RuntimeError as exc:
        return response_error(str(exc))
