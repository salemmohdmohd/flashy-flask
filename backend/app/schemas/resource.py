"""Resource schemas."""

from __future__ import annotations

from flask import url_for
from marshmallow import fields

from ..extensions import db, ma
from ..models import Resource


class ResourceSchema(ma.SQLAlchemyAutoSchema):
    """Serialize resource data."""

    categories = fields.List(fields.Str())
    owner_email = fields.Method("get_owner_email")
    download_url = fields.Method("get_download_url")
    content_preview = fields.Method("get_content_preview")

    class Meta:
        model = Resource
        sqla_session = db.session
        load_instance = True
        include_fk = True
        exclude = ("text_content",)

    def dump(self, obj, *, many: bool | None = None):  # type: ignore[override]
        payload = super().dump(obj, many=many)
        if many:
            for resource, data in zip(obj, payload):  # type: ignore[arg-type]
                data["categories"] = [category.name for category in resource.categories]
                data["download_url"] = self.get_download_url(resource)
                data["content_preview"] = self.get_content_preview(resource)
                if resource.storage_url and not resource.storage_url.startswith("http"):
                    data["storage_url"] = data["download_url"]
        else:
            payload["categories"] = [category.name for category in obj.categories]
            payload["download_url"] = self.get_download_url(obj)
            payload["content_preview"] = self.get_content_preview(obj)
            if obj.storage_url and not obj.storage_url.startswith("http"):
                payload["storage_url"] = payload["download_url"]
        return payload

    def get_download_url(self, obj: Resource) -> str | None:
        """Return a download URL for locally stored resources."""
        if not obj.storage_url:
            return None
        if obj.storage_url.startswith("http"):
            return obj.storage_url
        try:
            return url_for(
                "resources.download_resource", resource_id=obj.id, _external=True
            )
        except RuntimeError:
            # Fallback for contexts without a request (e.g., CLI)
            return obj.storage_url

    def get_content_preview(self, obj: Resource) -> str | None:
        """Return a truncated preview of the extracted text content."""
        return obj.text_excerpt()

    def get_owner_email(self, obj: Resource) -> str | None:
        """Return the email address of the resource owner if available."""
        return obj.owner.email if obj.owner else None
