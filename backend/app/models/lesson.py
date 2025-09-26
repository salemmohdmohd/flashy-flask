"""Lesson model representing structured learning content."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .category import lesson_categories

if TYPE_CHECKING:
    from .category import Category
    from .resource import Resource
    from .user import User


class Lesson(TimestampMixin, Base):
    """Lesson generated from resources and curated by experts."""

    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resource_id: Mapped[int | None] = mapped_column(
        ForeignKey("resources.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(String(50), default="draft")

    author: Mapped["User" | None] = relationship("User", back_populates="lessons")
    resource: Mapped["Resource" | None] = relationship("Resource")
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        secondary=lesson_categories,
        back_populates="lessons",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Lesson {self.title}>"
