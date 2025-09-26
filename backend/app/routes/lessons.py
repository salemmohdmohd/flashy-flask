"""Lesson endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..models import Lesson, Resource
from ..schemas import LessonSchema
from ..services.lesson_service import LessonServiceError, lesson_service
from ..utils.security import roles_accepted

lesson_bp = Blueprint("lessons", __name__)
lesson_schema = LessonSchema()


@lesson_bp.post("/generate")
@jwt_required()
@roles_accepted("teacher", "expert", "admin")
def generate_lesson():
    """Generate a lesson for a resource."""
    payload = request.get_json() or {}
    resource_id = payload.get("resource_id")
    if not resource_id:
        return jsonify({"message": "resource_id is required"}), 400
    resource = Resource.query.get_or_404(resource_id)
    try:
        lesson = lesson_service.generate_lesson(author=current_user, resource=resource)
    except LessonServiceError as exc:
        return jsonify({"message": str(exc)}), 400
    return lesson_schema.jsonify(lesson), 201


@lesson_bp.put("/<int:lesson_id>/publish")
@jwt_required()
@roles_accepted("teacher", "expert", "admin")
def publish_lesson(lesson_id: int):
    """Publish a lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.author_id != current_user.id and not current_user.has_role("admin"):
        return jsonify({"message": "Not authorized"}), 403
    lesson = lesson_service.publish_lesson(lesson)
    return lesson_schema.jsonify(lesson), 200


@lesson_bp.get("/<int:lesson_id>")
@jwt_required()
def get_lesson(lesson_id: int):
    """Fetch a lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.author_id != current_user.id and not current_user.has_role("admin"):
        return jsonify({"message": "Not authorized"}), 403
    return lesson_schema.jsonify(lesson), 200
