"""Authentication endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    current_user,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from ..schemas import LoginSchema, RegisterSchema, UserSchema
from ..services.auth_service import AuthServiceError, auth_service

auth_bp = Blueprint("auth", __name__)
register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()


@auth_bp.post("/register")
def register_user():
    """Register a new user."""
    payload = request.get_json() or {}
    errors = register_schema.validate(payload)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        user = auth_service.register_user(
            email=payload["email"],
            username=payload["username"],
            password=payload["password"],
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            role_name=payload.get("role"),
        )
    except AuthServiceError as exc:
        return jsonify({"message": str(exc)}), 400
    return user_schema.jsonify(user), 201


@auth_bp.post("/login")
def login_user():
    """Authenticate and issue JWT tokens."""
    payload = request.get_json() or {}
    errors = login_schema.validate(payload)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        access_token, refresh_token, user = auth_service.authenticate(
            email=payload["email"],
            password=payload["password"],
        )
    except AuthServiceError as exc:
        return jsonify({"message": str(exc)}), 401
    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_schema.dump(user),
            }
        ),
        200,
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_token():
    """Issue a new access token using a refresh token."""
    identity = get_jwt_identity()
    claims = get_jwt()
    roles = claims.get("roles", [])
    if not roles:
        try:
            roles = auth_service.get_user_roles(identity)
        except AuthServiceError as exc:
            return jsonify({"message": str(exc)}), 401
    new_token = create_access_token(
        identity=identity, additional_claims={"roles": roles}
    )
    return jsonify({"access_token": new_token}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the current user's profile."""
    return user_schema.jsonify(current_user), 200


@auth_bp.post("/google")
def google_login():
    """Handle Google OAuth login by exchanging authorization code."""
    payload = request.get_json() or {}
    code = payload.get("code")
    if not code:
        return jsonify({"message": "Authorization code missing"}), 400
    try:
        access_token, refresh_token, user = auth_service.google_oauth_login(code=code)
    except AuthServiceError as exc:
        return jsonify({"message": str(exc)}), 400
    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_schema.dump(user),
            }
        ),
        200,
    )
