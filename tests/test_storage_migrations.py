import sqlite3
import tempfile

from aios_cofounder_mcp.storage.db import init_db


def test_migrations_create_tables() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/test.db"
        init_db(f"sqlite:///{db_path}")
        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        conn.close()

    tables = {row[0] for row in rows}
    expected = {
        "companies",
        "contacts",
        "oauth_tokens",
        "approvals",
        "audit_log",
        "assistant_notes",
    }
    assert expected.issubset(tables)
