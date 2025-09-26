"""Lesson schema."""

from __future__ import annotations

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ..extensions import db
from ..models import Lesson


class LessonSchema(SQLAlchemyAutoSchema):
    """Serialize lesson data."""

    categories = fields.List(fields.Str())

    class Meta:
        model = Lesson
        sqla_session = db.session
        load_instance = True
        include_fk = True

    def dump(self, obj, *, many: bool | None = None):  # type: ignore[override]
        payload = super().dump(obj, many=many)
        if many:
            for lesson, data in zip(obj, payload):  # type: ignore[arg-type]
                data["categories"] = [category.name for category in lesson.categories]
        else:
            payload["categories"] = [category.name for category in obj.categories]
        return payload
