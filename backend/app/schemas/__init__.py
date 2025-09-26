"""Schema exports."""

from __future__ import annotations

from .auth import LoginSchema, RegisterSchema
from .flashcard import FlashcardDeckSchema, FlashcardSchema
from .lesson import LessonSchema
from .profile import ProfileSchema
from .resource import ResourceSchema
from .user import UserSchema

__all__ = [
    "LoginSchema",
    "RegisterSchema",
    "FlashcardDeckSchema",
    "FlashcardSchema",
    "LessonSchema",
    "ProfileSchema",
    "ResourceSchema",
    "UserSchema",
]
