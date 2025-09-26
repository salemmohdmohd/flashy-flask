"""Public content endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify

from ..models import FAQ, BlogPost, FlashcardDeck, Lesson
from ..schemas import FlashcardDeckSchema, LessonSchema

public_bp = Blueprint("public", __name__)
deck_schema = FlashcardDeckSchema()
lesson_schema = LessonSchema()


@public_bp.get("/lessons")
def list_public_lessons():
    """Return published lessons."""
    lessons = (
        Lesson.query.filter_by(status="published")
        .order_by(Lesson.created_at.desc())
        .all()
    )
    return lesson_schema.jsonify(lessons, many=True), 200


@public_bp.get("/flashcards")
def list_public_decks():
    """Return flashcard decks flagged as public."""
    decks = (
        FlashcardDeck.query.order_by(FlashcardDeck.created_at.desc()).limit(20).all()
    )
    return deck_schema.jsonify(decks, many=True), 200


@public_bp.get("/blog")
def list_posts():
    """Return published blog posts."""
    posts = (
        BlogPost.query.filter_by(is_published=True)
        .order_by(BlogPost.created_at.desc())
        .with_entities(
            BlogPost.title, BlogPost.slug, BlogPost.content, BlogPost.hero_image_url
        )
        .all()
    )
    return (
        jsonify(
            [
                {
                    "title": title,
                    "slug": slug,
                    "content": content,
                    "hero_image_url": hero_image_url,
                }
                for title, slug, content, hero_image_url in posts
            ]
        ),
        200,
    )


@public_bp.get("/faq")
def list_faq():
    """Return active FAQs."""
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.created_at.asc()).all()
    return (
        jsonify([{"question": faq.question, "answer": faq.answer} for faq in faqs]),
        200,
    )
