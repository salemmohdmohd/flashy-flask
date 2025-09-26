"""Flashcard-related models."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .resource import Resource
    from .user import User


class FlashcardDeck(TimestampMixin, Base):
    """Deck of flashcards generated from a resource."""

    __tablename__ = "flashcard_decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    resource_id: Mapped[int | None] = mapped_column(
        ForeignKey("resources.id", ondelete="SET NULL")
    )

    owner: Mapped["User"] = relationship("User", back_populates="flashcard_decks")
    resource: Mapped["Resource" | None] = relationship(
        "Resource", back_populates="flashcard_decks"
    )
    flashcards: Mapped[List["Flashcard"]] = relationship(
        "Flashcard",
        back_populates="deck",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<FlashcardDeck {self.title}>"


class Flashcard(TimestampMixin, Base):
    """Individual flashcard within a deck."""

    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("flashcard_decks.id", ondelete="CASCADE")
    )

    deck: Mapped[FlashcardDeck] = relationship(
        "FlashcardDeck", back_populates="flashcards"
    )

    def __repr__(self) -> str:
        return f"<Flashcard {self.id}>"
