"""Admin endpoints for managing users and content."""

from __future__ import annotations

import sqlalchemy as sa
from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import FAQ, BlogPost, Lesson, Notification, Resource, Role, User
from ..schemas import BlogPostSchema, ResourceSchema, UserSchema
from ..utils.security import roles_accepted, roles_required

admin_bp = Blueprint("admin_api", __name__)
user_schema = UserSchema()
resource_schema = ResourceSchema()
blog_post_schema = BlogPostSchema()

VALID_RESOURCE_STATUSES: set[str] = {
    "pending",
    "processing",
    "complete",
    "failed",
    "rejected",
}


@admin_bp.get("/users")
@jwt_required()
@roles_required("admin")
def list_users():
    """Return all users."""
    stmt = (
        sa.select(User)
        .order_by(User.created_at.desc())
        .options(selectinload(User.roles))
    )
    users = db.session.scalars(stmt).all()
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
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    role = db.session.scalar(sa.select(Role).where(Role.name == role_name))
    if not role:
        return jsonify({"message": "Role not found"}), 404
    if role not in user.roles:
        user.roles.append(role)
    db.session.commit()
    return user_schema.jsonify(user), 200


@admin_bp.patch("/users/<int:user_id>")
@jwt_required()
@roles_required("admin")
def update_user(user_id: int):
    """Update user attributes such as active state or assigned roles."""

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    payload = request.get_json() or {}
    updated = False

    if "is_active" in payload:
        user.is_active = bool(payload.get("is_active"))
        updated = True

    if "roles" in payload:
        roles_payload = payload.get("roles")
        if not isinstance(roles_payload, list):
            return jsonify({"message": "roles must be provided as a list"}), 400
        desired_roles = {str(role_name) for role_name in roles_payload}
        if not desired_roles:
            return jsonify({"message": "At least one role must be provided"}), 400

        stmt = sa.select(Role).where(Role.name.in_(desired_roles))
        roles = db.session.scalars(stmt).all()
        found_role_names = {role.name for role in roles}
        missing = desired_roles - found_role_names
        if missing:
            return (
                jsonify({"message": "Unknown roles", "missing": sorted(missing)}),
                400,
            )

        user.roles = roles
        updated = True

    if not updated:
        return jsonify({"message": "No updatable fields provided"}), 400

    db.session.commit()
    return user_schema.jsonify(user), 200


@admin_bp.get("/resources")
@jwt_required()
@roles_required("admin")
def moderate_resources():
    """Return all resources for moderation."""
    stmt = (
        sa.select(Resource)
        .order_by(Resource.created_at.desc())
        .options(selectinload(Resource.categories), selectinload(Resource.owner))
    )
    resources = db.session.scalars(stmt).all()
    return resource_schema.jsonify(resources, many=True), 200


@admin_bp.patch("/resources/<int:resource_id>")
@jwt_required()
@roles_required("admin")
def update_resource(resource_id: int):
    """Update moderation state or metadata for a resource."""

    resource = db.session.get(Resource, resource_id)
    if not resource:
        return jsonify({"message": "Resource not found"}), 404

    payload = request.get_json() or {}
    updated = False

    if "ai_processing_status" in payload:
        status = str(payload.get("ai_processing_status"))
        if status not in VALID_RESOURCE_STATUSES:
            return (
                jsonify(
                    {
                        "message": "Invalid status",
                        "allowed": sorted(VALID_RESOURCE_STATUSES),
                    }
                ),
                400,
            )
        resource.ai_processing_status = status
        updated = True

    if "description" in payload:
        resource.description = payload.get("description")
        updated = True

    if not updated:
        return jsonify({"message": "No updatable fields provided"}), 400

    db.session.commit()
    return resource_schema.jsonify(resource), 200


@admin_bp.get("/blog-posts")
@jwt_required()
@roles_accepted("admin", "marketing")
def list_blog_posts():
    """List marketing blog posts with optional filters."""

    status = request.args.get("status")
    search = request.args.get("q")

    stmt = (
        sa.select(BlogPost)
        .options(selectinload(BlogPost.author))
        .order_by(BlogPost.created_at.desc())
    )

    if status == "published":
        stmt = stmt.where(BlogPost.is_published.is_(True))
    elif status == "draft":
        stmt = stmt.where(BlogPost.is_published.is_(False))

    if search:
        pattern = f"%{search.lower()}%"
        stmt = stmt.where(
            sa.or_(
                sa.func.lower(BlogPost.title).like(pattern),
                sa.func.lower(BlogPost.slug).like(pattern),
            )
        )

    posts = db.session.scalars(stmt).all()
    return blog_post_schema.jsonify(posts, many=True), 200


@admin_bp.post("/blog-posts")
@jwt_required()
@roles_accepted("admin", "marketing")
def create_blog_post():
    """Create a new marketing blog post."""

    payload = request.get_json() or {}
    title = payload.get("title")
    slug = payload.get("slug")
    content = payload.get("content")

    if not title or not slug or not content:
        return (
            jsonify({"message": "title, slug, and content are required"}),
            400,
        )

    existing = db.session.scalar(sa.select(BlogPost).where(BlogPost.slug == slug))
    if existing:
        return jsonify({"message": "Slug already exists"}), 409

    post = BlogPost(
        title=title,
        slug=slug,
        content=content,
        hero_image_url=payload.get("hero_image_url"),
        is_published=bool(payload.get("is_published", False)),
    )

    if current_user:
        post.author = current_user

    db.session.add(post)
    db.session.commit()
    return blog_post_schema.jsonify(post), 201


