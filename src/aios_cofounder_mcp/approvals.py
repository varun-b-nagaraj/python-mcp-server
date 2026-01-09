from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .storage.repo import Repository


@dataclass
class ApprovalCheck:
    ok: bool
    status: str
    approval_id: int | None


def ensure_approval(
    repo: Repository,
    action: str,
    payload: dict[str, Any],
    approval_id: int | None,
) -> ApprovalCheck:
    if approval_id is None:
        created_id = repo.create_approval(action, payload)
        return ApprovalCheck(ok=False, status="approval_required", approval_id=created_id)

    approval = repo.get_approval(approval_id)
    if not approval:
        return ApprovalCheck(ok=False, status="approval_not_found", approval_id=approval_id)
    if approval["status"] != "approved":
        return ApprovalCheck(ok=False, status=f"approval_{approval['status']}", approval_id=approval_id)
    return ApprovalCheck(ok=True, status="approved", approval_id=approval_id)
