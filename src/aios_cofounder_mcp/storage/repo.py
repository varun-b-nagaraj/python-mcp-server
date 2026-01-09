from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from .db import get_connection


@dataclass
class Repository:
    db_url: str

    def _conn(self):
        return get_connection(self.db_url)

    def list_companies(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, name, domain, metadata, created_at FROM companies ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

    def add_company(self, name: str, domain: str | None, metadata: dict[str, Any] | None) -> dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO companies (name, domain, metadata) VALUES (?, ?, ?)",
                (name, domain, json.dumps(metadata) if metadata else None),
            )
            conn.commit()
            row = conn.execute("SELECT id, name, domain, metadata, created_at FROM companies ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else {}

    def list_contacts(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, name, email, company, metadata, created_at FROM contacts ORDER BY id DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def upsert_contact(
        self,
        name: str,
        email: str,
        company: str | None,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO contacts (name, email, company, metadata) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(email) DO UPDATE SET name=excluded.name, company=excluded.company, metadata=excluded.metadata",
                (name, email, company, json.dumps(metadata) if metadata else None),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, name, email, company, metadata, created_at FROM contacts WHERE email = ?",
                (email,),
            ).fetchone()
        return dict(row) if row else {}

    def save_oauth_tokens(self, provider: str, token_json: str, scopes: Iterable[str], expiry: str | None) -> None:
        scopes_value = ",".join(scopes)
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO oauth_tokens (provider, token_json, scopes, expiry) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(provider) DO UPDATE SET token_json=excluded.token_json, scopes=excluded.scopes, expiry=excluded.expiry, updated_at=CURRENT_TIMESTAMP",
                (provider, token_json, scopes_value, expiry),
            )
            conn.commit()

    def get_oauth_tokens(self, provider: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT provider, token_json, scopes, expiry, updated_at FROM oauth_tokens WHERE provider = ?",
                (provider,),
            ).fetchone()
        return dict(row) if row else None

    def create_oauth_request(
        self,
        provider: str,
        approval_id: str,
        state: str,
        expires_at: str,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO oauth_requests (approval_id, provider, state, status, expires_at) VALUES (?, ?, ?, ?, ?)",
                (approval_id, provider, state, "pending", expires_at),
            )
            conn.commit()

    def get_oauth_request_by_state(self, provider: str, state: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT approval_id, provider, state, status, error_message, created_at, expires_at "
                "FROM oauth_requests WHERE provider = ? AND state = ?",
                (provider, state),
            ).fetchone()
        return dict(row) if row else None

    def get_oauth_request(self, provider: str, approval_id: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT approval_id, provider, state, status, error_message, created_at, expires_at "
                "FROM oauth_requests WHERE provider = ? AND approval_id = ?",
                (provider, approval_id),
            ).fetchone()
        return dict(row) if row else None

    def update_oauth_request_status(
        self,
        provider: str,
        approval_id: str,
        status: str,
        error_message: str | None,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE oauth_requests SET status = ?, error_message = ? WHERE provider = ? AND approval_id = ?",
                (status, error_message, provider, approval_id),
            )
            conn.commit()

    def create_approval(self, action: str, payload: dict[str, Any]) -> int:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO approvals (action, payload, status) VALUES (?, ?, ?)",
                (action, json.dumps(payload), "pending"),
            )
            conn.commit()
            row = conn.execute("SELECT id FROM approvals ORDER BY id DESC LIMIT 1").fetchone()
        return int(row["id"]) if row else 0

    def resolve_approval(self, approval_id: int, decision: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE approvals SET status = ?, resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
                (decision, approval_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, action, payload, status, created_at, resolved_at FROM approvals WHERE id = ?",
                (approval_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_approval(self, approval_id: int) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id, action, payload, status, created_at, resolved_at FROM approvals WHERE id = ?",
                (approval_id,),
            ).fetchone()
        return dict(row) if row else None

    def list_approvals(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, action, payload, status, created_at, resolved_at FROM approvals ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_audit(self, action: str, payload: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO audit_log (action, payload, result) VALUES (?, ?, ?)",
                (action, json.dumps(payload), json.dumps(result)),
            )
            conn.commit()
            row = conn.execute("SELECT id, action, payload, result, created_at FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else {}

    def list_audit(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, action, payload, result, created_at FROM audit_log ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_note(self, source: str, summary: str) -> dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO assistant_notes (source, summary) VALUES (?, ?)",
                (source, summary),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, source, summary, created_at FROM assistant_notes ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return dict(row) if row else {}

    def list_notes(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, source, summary, created_at FROM assistant_notes ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
