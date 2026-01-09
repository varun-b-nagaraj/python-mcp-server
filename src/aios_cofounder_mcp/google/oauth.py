from __future__ import annotations

from typing import Any

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from ..settings import Settings, get_redirect_uri
from ..storage.repo import Repository


GOOGLE_OAUTH_PROVIDER = "google"


def _require_oauth_config(settings: Settings) -> None:
    if not settings.google_client_id or not settings.google_client_secret:
        raise RuntimeError("google_oauth_not_configured")
    if not settings.oauth_redirect_base_url:
        raise RuntimeError("oauth_redirect_base_url_missing")


def _client_config(settings: Settings) -> dict[str, Any]:
    return {
        "installed": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uris": [get_redirect_uri(settings)],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


def start_oauth(settings: Settings, repo: Repository) -> dict[str, Any]:
    _require_oauth_config(settings)
    from google_auth_oauthlib.flow import Flow

    state = secrets.token_urlsafe(32)
    approval_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=settings.oauth_state_ttl_seconds)
    repo.create_oauth_request(
        provider=GOOGLE_OAUTH_PROVIDER,
        approval_id=approval_id,
        state=state,
        expires_at=expires_at.isoformat(),
    )
    redirect_uri = get_redirect_uri(settings)
    flow = Flow.from_client_config(
        _client_config(settings),
        scopes=settings.google_scopes,
        redirect_uri=redirect_uri,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    return {"auth_url": auth_url, "approval_id": approval_id, "expires_at": expires_at.isoformat()}


def handle_oauth_callback(settings: Settings, repo: Repository, code: str, state: str) -> dict[str, Any]:
    _require_oauth_config(settings)
    request = repo.get_oauth_request_by_state(GOOGLE_OAUTH_PROVIDER, state)
    if not request:
        return {"ok": False, "error": "invalid_state"}
    if _is_expired(request.get("expires_at")):
        repo.update_oauth_request_status(
            provider=GOOGLE_OAUTH_PROVIDER,
            approval_id=request["approval_id"],
            status="expired",
            error_message="state_expired",
        )
        return {"ok": False, "error": "state_expired"}

    from google_auth_oauthlib.flow import Flow

    redirect_uri = get_redirect_uri(settings)
    flow = Flow.from_client_config(
        _client_config(settings),
        scopes=settings.google_scopes,
        redirect_uri=redirect_uri,
    )
    try:
        flow.fetch_token(code=code)
    except Exception as exc:
        repo.update_oauth_request_status(
            provider=GOOGLE_OAUTH_PROVIDER,
            approval_id=request["approval_id"],
            status="error",
            error_message=str(exc),
        )
        return {"ok": False, "error": "token_exchange_failed"}

    credentials = flow.credentials
    repo.save_oauth_tokens(
        provider=GOOGLE_OAUTH_PROVIDER,
        token_json=credentials.to_json(),
        scopes=settings.google_scopes,
        expiry=credentials.expiry.isoformat() if credentials.expiry else None,
    )
    repo.update_oauth_request_status(
        provider=GOOGLE_OAUTH_PROVIDER,
        approval_id=request["approval_id"],
        status="approved",
        error_message=None,
    )
    return {"ok": True, "approval_id": request["approval_id"]}


def get_oauth_status(settings: Settings, repo: Repository, approval_id: str) -> dict[str, Any]:
    request = repo.get_oauth_request(GOOGLE_OAUTH_PROVIDER, approval_id)
    if not request:
        return {"status": "not_found"}
    if request.get("status") == "pending" and _is_expired(request.get("expires_at")):
        repo.update_oauth_request_status(
            provider=GOOGLE_OAUTH_PROVIDER,
            approval_id=approval_id,
            status="expired",
            error_message="state_expired",
        )
        request["status"] = "expired"
    return {"status": request.get("status"), "error_message": request.get("error_message")}


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


def _is_expired(expires_at: str | None) -> bool:
    if not expires_at:
        return False
    try:
        expires_dt = datetime.fromisoformat(expires_at)
    except ValueError:
        return False
    if expires_dt.tzinfo is None:
        expires_dt = expires_dt.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= expires_dt
