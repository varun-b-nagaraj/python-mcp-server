from __future__ import annotations

from typing import Any

from ..settings import Settings
from ..storage.repo import Repository


GOOGLE_OAUTH_PROVIDER = "google"


def _require_oauth_config(settings: Settings) -> None:
    if not settings.google_client_id or not settings.google_client_secret:
        raise RuntimeError("google_oauth_not_configured")
    if not settings.google_redirect_uri:
        raise RuntimeError("google_redirect_uri_missing")


def _client_config(settings: Settings) -> dict[str, Any]:
    return {
        "installed": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uris": [settings.google_redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


def start_oauth(settings: Settings) -> dict[str, Any]:
    _require_oauth_config(settings)
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        _client_config(settings),
        scopes=settings.google_scopes,
        redirect_uri=settings.google_redirect_uri,
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return {"auth_url": auth_url, "state": state}


def exchange_code(settings: Settings, repo: Repository, code: str) -> dict[str, Any]:
    _require_oauth_config(settings)
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        _client_config(settings),
        scopes=settings.google_scopes,
        redirect_uri=settings.google_redirect_uri,
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    repo.save_oauth_tokens(
        provider=GOOGLE_OAUTH_PROVIDER,
        token_json=credentials.to_json(),
        scopes=settings.google_scopes,
        expiry=credentials.expiry.isoformat() if credentials.expiry else None,
    )
    return {
        "provider": GOOGLE_OAUTH_PROVIDER,
        "scopes": settings.google_scopes,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    }


def load_credentials(settings: Settings, repo: Repository):
    token_row = repo.get_oauth_tokens(GOOGLE_OAUTH_PROVIDER)
    if not token_row:
        return None
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import json

    token_info = token_row["token_json"]
    if isinstance(token_info, str):
        token_info = json.loads(token_info)
    creds = Credentials.from_authorized_user_info(
        info=token_info,
        scopes=settings.google_scopes,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        repo.save_oauth_tokens(
            provider=GOOGLE_OAUTH_PROVIDER,
            token_json=creds.to_json(),
            scopes=settings.google_scopes,
            expiry=creds.expiry.isoformat() if creds.expiry else None,
        )
    return creds
