"""Role model for RBAC."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, MetaData, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User

# Naming convention for Alembic
metadata_obj = MetaData()


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(TimestampMixin, Base):
    """Role assigned to users."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"
