from __future__ import annotations

from typing import Any

from .storage.repo import Repository


def log_action(repo: Repository, action: str, payload: dict[str, Any], result: dict[str, Any]) -> None:
    repo.add_audit(action=action, payload=payload, result=result)
