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
        data = oauth.start_oauth(settings)
        return response_ok(data)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def auth_google_callback(code: str) -> dict:
    """Exchange OAuth code for tokens and store them."""
    log_tool_call("auth_google_callback", {"code": code})
    try:
        data = oauth.exchange_code(settings, _repo, code)
        return response_ok(data)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def auth_status() -> dict:
    """Return connection status and token expiry information."""
    log_tool_call("auth_status", {})
    token_row = _repo.get_oauth_tokens(oauth.GOOGLE_OAUTH_PROVIDER)
    scopes_raw = token_row.get("scopes") if token_row else None
    data = {
        "google_connected": bool(token_row),
        "expiry": token_row.get("expiry") if token_row else None,
        "scopes": [scope for scope in scopes_raw.split(",") if scope] if scopes_raw else [],
    }
    return response_ok(data)
