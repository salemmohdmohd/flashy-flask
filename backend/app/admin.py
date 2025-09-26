"""Flask-Admin configuration."""

from __future__ import annotations

from flask import abort
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import current_user

from .extensions import admin, db
from .models import (
    BlogPost,
    Category,
    Flashcard,
    FlashcardDeck,
    Lesson,
    Notification,
    Profile,
    Resource,
    Role,
    User,
)


class SecureModelView(ModelView):
    """ModelView enforcing admin authentication."""

    def is_accessible(self) -> bool:  # type: ignore[override]
        return bool(
            current_user
            and current_user.is_authenticated
            and current_user.has_role("admin")
        )

    def inaccessible_callback(self, name, **kwargs):  # type: ignore[override]
        abort(403)


class SecureAdminIndexView(AdminIndexView):
    """Custom admin index that enforces authentication."""

    def is_accessible(self) -> bool:  # type: ignore[override]
        return bool(
            current_user
            and current_user.is_authenticated
            and current_user.has_role("admin")
        )

    def inaccessible_callback(self, name, **kwargs):  # type: ignore[override]
        abort(403)


def setup_admin(app) -> Admin:
    """Register admin views."""
    admin._set_admin_index_view(SecureAdminIndexView())  # type: ignore[attr-defined]
    admin.init_app(app)

    models = [
        User,
        Role,
        Profile,
        Category,
        Resource,
        FlashcardDeck,
        Flashcard,
        Lesson,
        BlogPost,
        Notification,
    ]
    for model in models:
        admin.add_view(SecureModelView(model, db.session))
    return admin
