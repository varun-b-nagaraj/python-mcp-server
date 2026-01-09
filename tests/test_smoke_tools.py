import os

os.environ["DB_URL"] = "sqlite:///:memory:"

from aios_cofounder_mcp.settings import settings
from aios_cofounder_mcp.storage.db import init_db

init_db(settings.db_url)

from aios_cofounder_mcp.tools import approval_tools, assistant_tools, gmail_tools


def test_approval_request_returns_structured_response() -> None:
    result = approval_tools.approval_request("test_action", {"k": "v"})
    assert result["ok"] is True
    assert result["data"]["approval_id"] > 0


def test_compose_email_reply_returns_structured_response() -> None:
    result = assistant_tools.compose_email_reply("Please confirm timeline", tone="neutral")
    assert result["ok"] is True
    assert "body" in result["data"]


def test_gmail_search_handles_missing_connection() -> None:
    result = gmail_tools.gmail_search("from:example", limit=1)
    assert result["ok"] is False
    assert result["error"] in {
        "gmail_not_connected",
        "google_oauth_not_configured",
        "google_api_client_not_installed",
    }
