from __future__ import annotations

from typing import Any

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..audit import log_action
from . import log_tool_call, response_ok, response_error


_repo = Repository(settings.db_url)


@mcp.tool()
def approval_request(action: str, payload: dict[str, Any]) -> dict:
    """Create a pending approval record."""
    log_tool_call("approval_request", {"action": action, "payload": payload})
    approval_id = _repo.create_approval(action, payload)
    result = {"approval_id": approval_id, "status": "pending"}
    log_action(_repo, "approval_request", {"action": action}, result)
    return response_ok(result)


@mcp.tool()
def approval_resolve(approval_id: int, decision: str) -> dict:
    """Approve or deny an action."""
    log_tool_call("approval_resolve", {"approval_id": approval_id, "decision": decision})
    if decision not in {"approved", "denied"}:
        return response_error("invalid_decision")
    record = _repo.resolve_approval(approval_id, decision)
    if not record:
        return response_error("approval_not_found")
    log_action(_repo, "approval_resolve", {"approval_id": approval_id, "decision": decision}, record)
    return response_ok(record)
