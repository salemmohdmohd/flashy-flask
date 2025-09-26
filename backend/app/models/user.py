"""User model with authentication helpers."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import bcrypt
from .base import Base, TimestampMixin
from .role import user_roles

if TYPE_CHECKING:
    from .role import Role

if TYPE_CHECKING:
    from .flashcard import FlashcardDeck
    from .lesson import Lesson
    from .notification import Notification
    from .profile import Profile
    from .resource import Resource


class User(TimestampMixin, Base):
    """Core user entity."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
    profile: Mapped[Optional["Profile"]] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        lazy="joined",
    )
    resources: Mapped[List["Resource"]] = relationship(
        "Resource",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    flashcard_decks: Mapped[List["FlashcardDeck"]] = relationship(
        "FlashcardDeck",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="recipient",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def has_role(self, role_name: str) -> bool:
        """Check whether the user possesses a given role."""
        return any(role.name == role_name for role in self.roles)

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def is_authenticated(self) -> bool:
        """Compatibility property for admin views."""
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return str(self.id)
