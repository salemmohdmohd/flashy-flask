"""Admin endpoints for managing users and content."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import FAQ, BlogPost, Resource, Role, User
from ..schemas import ResourceSchema, UserSchema
from ..utils.security import roles_accepted, roles_required

admin_bp = Blueprint("admin", __name__)
user_schema = UserSchema()
resource_schema = ResourceSchema()


@admin_bp.get("/users")
@jwt_required()
@roles_required("admin")
def list_users():
    """Return all users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return user_schema.jsonify(users, many=True), 200


@admin_bp.post("/users/role")
@jwt_required()
@roles_required("admin")
def update_user_role():
    """Assign a role to a user."""
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    role_name = payload.get("role")
    if not user_id or not role_name:
        return jsonify({"message": "user_id and role are required"}), 400
    user = User.query.get_or_404(user_id)
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({"message": "Role not found"}), 404
    if role not in user.roles:
        user.roles.append(role)
    db.session.commit()
    return user_schema.jsonify(user), 200


@admin_bp.get("/resources")
@jwt_required()
@roles_required("admin")
def moderate_resources():
    """Return all resources for moderation."""
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
    return resource_schema.jsonify(resources, many=True), 200


@admin_bp.post("/content/blog")
@jwt_required()
@roles_accepted("admin", "marketing")
def create_blog_post():
    """Create or update a marketing blog post."""
    payload = request.get_json() or {}
    slug = payload.get("slug")
    if not slug:
        return jsonify({"message": "slug is required"}), 400
    post = BlogPost.query.filter_by(slug=slug).first()
    if not post:
        post = BlogPost(slug=slug)
        db.session.add(post)
    post.title = payload.get("title", post.title)
    post.content = payload.get("content", post.content)
    post.is_published = payload.get("is_published", post.is_published or False)
    if "hero_image_url" in payload:
        post.hero_image_url = payload.get("hero_image_url")
    db.session.commit()
    return jsonify({"message": "Blog post saved", "slug": post.slug}), 200


@admin_bp.post("/content/faq")
@jwt_required()
@roles_accepted("admin", "marketing")
def create_faq():
    """Create or update FAQs."""
    payload = request.get_json() or {}
    faq = FAQ(question=payload.get("question"), answer=payload.get("answer"))
    db.session.add(faq)
    db.session.commit()
    return jsonify({"message": "FAQ created", "id": faq.id}), 201
