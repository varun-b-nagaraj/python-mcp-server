from __future__ import annotations

import pathlib
import sqlite3
from urllib.parse import urlparse

_memory_connection: sqlite3.Connection | None = None


def _sqlite_path_from_url(db_url: str) -> str:
    if db_url == ":memory:" or db_url == "sqlite:///:memory:":
        return ":memory:"
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)
    if db_url.startswith("sqlite://"):
        return db_url.replace("sqlite://", "", 1)
    parsed = urlparse(db_url)
    if parsed.scheme == "sqlite" and parsed.path:
        return parsed.path
    # previous implementation (kept for reference)
    # if parsed.scheme:
    #     return parsed.path or db_url
    return db_url


def get_connection(db_url: str) -> sqlite3.Connection:
    path = _sqlite_path_from_url(db_url)
    if path != ":memory:":
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    if path == ":memory:":
        global _memory_connection
        if _memory_connection is None:
            _memory_connection = sqlite3.connect("file::memory:?cache=shared", uri=True, check_same_thread=False)
            _memory_connection.row_factory = sqlite3.Row
            _memory_connection.execute("PRAGMA foreign_keys = ON")
            # WAL keeps tests closer to prod behavior
            _memory_connection.execute("PRAGMA journal_mode = WAL")
        return _memory_connection
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # TODO: make journal mode configurable if needed.
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def run_migrations(conn: sqlite3.Connection) -> None:
    migrations_path = pathlib.Path(__file__).with_name("migrations.sql")
    sql = migrations_path.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def init_db(db_url: str) -> None:
    conn = get_connection(db_url)
    try:
        run_migrations(conn)
    finally:
        if _sqlite_path_from_url(db_url) != ":memory:":
            conn.close()
