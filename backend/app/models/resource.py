"""Resource model representing uploaded study materials."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .category import resource_categories

if TYPE_CHECKING:
    from .category import Category
    from .flashcard import FlashcardDeck
    from .user import User


class Resource(TimestampMixin, Base):
    """Uploaded learning material."""

    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120))
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    text_content: Mapped[str | None] = mapped_column(Text)
    ai_processing_status: Mapped[str] = mapped_column(String(50), default="pending")

    owner: Mapped["User"] = relationship("User", back_populates="resources")
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        secondary=resource_categories,
        back_populates="resources",
        lazy="selectin",
    )
    flashcard_decks: Mapped[List["FlashcardDeck"]] = relationship(
        "FlashcardDeck",
        back_populates="resource",
    )

    def __repr__(self) -> str:
        return f"<Resource {self.filename}>"

    def text_excerpt(self, length: int = 500) -> str | None:
        """Return a truncated excerpt of the extracted text content."""
        if not self.text_content:
            return None
        if len(self.text_content) <= length:
            return self.text_content
        return f"{self.text_content[:length].rstrip()}…"
