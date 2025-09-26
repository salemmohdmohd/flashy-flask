"""User serialization schemas."""
from __future__ import annotations

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ..extensions import db
from ..models import User
from .profile import ProfileSchema


class UserSchema(SQLAlchemyAutoSchema):
    """Serialize user information."""

    profile = fields.Nested(ProfileSchema)
    roles = fields.Method("get_roles")

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("password_hash",)

    def get_roles(self, obj: User) -> list[str]:
        """Return role names for the user."""
        return [role.name for role in obj.roles]
