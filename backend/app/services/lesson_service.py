"""Lesson services handling AI generation and lifecycle."""

from __future__ import annotations

from ..extensions import db
from ..models import Lesson, Resource, User
from .gemini_service import GeminiService, GeminiServiceError, gemini_service


class LessonServiceError(Exception):
    """Raised when lesson operations fail."""


class LessonService:
    """Encapsulates lesson workflows."""

    def __init__(self, ai_service: GeminiService) -> None:
        self._ai_service = ai_service

    def generate_lesson(self, *, author: User, resource: Resource) -> Lesson:
        """Generate a lesson from a resource."""
        if resource.owner_id != author.id and not author.has_role("admin"):
            raise LessonServiceError(
                "Unauthorized to generate lesson for this resource"
            )
        try:
            chunks = self._ai_service.chunk_resource(resource, chunk_size=1000)
            payload = self._ai_service.generate_flashcards(chunks)
        except GeminiServiceError as exc:  # pragma: no cover - relies on external API
            resource.ai_processing_status = "failed"
            db.session.commit()
            raise LessonServiceError(str(exc)) from exc
        lesson = Lesson(
            title=f"Lesson on {resource.original_name}",
            content="\n".join(
                f"Q: {card.question}\nA: {card.answer}" for card in payload.cards
            ),
            summary=payload.summary,
            author=author,
            resource=resource,
            status="draft",
        )
        db.session.add(lesson)
        resource.ai_processing_status = "complete"
        db.session.commit()
        return lesson

    def publish_lesson(self, lesson: Lesson) -> Lesson:
        """Publish a lesson."""
        lesson.status = "published"
        db.session.commit()
        return lesson


lesson_service = LessonService(gemini_service)
