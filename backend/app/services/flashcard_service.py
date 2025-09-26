"""Flashcard generation services."""
from __future__ import annotations

from typing import Iterable

from flask import current_app

from ..extensions import db
from ..models import Flashcard, FlashcardDeck, Resource, User
from .gemini_service import GeminiService, gemini_service


class FlashcardServiceError(Exception):
    """Raised when flashcard operations fail."""


class FlashcardService:
    """Service orchestrating flashcard lifecycle."""

    def __init__(self, ai_service: GeminiService) -> None:
        self._ai_service = ai_service

    def generate_deck(self, *, owner: User, resource: Resource, chunk_size: int = 800) -> FlashcardDeck:
        """Generate a deck of flashcards from a resource."""
        if resource.owner_id != owner.id and not owner.has_role("admin"):
            raise FlashcardServiceError("Unauthorized to generate flashcards for this resource")

        chunks = self._ai_service.chunk_resource(resource, chunk_size=chunk_size)
        ai_payload = self._ai_service.generate_flashcards(chunks)

        deck = FlashcardDeck(
            title=f"AI Deck for {resource.original_name}",
            description=ai_payload.summary,
            owner=owner,
            resource=resource,
        )
        db.session.add(deck)
        for item in ai_payload.cards:
            flashcard = Flashcard(question=item.question, answer=item.answer, deck=deck)
            db.session.add(flashcard)
        db.session.commit()
        return deck

    def update_cards(self, *, deck: FlashcardDeck, cards: Iterable[dict[str, str]]) -> FlashcardDeck:
        """Replace deck cards with new content."""
        Flashcard.query.filter_by(deck_id=deck.id).delete()
        for card in cards:
            flashcard = Flashcard(question=card["question"], answer=card["answer"], deck=deck)
            db.session.add(flashcard)
        db.session.commit()
        return deck


flashcard_service = FlashcardService(gemini_service)
