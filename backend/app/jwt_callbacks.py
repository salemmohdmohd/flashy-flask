"""JWT callbacks for user loading and claims."""

from __future__ import annotations

import sqlalchemy as sa
from flask import jsonify
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import selectinload

from .extensions import db
from .models import User


def configure_jwt(jwt: JWTManager) -> None:
    """Configure JWT callbacks for the application."""

    @jwt.user_lookup_loader
    def load_user(_jwt_header, jwt_data):
        """Return the authenticated user for the current JWT."""

        try:
            identity = int(jwt_data["sub"])
        except (KeyError, TypeError, ValueError):
            return None

        return _load_user(identity)

    @jwt.additional_claims_loader
    def add_claims(identity):
        user = _load_user(identity)
        if not user:
            return {}
        return {"roles": [role.name for role in user.roles]}

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({"message": "Invalid token", "error": error_string}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({"message": "Missing token", "error": error_string}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Token expired"}), 401


def _load_user(user_id: int) -> User | None:
    """Fetch a user with roles eagerly loaded for JWT processing."""

    try:
        resolved_id = int(user_id)
    except (TypeError, ValueError):
        return None

    stmt = (
        sa.select(User).options(selectinload(User.roles)).where(User.id == resolved_id)
    )
    return db.session.execute(stmt).scalar_one_or_none()
