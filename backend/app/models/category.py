"""Category model used for tagging content."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .lesson import Lesson
    from .resource import Resource

resource_categories = Table(
    "resource_categories",
    Base.metadata,
    Column("resource_id", ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

lesson_categories = Table(
    "lesson_categories",
    Base.metadata,
    Column("lesson_id", ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Category(TimestampMixin, Base):
    """Category entity."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    resources: Mapped[List["Resource"]] = relationship(
        "Resource",
        secondary=resource_categories,
        back_populates="categories",
        lazy="selectin",
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        secondary=lesson_categories,
        back_populates="categories",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
