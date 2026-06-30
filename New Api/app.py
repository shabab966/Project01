"""Application factory and route registration."""
from flask import Flask, jsonify
from flask_login import LoginManager, current_user, login_required

import config
from db import close_db, get_db, init_db
from models import User


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    # --- database lifecycle -------------------------------------------------
    app.teardown_appcontext(close_db)

    # --- Flask-Login setup --------------------------------------------------
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.get(int(user_id))
        except (TypeError, ValueError):
            return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Authentication required."}), 401

    # --- ensure schema exists on first request ------------------------------
    @app.before_request
    def _ensure_db():
        init_db(get_db())

    # --- blueprints ---------------------------------------------------------
    from auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # --- routes -------------------------------------------------------------
    @app.get("/")
    def index():
        return jsonify(
            {
                "service": "sign-in-api",
                "endpoints": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                    "logout": "POST /api/auth/logout",
                    "me": "GET /api/auth/me",
                    "protected": "GET /api/protected",
                },
            }
        )

    @app.get("/api/protected")
    @login_required
    def protected():
        return jsonify(
            {
                "message": f"Hello {current_user.username}, you are signed in.",
                "user": {"id": current_user.id, "username": current_user.username},
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    # debug=True gives auto-reload and useful error pages while developing.
    app.run(host="127.0.0.1", port=5000, debug=True)
