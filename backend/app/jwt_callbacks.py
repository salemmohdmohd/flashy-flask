"""JWT callbacks for user loading and claims."""
from __future__ import annotations

from flask import jsonify
from flask_jwt_extended import JWTManager

from .models import User


def configure_jwt(jwt: JWTManager) -> None:
    """Configure JWT callbacks for the application."""

    @jwt.user_lookup_loader
    def load_user(_jwt_header, jwt_data):
        identity = int(jwt_data["sub"])
        return User.query.get(identity)

    @jwt.additional_claims_loader
    def add_claims(identity):
        user = User.query.get(int(identity))
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
