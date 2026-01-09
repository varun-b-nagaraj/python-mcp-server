from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..google import oauth
from . import log_tool_call, response_ok, response_error


_repo = Repository(settings.db_url)


@mcp.tool()
def auth_google_start() -> dict:
    """Start Google OAuth flow and return an authorization URL."""
    log_tool_call("auth_google_start", {})
    try:
        data = oauth.start_oauth(settings, _repo)
        return response_ok(data)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def auth_status(approval_id: str | None = None) -> dict:
    """Return OAuth status for an approval_id or current connection status."""
    log_tool_call("auth_status", {"approval_id": approval_id})
    if approval_id:
        data = oauth.get_oauth_status(settings, _repo, approval_id)
        return response_ok(data)
    # legacy path: check token table directly for connected state
    token_row = _repo.get_oauth_tokens(oauth.GOOGLE_OAUTH_PROVIDER)
    scopes_raw = token_row.get("scopes") if token_row else None
    data = {
        "google_connected": bool(token_row),
        "expiry": token_row.get("expiry") if token_row else None,
        "scopes": [scope for scope in scopes_raw.split(",") if scope] if scopes_raw else [],
    }
    # previous implementation (kept for reference)
    # data = {"google_connected": bool(token_row)}
    return response_ok(data)
