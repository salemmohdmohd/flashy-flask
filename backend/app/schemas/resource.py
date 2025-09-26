"""Resource schemas."""

from __future__ import annotations

from marshmallow import fields

from ..extensions import db, ma
from ..models import Resource


class ResourceSchema(ma.SQLAlchemyAutoSchema):
    """Serialize resource data."""

    categories = fields.List(fields.Str())

    class Meta:
        model = Resource
        sqla_session = db.session
        load_instance = True
        include_fk = True

    def dump(self, obj, *, many: bool | None = None):  # type: ignore[override]
        payload = super().dump(obj, many=many)
        if many:
            for resource, data in zip(obj, payload):  # type: ignore[arg-type]
                data["categories"] = [category.name for category in resource.categories]
        else:
            payload["categories"] = [category.name for category in obj.categories]
        return payload
