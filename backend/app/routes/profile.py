"""Profile management endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..extensions import db
from ..schemas import ProfileSchema, UserSchema

profile_bp = Blueprint("profile", __name__)
profile_schema = ProfileSchema()
user_schema = UserSchema()


@profile_bp.get("")
@jwt_required()
def get_profile():
    """Return the authenticated user's profile."""
    return jsonify({"user": user_schema.dump(current_user)}), 200


@profile_bp.put("")
@jwt_required()
def update_profile():
    """Update the authenticated user's profile."""
    payload = request.get_json() or {}
    errors = profile_schema.validate(payload, partial=True)
    if errors:
        return jsonify({"errors": errors}), 400
    profile = current_user.profile
    if not profile:
        profile = profile_schema.load(payload)
        current_user.profile = profile
    else:
        for key, value in payload.items():
            setattr(profile, key, value)
    db.session.commit()
    return profile_schema.jsonify(profile), 200
