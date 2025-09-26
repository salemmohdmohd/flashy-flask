"""Flashcard schemas."""

from __future__ import annotations

from marshmallow import fields

from ..extensions import db, ma
from ..models import Flashcard, FlashcardDeck


class FlashcardSchema(ma.SQLAlchemyAutoSchema):
    """Serialize flashcards."""

    class Meta:
        model = Flashcard
        sqla_session = db.session
        load_instance = True
        include_fk = True


class FlashcardDeckSchema(ma.SQLAlchemyAutoSchema):
    """Serialize flashcard decks."""

    flashcards = fields.Nested(FlashcardSchema, many=True)

    class Meta:
        model = FlashcardDeck
        sqla_session = db.session
        load_instance = True
        include_fk = True
