from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..google import oauth


_repo = Repository(settings.db_url)


@mcp.resource("connections://status")
def connections_status() -> dict:
    token_row = _repo.get_oauth_tokens(oauth.GOOGLE_OAUTH_PROVIDER)
    scopes_raw = token_row.get("scopes") if token_row else None
    return {
        "google_connected": bool(token_row),
        "expiry": token_row.get("expiry") if token_row else None,
        "scopes": [scope for scope in scopes_raw.split(",") if scope] if scopes_raw else [],
    }


@mcp.resource("assistant://companies")
def assistant_companies() -> dict:
    return {"companies": _repo.list_companies()}


@mcp.resource("assistant://contacts")
def assistant_contacts() -> dict:
    return {"contacts": _repo.list_contacts()}


@mcp.resource("assistant://notes")
def assistant_notes() -> dict:
    return {"notes": _repo.list_notes()}


@mcp.resource("assistant://audit")
def assistant_audit() -> dict:
    return {"audit": _repo.list_audit()}
