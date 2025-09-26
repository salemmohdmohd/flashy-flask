"""Resource service for upload and moderation."""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Iterable

from flask import current_app

from ..extensions import db
from ..models import Category, Resource, User


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class ResourceServiceError(Exception):
    """Raised when resource operations fail."""


class ResourceService:
    """Business logic for managing resources."""

    def save_resource(
        self,
        *,
        owner: User,
        filename: str,
        storage_url: str,
        description: str | None,
        categories: Iterable[str] | None,
    ) -> Resource:
        """Persist resource metadata after successful upload."""
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ResourceServiceError("File type not supported")
        mime_type, _ = mimetypes.guess_type(filename)
        resource = Resource(
            owner=owner,
            filename=Path(filename).name,
            original_name=Path(filename).name,
            storage_url=storage_url,
            description=description,
            mime_type=mime_type,
            ai_processing_status="pending",
        )
        if categories:
            resource.categories.extend(self._resolve_categories(categories))
        db.session.add(resource)
        db.session.commit()
        return resource

    def update_status(self, resource: Resource, status: str) -> Resource:
        """Update AI processing status for a resource."""
        resource.ai_processing_status = status
        db.session.commit()
        return resource

    def _resolve_categories(self, category_names: Iterable[str]) -> list[Category]:
        resolved: list[Category] = []
        for name in category_names:
            category = Category.query.filter_by(name=name).first()
            if not category:
                category = Category(name=name)
                db.session.add(category)
            resolved.append(category)
        return resolved


resource_service = ResourceService()
