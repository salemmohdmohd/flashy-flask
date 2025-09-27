"""Schema exports."""

from __future__ import annotations

from .auth import LoginSchema, RegisterSchema
from .blog import BlogPostSchema
from .flashcard import FlashcardDeckSchema, FlashcardSchema
from .lesson import LessonSchema
from .profile import ProfileSchema
from .resource import ResourceSchema
from .user import UserSchema

__all__ = [
    "LoginSchema",
    "RegisterSchema",
    "BlogPostSchema",
    "FlashcardDeckSchema",
    "FlashcardSchema",
    "LessonSchema",
    "ProfileSchema",
    "ResourceSchema",
    "UserSchema",
]
