"""Blog post serialization schemas."""

from __future__ import annotations

from marshmallow import fields

from ..extensions import db, ma
from ..models import BlogPost
from .user import UserSchema


class BlogPostSchema(ma.SQLAlchemyAutoSchema):
    """Serialize marketing blog posts."""

    author = fields.Nested(UserSchema, allow_none=True)

    class Meta:
        model = BlogPost
        sqla_session = db.session
        load_instance = True
        include_fk = True
        exclude = ("author_id",)
