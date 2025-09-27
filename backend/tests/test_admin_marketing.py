"""Tests for admin and marketing backend endpoints."""

from __future__ import annotations

from typing import Callable

import pytest
from app import create_app
from app.extensions import db
from app.models import BlogPost, Resource, Role, User


@pytest.fixture()
def test_app(tmp_path):
    """Provide a Flask test app with an isolated SQLite database."""

    app = create_app("backend.config.TestingConfig")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path}/admin_marketing.db"

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


@pytest.fixture()
def create_user() -> Callable[[str, str, list[str]], User]:
    def _create_user(email: str, password: str, roles: list[str]) -> User:
        user = User(email=email, username=email.split("@")[0])
        user.set_password(password)
        for role_name in roles:
            role = db.session.scalar(db.select(Role).where(Role.name == role_name))
            if role is None:
                role = Role(name=role_name, description=f"{role_name.title()} role")
                db.session.add(role)
                db.session.flush()
            user.roles.append(role)
        db.session.add(user)
        db.session.commit()
        return user

    return _create_user


@pytest.fixture()
def create_resource(
    create_user: Callable[[str, str, list[str]], User],
) -> Callable[..., Resource]:
    def _create_resource(
        *,
        owner: User | None = None,
        filename: str = "study.pdf",
        original_name: str = "Study Guide.pdf",
        storage_url: str = "https://cdn.example.com/study.pdf",
        ai_processing_status: str = "pending",
    ) -> Resource:
        resource_owner = owner or create_user(
            "owner@example.com", "Owner123!", ["user"]
        )
        resource = Resource(
            owner=resource_owner,
            filename=filename,
            original_name=original_name,
            storage_url=storage_url,
            mime_type="application/pdf",
            ai_processing_status=ai_processing_status,
        )
        db.session.add(resource)
        db.session.commit()
        return resource

    return _create_resource


def login(client, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    data = response.get_json()
    return data["access_token"]


def test_marketing_can_manage_blog_posts(client, create_user):
    create_user("marketing@example.com", "Market123!", ["marketing"])

    token = login(client, "marketing@example.com", "Market123!")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/api/v1/admin/blog-posts",
        json={
            "title": "Growth playbook",
            "slug": "growth-playbook",
            "content": "Content roadmap for the upcoming quarter.",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201

    list_resp = client.get("/api/v1/admin/blog-posts", headers=headers)
    assert list_resp.status_code == 200
    posts = list_resp.get_json()
    assert len(posts) == 1
    assert posts[0]["slug"] == "growth-playbook"

    summary_resp = client.get("/api/v1/admin/marketing/summary", headers=headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.get_json()
    assert summary["draft_posts"] == 1
    assert summary["published_posts"] == 0


def test_super_admin_can_delete_blog_post(client, create_user):
    marketing_user = create_user("marketer@example.com", "Market123!", ["marketing"])
    admin_user = create_user("admin@example.com", "ChangeMe123!", ["admin"])

    post = BlogPost(
        title="Launch announcement",
        slug="launch-announcement",
        content="We are launching a new feature.",
        author=marketing_user,
        is_published=True,
    )
    db.session.add(post)
    db.session.commit()

    token = login(client, "admin@example.com", "ChangeMe123!")
    headers = {"Authorization": f"Bearer {token}"}

    delete_resp = client.delete(
        "/api/v1/admin/blog-posts/launch-announcement", headers=headers
    )
    assert delete_resp.status_code == 200

    remaining = db.session.scalar(db.select(db.func.count()).select_from(BlogPost))
    assert remaining == 0


def test_admin_can_update_user_state_and_roles(client, create_user):
    admin = create_user("super@example.com", "ChangeMe123!", ["admin"])
    staff = create_user("staff@example.com", "Staff123!", ["marketing"])

    token = login(client, admin.email, "ChangeMe123!")
    headers = {"Authorization": f"Bearer {token}"}

    deactivate_resp = client.patch(
        f"/api/v1/admin/users/{staff.id}",
        json={"is_active": False},
        headers=headers,
    )
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.get_json()["is_active"] is False

    roles_resp = client.patch(
        f"/api/v1/admin/users/{staff.id}",
        json={"roles": ["marketing", "admin"]},
        headers=headers,
    )
    assert roles_resp.status_code == 200
    assert set(roles_resp.get_json()["roles"]) == {"marketing", "admin"}


def test_admin_can_update_resource_status(client, create_user, create_resource):
    admin = create_user("mod@example.com", "ChangeMe123!", ["admin"])
    owner = create_user("learner@example.com", "Learner123!", ["user"])
    resource = create_resource(owner=owner)

    token = login(client, admin.email, "ChangeMe123!")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.patch(
        f"/api/v1/admin/resources/{resource.id}",
        json={"ai_processing_status": "complete"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["ai_processing_status"] == "complete"


def test_marketing_can_update_post_slug(client, create_user):
    marketer = create_user("creator@example.com", "Market123!", ["marketing"])

    token = login(client, marketer.email, "Market123!")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/api/v1/admin/blog-posts",
        json={
            "title": "Product deep dive",
            "slug": "product-deep-dive",
            "content": "Long-form content for launch",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201

    update_resp = client.put(
        "/api/v1/admin/blog-posts/product-deep-dive",
        json={
            "title": "Product deep dive",
            "slug": "product-story",
            "content": "Updated content",
        },
        headers=headers,
    )
    assert update_resp.status_code == 200
    payload = update_resp.get_json()
    assert payload["slug"] == "product-story"

    # Ensure the new slug can be retrieved
    list_resp = client.get(
        "/api/v1/admin/blog-posts",
        headers=headers,
    )
    assert list_resp.status_code == 200
    slugs = {entry["slug"] for entry in list_resp.get_json()}
    assert "product-story" in slugs
    assert "product-deep-dive" not in slugs
