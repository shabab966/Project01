"""SQLite database helpers (thread-safe, row-as-dict access)."""
import sqlite3
from flask import g

from config import DATABASE

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


def get_db():
    """Return a per-request SQLite connection, opening one if needed.

    Rows are returned as dict-like objects via sqlite3.Row. We set
    check_same_thread=False because the connection is scoped to the Flask
    request context (one connection per request/thread), not shared across
    threads.
    """
    if "db" not in g:
        conn = sqlite3.connect(DATABASE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(exception=None):
    """Teardown handler: close the connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db):
    """Create tables if they don't already exist."""
    db.executescript(SCHEMA)
    db.commit()
