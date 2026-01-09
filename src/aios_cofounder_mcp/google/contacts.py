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
        raise RuntimeError("contacts_not_connected")
    return build("people", "v1", credentials=creds)


def search_contacts(settings: Settings, repo: Repository, query: str) -> list[dict[str, Any]]:
    service = _get_service(settings, repo)
    response = service.people().searchContacts(query=query, pageSize=10, readMask="names,emailAddresses,organizations").execute()
    return response.get("results", [])


def get_contact(settings: Settings, repo: Repository, contact_id: str) -> dict[str, Any]:
    service = _get_service(settings, repo)
    return service.people().get(resourceName=contact_id, personFields="names,emailAddresses,organizations").execute()


def create_or_update_contact(
    settings: Settings,
    repo: Repository,
    name: str,
    email: str,
    company: str | None,
) -> dict[str, Any]:
    service = _get_service(settings, repo)
    existing = service.people().searchContacts(query=email, pageSize=1, readMask="names,emailAddresses,organizations").execute()
    results = existing.get("results", [])
    person_body: dict[str, Any] = {
        "names": [{"displayName": name}],
        "emailAddresses": [{"value": email}],
    }
    if company:
        person_body["organizations"] = [{"name": company}]

    if results:
        resource_name = results[0]["person"]["resourceName"]
        return service.people().updateContact(
            resourceName=resource_name,
            updatePersonFields="names,emailAddresses,organizations",
            body=person_body,
        ).execute()
    return service.people().createContact(body=person_body).execute()
