from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..google import gmail as gmail_client


_repo = Repository(settings.db_url)


@mcp.resource("gmail://thread/{thread_id}")
def gmail_thread(thread_id: str) -> dict:
    try:
        return gmail_client.get_thread(settings, _repo, thread_id)
    except RuntimeError as exc:
        return {"error": str(exc)}
