from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    log_level: str
    db_url: str
    google_client_id: str | None
    google_client_secret: str | None
    oauth_redirect_base_url: str | None
    google_scopes: List[str]
    oauth_state_ttl_seconds: int
    web_user_agent: str
    web_timeout_seconds: int


def _parse_scopes(raw: str | None) -> List[str]:
    if not raw:
        return [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/contacts.readonly",
        ]
    if " " in raw and "," not in raw:
        return [scope.strip() for scope in raw.split(" ") if scope.strip()]
    normalized = raw.replace(" ", ",")
    return [scope.strip() for scope in normalized.split(",") if scope.strip()]


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        db_url=os.getenv("DB_URL", "sqlite:///./aios_cofounder_mcp.db"),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        oauth_redirect_base_url=os.getenv("OAUTH_REDIRECT_BASE_URL"),
        google_scopes=_parse_scopes(os.getenv("GOOGLE_OAUTH_SCOPES")),
        oauth_state_ttl_seconds=int(os.getenv("OAUTH_STATE_TTL_SECONDS", "600")),
        web_user_agent=os.getenv("WEB_USER_AGENT", "aios-cofounder-mcp/0.1"),
        web_timeout_seconds=int(os.getenv("WEB_TIMEOUT_SECONDS", "12")),
    )


settings = load_settings()


def get_redirect_uri(settings: Settings) -> str | None:
    if not settings.oauth_redirect_base_url:
        return None
    return settings.oauth_redirect_base_url.rstrip("/") + "/oauth/google/callback"
