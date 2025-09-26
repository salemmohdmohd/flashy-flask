"""Application factory for the Flashy Flask backend."""

from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Any

from flask import Flask
from flask_cors import CORS

from .extensions import admin, bcrypt, db, jwt, limiter, mail, migrate
from .routes.admin import admin_bp
from .routes.auth import auth_bp
from .routes.flashcards import flashcard_bp
from .routes.lessons import lesson_bp
from .routes.profile import profile_bp
from .routes.public import public_bp
from .routes.resources import resource_bp
from .utils.logging import LOGGING_CONFIG


def create_app(config_class: str = "backend.config.DevelopmentConfig") -> Flask:
    """Create and configure the Flask application.

    Args:
        config_class: The import path to the configuration object.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).info("Loading configuration %s", config_class)

    register_extensions(app)
    register_blueprints(app)
    register_cli(app)
    configure_cors(app)

    return app


def register_extensions(app: Flask) -> None:
    """Bind Flask extensions to the application."""
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    admin.init_app(app)


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/v1/profile")
    app.register_blueprint(resource_bp, url_prefix="/api/v1/resources")
    app.register_blueprint(flashcard_bp, url_prefix="/api/v1/flashcards")
    app.register_blueprint(lesson_bp, url_prefix="/api/v1/lessons")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(public_bp, url_prefix="/api/v1/public")


def configure_cors(app: Flask) -> None:
    """Configure Cross-Origin Resource Sharing policies."""
    allowed_origins: list[str] = app.config.get("CORS_ORIGINS", [])
    if not allowed_origins:
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )


def register_cli(app: Flask) -> None:
    """Register custom CLI commands."""
    from .seeds.seed_data import seed_command

    app.cli.add_command(seed_command)


__all__ = ["create_app", "register_extensions"]
