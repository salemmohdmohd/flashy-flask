"""Flashcard schemas."""

from __future__ import annotations

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ..extensions import db
from ..models import Flashcard, FlashcardDeck


class FlashcardSchema(SQLAlchemyAutoSchema):
    """Serialize flashcards."""

    class Meta:
        model = Flashcard
        sqla_session = db.session
        load_instance = True
        include_fk = True


class FlashcardDeckSchema(SQLAlchemyAutoSchema):
    """Serialize flashcard decks."""

    flashcards = fields.Nested(FlashcardSchema, many=True)

    class Meta:
        model = FlashcardDeck
        sqla_session = db.session
        load_instance = True
        include_fk = True
