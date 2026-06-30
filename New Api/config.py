"""Application configuration."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SQLite database file lives next to this module.
DATABASE = os.path.join(BASE_DIR, "app.db")

# The secret key signs the session cookie. Override in production with the
# APP_SECRET_KEY environment variable.
SECRET_KEY = os.environ.get("APP_SECRET_KEY", "dev-only-change-me-in-production")

# Cookies are httponly by default in Flask; for a real production deployment
# behind HTTPS you should also set SESSION_COOKIE_SECURE = True.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
