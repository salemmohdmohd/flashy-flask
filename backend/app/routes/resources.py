"""Resource upload and moderation endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..models import Resource
from ..schemas import ResourceSchema
from ..services.resource_service import ResourceServiceError, resource_service
from ..utils.security import roles_accepted

resource_bp = Blueprint("resources", __name__)
resource_schema = ResourceSchema()


@resource_bp.post("")
@jwt_required()
def create_resource():
    """Persist metadata for an uploaded resource."""
    payload = request.get_json() or {}
    filename = payload.get("filename")
    storage_url = payload.get("storage_url")
    if not filename or not storage_url:
        return jsonify({"message": "filename and storage_url are required"}), 400
    try:
        resource = resource_service.save_resource(
            owner=current_user,
            filename=filename,
            storage_url=storage_url,
            description=payload.get("description"),
            categories=payload.get("categories"),
        )
    except ResourceServiceError as exc:
        return jsonify({"message": str(exc)}), 400
    return resource_schema.jsonify(resource), 201


@resource_bp.get("")
@jwt_required()
def list_resources():
    """List resources owned by the user."""
    query = Resource.query
    if not current_user.has_role("admin"):
        query = query.filter_by(owner_id=current_user.id)
    resources = query.order_by(Resource.created_at.desc()).all()
    return resource_schema.jsonify(resources, many=True), 200


@resource_bp.get("/<int:resource_id>")
@jwt_required()
def get_resource(resource_id: int):
    """Retrieve a single resource."""
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner_id != current_user.id and not current_user.has_role("admin"):
        return jsonify({"message": "Not authorized"}), 403
    return resource_schema.jsonify(resource), 200


@resource_bp.put("/<int:resource_id>/status")
@jwt_required()
@roles_accepted("admin", "expert")
def update_resource_status(resource_id: int):
    """Update AI processing status."""
    resource = Resource.query.get_or_404(resource_id)
    status = request.json.get("status")
    if not status:
        return jsonify({"message": "status is required"}), 400
    resource_service.update_status(resource, status)
    return resource_schema.jsonify(resource), 200
