"""Tests for the resource service upload workflow."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from werkzeug.datastructures import FileStorage

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User
from backend.app.services.resource_service import resource_service


def test_save_resource_from_text_file(tmp_path):
    app = create_app("backend.config.TestingConfig")
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        db.create_all()
        try:
            user = User(email="test@example.com", username="tester")
            user.set_password("Example123!")
            db.session.add(user)
            db.session.commit()

            storage = FileStorage(
                stream=BytesIO(b"Sample lesson content for extraction."),
                filename="lesson.txt",
                content_type="text/plain",
            )

            resource = resource_service.save_resource(
                owner=user,
                uploaded_file=storage,
                description="Test upload",
                categories=["Science", "Physics"],
            )

            assert resource.id is not None
            assert resource.text_content is not None
            assert "Sample lesson content" in resource.text_content
            assert resource.ai_processing_status == "ready"
            stored_path = Path(resource.storage_url)
            assert stored_path.exists()
            assert sorted(category.name for category in resource.categories) == [
                "Physics",
                "Science",
            ]
        finally:
            db.session.remove()
            db.drop_all()
