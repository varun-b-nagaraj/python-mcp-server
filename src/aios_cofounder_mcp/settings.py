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
    google_redirect_uri: str | None
    google_scopes: List[str]
    web_user_agent: str
    web_timeout_seconds: int


def _parse_scopes(raw: str | None) -> List[str]:
    if not raw:
        return [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/contacts",
        ]
    return [scope.strip() for scope in raw.split(",") if scope.strip()]


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        db_url=os.getenv("DB_URL", "sqlite:///./aios_cofounder_mcp.db"),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        google_redirect_uri=os.getenv("GOOGLE_REDIRECT_URI"),
        google_scopes=_parse_scopes(os.getenv("GOOGLE_SCOPES")),
        web_user_agent=os.getenv("WEB_USER_AGENT", "aios-cofounder-mcp/0.1"),
        web_timeout_seconds=int(os.getenv("WEB_TIMEOUT_SECONDS", "12")),
    )


settings = load_settings()
