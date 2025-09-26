"""Profile schema."""

from __future__ import annotations

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ..extensions import db
from ..models import Profile


class ProfileSchema(SQLAlchemyAutoSchema):
    """Serialize profile data."""

    class Meta:
        model = Profile
        sqla_session = db.session
        load_instance = True
