from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..google import calendar as calendar_client


_repo = Repository(settings.db_url)


@mcp.resource("calendar://event/{event_id}")
def calendar_event(event_id: str) -> dict:
    try:
        return calendar_client.get_event(settings, _repo, event_id)
    except RuntimeError as exc:
        return {"error": str(exc)}