@admin_bp.put("/blog-posts/<string:slug>")
@jwt_required()
@roles_accepted("admin", "marketing")
def update_blog_post(slug: str):
    """Update an existing blog post."""

    post = db.session.scalar(sa.select(BlogPost).where(BlogPost.slug == slug))
    if not post:
        return jsonify({"message": "Blog post not found"}), 404

    payload = request.get_json() or {}
    post.title = payload.get("title", post.title)
    post.content = payload.get("content", post.content)

    if "hero_image_url" in payload:
        post.hero_image_url = payload.get("hero_image_url")

    if "slug" in payload and payload["slug"] != post.slug:
        new_slug = payload.get("slug")
        if not new_slug:
            return jsonify({"message": "slug cannot be empty"}), 400
        existing = db.session.scalar(
            sa.select(BlogPost).where(BlogPost.slug == new_slug)
        )
        if existing:
            return jsonify({"message": "Slug already exists"}), 409
        post.slug = new_slug

    if "is_published" in payload:
        post.is_published = bool(payload.get("is_published"))

    if current_user and not post.author:
        post.author = current_user

    db.session.commit()
    return blog_post_schema.jsonify(post), 200


@admin_bp.post("/blog-posts/<string:slug>/publish")
@jwt_required()
@roles_accepted("admin", "marketing")
def toggle_blog_post_publish(slug: str):
    """Publish or unpublish a blog post."""

    post = db.session.scalar(sa.select(BlogPost).where(BlogPost.slug == slug))
    if not post:
        return jsonify({"message": "Blog post not found"}), 404

    payload = request.get_json() or {}
    desired_state = payload.get("is_published")
    if desired_state is None:
        return jsonify({"message": "is_published is required"}), 400

    post.is_published = bool(desired_state)
    if post.is_published and current_user:
        post.author = current_user

    db.session.commit()
    return blog_post_schema.jsonify(post), 200


@admin_bp.delete("/blog-posts/<string:slug>")
@jwt_required()
@roles_required("admin")
def delete_blog_post(slug: str):
    """Delete a blog post (admin only)."""

    post = db.session.scalar(sa.select(BlogPost).where(BlogPost.slug == slug))
    if not post:
        return jsonify({"message": "Blog post not found"}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Blog post removed"}), 200


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


@admin_bp.get("/summary")
@jwt_required()
@roles_required("admin")
def admin_summary():
    """Return aggregate metrics for the admin dashboard."""
    user_count = db.session.scalar(sa.select(sa.func.count()).select_from(User)) or 0
    resource_pending = (
        db.session.scalar(
            sa.select(sa.func.count())
            .select_from(Resource)
            .where(Resource.ai_processing_status != "complete")
        )
        or 0
    )
    published_lessons = (
        db.session.scalar(
            sa.select(sa.func.count())
            .select_from(Lesson)
            .where(Lesson.status == "published")
        )
        or 0
    )
    unread_notifications = (
        db.session.scalar(
            sa.select(sa.func.count())
            .select_from(Notification)
            .where(Notification.is_read.is_(False))
        )
        or 0
    )
    return (
        jsonify(
            {
                "user_count": user_count,
                "resource_pending": resource_pending,
                "published_lessons": published_lessons,
                "unread_notifications": unread_notifications,
            }
        ),
        200,
    )


@admin_bp.get("/marketing/summary")
@jwt_required()
@roles_accepted("admin", "marketing")
def marketing_summary():
    """Return metrics tailored for marketing administrators."""

    published_posts = (
        db.session.scalar(
            sa.select(sa.func.count())
            .select_from(BlogPost)
            .where(BlogPost.is_published.is_(True))
        )
        or 0
    )

    draft_posts = (
        db.session.scalar(
            sa.select(sa.func.count())
            .select_from(BlogPost)
            .where(BlogPost.is_published.is_(False))
        )
        or 0
    )

    latest_stmt = (
        sa.select(BlogPost)
        .options(selectinload(BlogPost.author))
        .order_by(BlogPost.updated_at.desc())
        .limit(5)
    )
    latest_posts = db.session.scalars(latest_stmt).all()

    return (
        jsonify(
            {
                "published_posts": published_posts,
                "draft_posts": draft_posts,
                "recent_posts": [
                    {
                        "title": post.title,
                        "slug": post.slug,
                        "is_published": post.is_published,
                        "updated_at": (
                            post.updated_at.isoformat() if post.updated_at else None
                        ),
                        "author": (
                            {
                                "id": post.author.id,
                                "email": post.author.email,
                                "username": post.author.username,
                            }
                            if post.author
                            else None
                        ),
                    }
                    for post in latest_posts
                ],
            }
        ),
        200,
    )


@admin_bp.get("/notifications")
@jwt_required()
@roles_required("admin")
def admin_notifications():
    """Return recent notifications for review."""
    stmt = (
        sa.select(Notification)
        .options(selectinload(Notification.recipient))
        .order_by(Notification.created_at.desc())
        .limit(25)
    )
    notifications = db.session.scalars(stmt).all()
    payload = [
        {
            "id": notification.id,
            "subject": notification.subject,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
            "recipient": {
                "id": notification.recipient.id if notification.recipient else None,
                "email": (
                    notification.recipient.email if notification.recipient else None
                ),
                "username": (
                    notification.recipient.username if notification.recipient else None
                ),
            },
        }
        for notification in notifications
    ]
    return jsonify(payload), 200
