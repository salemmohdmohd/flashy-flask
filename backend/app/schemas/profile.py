"""Profile schema."""

from __future__ import annotations

from ..extensions import db, ma
from ..models import Profile


class ProfileSchema(ma.SQLAlchemyAutoSchema):
    """Serialize profile data."""

    class Meta:
        model = Profile
        sqla_session = db.session
        load_instance = True
