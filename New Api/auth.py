"""Authentication blueprint: register, login, logout, and current user."""
from __future__ import annotations

from typing import Optional

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _validate_credentials(payload) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (username, password, error_message)."""
    if not payload or not isinstance(payload, dict):
        return None, None, "Request body must be a JSON object."
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not username or not password:
        return None, None, "Both 'username' and 'password' are required."
    if len(username) < 3:
        return None, None, "Username must be at least 3 characters."
    if len(password) < 6:
        return None, None, "Password must be at least 6 characters."
    return username, password, None


@bp.post("/register")
def register():
    username, password, error = _validate_credentials(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    if User.get_by_username(username) is not None:
        return jsonify({"error": "That username is already taken."}), 409

    user = User(id=None, username=username, password_hash="")
    user.set_password(password)
    user.save()

    # Log the new user in right away by creating a session.
    login_user(user)
    return jsonify(
        {
            "message": "Account created and logged in.",
            "user": {"id": user.id, "username": user.username},
        }
    ), 201


@bp.post("/login")
def login():
    username, password, error = _validate_credentials(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    user = User.get_by_username(username)
    if user is None or not user.check_password(password):
        # Same message for both cases to avoid leaking which usernames exist.
        return jsonify({"error": "Invalid username or password."}), 401

    login_user(user)
    return jsonify(
        {
            "message": "Logged in.",
            "user": {"id": user.id, "username": user.username},
        }
    )


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out."})


@bp.get("/me")
@login_required
def me():
    return jsonify({"user": {"id": current_user.id, "username": current_user.username}})
