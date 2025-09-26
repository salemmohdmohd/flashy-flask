"""Resource service for upload and moderation."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Category, Resource, User

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
VALID_STATUSES = {"pending", "processing", "ready", "complete", "failed"}


class ResourceServiceError(Exception):
    """Raised when resource operations fail."""


class ResourceService:
    """Business logic for managing resources."""

    def save_resource(
        self,
        *,
        owner: User,
        uploaded_file: FileStorage | None = None,
        filename: str | None = None,
        storage_url: str | None = None,
        description: str | None = None,
        categories: Iterable[str] | None = None,
    ) -> Resource:
        """Persist resource metadata or handle an uploaded file."""

        normalized_categories = self._normalize_categories(categories)

        if uploaded_file is not None:
            original_name = Path(uploaded_file.filename or "").name
            if not original_name:
                raise ResourceServiceError("Uploaded file is missing a filename")
            extension = Path(original_name).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                raise ResourceServiceError("File type not supported")

            secure_name = secure_filename(original_name)
            unique_name = f"{uuid4().hex}_{secure_name}" if secure_name else uuid4().hex
            configured_path = current_app.config.get("UPLOAD_FOLDER", "uploads")
            upload_dir = Path(configured_path)
            if not upload_dir.is_absolute():
                upload_dir = Path(current_app.root_path).joinpath(upload_dir).resolve()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / unique_name
            uploaded_file.save(file_path)

            mime_type = uploaded_file.mimetype or mimetypes.guess_type(original_name)[0]
            text_content = self._extract_text(file_path, extension)

            resource = Resource(
                owner=owner,
                filename=secure_name or original_name,
                original_name=original_name,
                storage_url=str(file_path),
                description=description,
                mime_type=mime_type,
                text_content=text_content,
                ai_processing_status="ready" if text_content else "pending",
            )
        elif filename and storage_url:
            original_name = Path(filename).name
            extension = Path(original_name).suffix.lower()
            if extension and extension not in ALLOWED_EXTENSIONS:
                raise ResourceServiceError("File type not supported")
            mime_type, _ = mimetypes.guess_type(original_name)
            resource = Resource(
                owner=owner,
                filename=original_name,
                original_name=original_name,
                storage_url=storage_url,
                description=description,
                mime_type=mime_type,
                text_content=None,
                ai_processing_status="pending",
            )
        else:
            raise ResourceServiceError(
                "Either an uploaded_file or filename and storage_url must be provided"
            )

        if normalized_categories:
            resource.categories.extend(self._resolve_categories(normalized_categories))

        db.session.add(resource)
        db.session.commit()
        return resource

    def update_status(self, resource: Resource, status: str) -> Resource:
        """Update AI processing status."""

        normalized_status = (status or "").strip().lower()
        if normalized_status not in VALID_STATUSES:
            raise ResourceServiceError("Invalid status value")
        resource.ai_processing_status = normalized_status
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

    def _normalize_categories(self, categories: Iterable[str] | None) -> list[str]:
        if not categories:
            return []
        if isinstance(categories, str):
            categories = [
                value.strip() for value in categories.split(",") if value.strip()
            ]
        else:
            categories = [
                value.strip() for value in categories if value and value.strip()
            ]
        normalized = {category.lower(): category for category in categories}
        return sorted(normalized.values())

    def _extract_text(self, file_path: Path, extension: str) -> str | None:
        """Extract textual content from supported file types."""
        text = ""
        try:
            if extension == ".pdf":
                from PyPDF2 import PdfReader

                reader = PdfReader(str(file_path))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            elif extension == ".docx":
                from docx import Document

                document = Document(str(file_path))
                text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            elif extension == ".txt":
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            else:
                return None
        except Exception as exc:  # pragma: no cover - defensive logging
            current_app.logger.warning(
                "Failed to extract text from %s: %s", file_path, exc
            )
            return None

        normalized = " ".join(text.split())
        return normalized or None


resource_service = ResourceService()
