"""User model backed by SQLite, integrated with Flask-Login."""
from __future__ import annotations

from typing import Optional

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db


class User(UserMixin):
    """A single application user.

    Flask-Login requires four properties (is_authenticated, is_active,
    is_anonymous, get_id()). UserMixin provides default implementations that
    work for us, so we only need get_id() to return the str(id).
    """

    def __init__(self, id: int, username: str, password_hash: str):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def get_id(self) -> str:
        return str(self.id)

    # ---- password helpers -------------------------------------------------

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # ---- persistence ------------------------------------------------------

    def save(self) -> "User":
        """Insert or update this user row."""
        db = get_db()
        if getattr(self, "id", None) is None:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (self.username, self.password_hash),
            )
        else:
            db.execute(
                "UPDATE users SET username = ?, password_hash = ? WHERE id = ?",
                (self.username, self.password_hash, self.id),
            )
        db.commit()
        # Fetch back to populate a fresh id on insert.
        return self._refresh(db)

    @classmethod
    def _row_to_user(cls, row) -> Optional["User"]:
        if row is None:
            return None
        return cls(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
        )

    @classmethod
    def get(cls, user_id: int) -> Optional["User"]:
        row = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return cls._row_to_user(row)

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        row = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return cls._row_to_user(row)

    def _refresh(self, db) -> "User":
        row = db.execute(
            "SELECT * FROM users WHERE id = last_insert_rowid()"
        ).fetchone()
        self.id = row["id"]
        self.username = row["username"]
        self.password_hash = row["password_hash"]
        return self
