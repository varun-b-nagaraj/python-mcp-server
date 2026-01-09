from __future__ import annotations

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
        raise RuntimeError("calendar_not_connected")
    return build("calendar", "v3", credentials=creds)


def list_events(settings: Settings, repo: Repository, start: str, end: str) -> list[dict[str, Any]]:
    service = _get_service(settings, repo)
    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events.get("items", [])


def find_free_slots(
    settings: Settings,
    repo: Repository,
    duration_minutes: int,
    window_start: str,
    window_end: str,
) -> dict[str, Any]:
    service = _get_service(settings, repo)
    body = {
        "timeMin": window_start,
        "timeMax": window_end,
        "items": [{"id": "primary"}],
    }
    response = service.freebusy().query(body=body).execute()
    busy = response.get("calendars", {}).get("primary", {}).get("busy", [])
    free = _compute_free_slots(busy, window_start, window_end, duration_minutes)
    return {
        "window_start": window_start,
        "window_end": window_end,
        "duration_minutes": duration_minutes,
        "busy": busy,
        "free": free,
    }


def _compute_free_slots(
    busy: list[dict[str, str]],
    window_start: str,
    window_end: str,
    duration_minutes: int,
) -> list[dict[str, str]]:
    from datetime import datetime, timedelta

    def _parse(value: str) -> datetime:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)

    start_dt = _parse(window_start)
    end_dt = _parse(window_end)
    intervals = sorted(
        [(_parse(item["start"]), _parse(item["end"])) for item in busy],
        key=lambda item: item[0],
    )
    free: list[dict[str, str]] = []
    cursor = start_dt
    min_delta = timedelta(minutes=duration_minutes)
    for busy_start, busy_end in intervals:
        if busy_start > cursor and busy_start - cursor >= min_delta:
            free.append({"start": cursor.isoformat(), "end": busy_start.isoformat()})
        if busy_end > cursor:
            cursor = busy_end
    if end_dt > cursor and end_dt - cursor >= min_delta:
        free.append({"start": cursor.isoformat(), "end": end_dt.isoformat()})
    return free


def create_event(
    settings: Settings,
    repo: Repository,
    title: str,
    start: str,
    end: str,
    attendees: list[str],
) -> dict[str, Any]:
    service = _get_service(settings, repo)
    event_body = {
        "summary": title,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
        "attendees": [{"email": email} for email in attendees],
    }
    event = (
        service.events()
        .insert(calendarId="primary", body=event_body, sendUpdates="none")
        .execute()
    )
    return event


def update_event(
    settings: Settings,
    repo: Repository,
    event_id: str,
    changes: dict[str, Any],
) -> dict[str, Any]:
    service = _get_service(settings, repo)
    event = service.events().patch(calendarId="primary", eventId=event_id, body=changes).execute()
    return event


def cancel_event(settings: Settings, repo: Repository, event_id: str) -> dict[str, Any]:
    service = _get_service(settings, repo)
    service.events().delete(calendarId="primary", eventId=event_id, sendUpdates="none").execute()
    return {"cancelled": True, "event_id": event_id}


def get_event(settings: Settings, repo: Repository, event_id: str) -> dict[str, Any]:
    service = _get_service(settings, repo)
    return service.events().get(calendarId="primary", eventId=event_id).execute()
