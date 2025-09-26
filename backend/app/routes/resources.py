"""Resource upload and moderation endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file
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


@resource_bp.post("/upload")
@jwt_required()
def upload_resource():
    """Handle multipart resource uploads and trigger metadata extraction."""
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"message": "file is required"}), 400

    categories = _parse_categories(request)
    description = request.form.get("description")

    try:
        resource = resource_service.save_resource(
            owner=current_user,
            uploaded_file=uploaded_file,
            description=description,
            categories=categories,
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
    try:
        resource_service.update_status(resource, status)
    except ResourceServiceError as exc:
        return jsonify({"message": str(exc)}), 400
    return resource_schema.jsonify(resource), 200


@resource_bp.get("/<int:resource_id>/download")
@jwt_required()
def download_resource(resource_id: int):
    """Download the underlying resource file if stored locally."""
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner_id != current_user.id and not current_user.has_role("admin"):
        return jsonify({"message": "Not authorized"}), 403

    if not resource.storage_url:
        return jsonify({"message": "File not available"}), 404
    if resource.storage_url.startswith("http"):
        return (
            jsonify(
                {"message": "Resource stored remotely", "url": resource.storage_url}
            ),
            200,
        )

    file_path = Path(resource.storage_url)
    if not file_path.exists():
        return jsonify({"message": "Resource file missing"}), 404
    return send_file(
        file_path, as_attachment=True, download_name=resource.original_name
    )


def _parse_categories(req) -> list[str] | None:
    """Extract category names from form data supporting multiple formats."""
    categories: list[str] = []
    if hasattr(req, "form"):
        categories = [value for value in req.form.getlist("categories") if value]
        if not categories and "categories[]" in req.form:
            categories = [value for value in req.form.getlist("categories[]") if value]
        if not categories:
            raw = req.form.get("categories")
            if raw:
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        categories = [str(item) for item in parsed if str(item).strip()]
                    elif isinstance(parsed, str):
                        categories = [parsed]
                except json.JSONDecodeError:
                    categories = [
                        item.strip() for item in raw.split(",") if item.strip()
                    ]
    return categories or None
