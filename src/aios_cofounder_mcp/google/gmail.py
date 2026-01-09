from __future__ import annotations

import base64
import email
from email.message import EmailMessage
from typing import Any

from ..settings import Settings
from ..storage.repo import Repository
from .oauth import load_credentials


def _get_service(settings: Settings, repo: Repository):
    try:
        from googleapiclient.discovery import build
    except ModuleNotFoundError as exc:
        raise RuntimeError("google_api_client_not_installed") from exc
    creds = load_credentials(settings, repo)
    if not creds:
        raise RuntimeError("gmail_not_connected")
    return build("gmail", "v1", credentials=creds)


def _header_value(headers: list[dict[str, str]], name: str) -> str | None:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value")
    return None


def _extract_text_from_raw(raw: str) -> dict[str, str | None]:
    decoded = base64.urlsafe_b64decode(raw.encode("utf-8"))
    msg = email.message_from_bytes(decoded)
    text_body = None
    html_body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and text_body is None:
                text_body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
            if content_type == "text/html" and html_body is None:
                html_body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            text_body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return {"text": text_body, "html": html_body}


def search(settings: Settings, repo: Repository, query: str, limit: int) -> list[dict[str, Any]]:
    service = _get_service(settings, repo)
    results = service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
    messages = results.get("messages", [])
    output: list[dict[str, Any]] = []
    for msg in messages:
        detail = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"])
            .execute()
        )
        headers = detail.get("payload", {}).get("headers", [])
        output.append(
            {
                "id": detail.get("id"),
                "thread_id": detail.get("threadId"),
                "from": _header_value(headers, "From"),
                "subject": _header_value(headers, "Subject"),
                "date": _header_value(headers, "Date"),
                "snippet": detail.get("snippet"),
            }
        )
    return output


def get_message(settings: Settings, repo: Repository, message_id: str) -> dict[str, Any]:
    service = _get_service(settings, repo)
    detail = service.users().messages().get(userId="me", id=message_id, format="raw").execute()
    raw = detail.get("raw", "")
    parsed = _extract_text_from_raw(raw) if raw else {"text": None, "html": None}
    return {
        "id": detail.get("id"),
        "thread_id": detail.get("threadId"),
        "snippet": detail.get("snippet"),
        "text": parsed.get("text"),
        "html": parsed.get("html"),
    }


def get_thread(settings: Settings, repo: Repository, thread_id: str) -> dict[str, Any]:
    service = _get_service(settings, repo)
    detail = service.users().threads().get(userId="me", id=thread_id, format="full").execute()
    return detail


def create_draft(
    settings: Settings,
    repo: Repository,
    to: str,
    subject: str,
    body: str,
    thread_id: str | None,
) -> dict[str, Any]:
    service = _get_service(settings, repo)
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft_body: dict[str, Any] = {"message": {"raw": raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id
    draft = service.users().drafts().create(userId="me", body=draft_body).execute()
    return {"id": draft.get("id"), "message": draft.get("message")}


def apply_labels(
    settings: Settings,
    repo: Repository,
    message_ids: list[str],
    labels: list[str],
) -> dict[str, Any]:
    service = _get_service(settings, repo)
    labels = _resolve_label_ids(service, labels)
    applied = []
    for message_id in message_ids:
        modified = (
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"addLabelIds": labels})
            .execute()
        )
        applied.append({"id": modified.get("id"), "label_ids": modified.get("labelIds", [])})
    return {"applied": applied}


def _resolve_label_ids(service, labels: list[str]) -> list[str]:
    if not labels:
        return labels
    existing = service.users().labels().list(userId="me").execute().get("labels", [])
    name_to_id = {label["name"]: label["id"] for label in existing}
    id_set = {label["id"] for label in existing}
    resolved = []
    for label in labels:
        if label in id_set:
            resolved.append(label)
        elif label in name_to_id:
            resolved.append(name_to_id[label])
        else:
            resolved.append(label)
    return resolved
