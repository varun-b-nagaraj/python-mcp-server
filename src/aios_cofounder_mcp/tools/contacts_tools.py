from __future__ import annotations

from ..server import mcp
from ..settings import settings
from ..storage.repo import Repository
from ..google import contacts as contacts_client
from ..approvals import ensure_approval
from ..audit import log_action
from . import log_tool_call, response_ok, response_error


_repo = Repository(settings.db_url)


@mcp.tool()
def contacts_search(query: str) -> dict:
    """Search Google Contacts."""
    log_tool_call("contacts_search", {"query": query})
    try:
        results = contacts_client.search_contacts(settings, _repo, query)
        return response_ok({"results": results})
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def contacts_get(contact_id: str) -> dict:
    """Return full contact details."""
    log_tool_call("contacts_get", {"contact_id": contact_id})
    try:
        contact = contacts_client.get_contact(settings, _repo, contact_id)
        return response_ok(contact)
    except RuntimeError as exc:
        return response_error(str(exc))


@mcp.tool()
def contacts_create_or_update(
    name: str,
    email: str,
    company: str | None = None,
    approval_id: int | None = None,
) -> dict:
    """Create or update a contact (requires approval)."""
    log_tool_call(
        "contacts_create_or_update",
        {"name": name, "email": email, "company": company, "approval_id": approval_id},
    )
    approval = ensure_approval(
        repo=_repo,
        action="contacts_create_or_update",
        payload={"name": name, "email": email, "company": company},
        approval_id=approval_id,
    )
    if not approval.ok:
        return response_error("approval_required", status=approval.status, approval_id=approval.approval_id)
    try:
        contact = contacts_client.create_or_update_contact(settings, _repo, name, email, company)
        log_action(_repo, "contacts_create_or_update", {"email": email}, contact)
        return response_ok(contact)
    except RuntimeError as exc:
        return response_error(str(exc))
