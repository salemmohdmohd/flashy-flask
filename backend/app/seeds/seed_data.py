"""Database seed command."""

from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent

import click
import sqlalchemy as sa
from flask import current_app
from flask.cli import with_appcontext

from ..extensions import db
from ..models import (
    FAQ,
    BlogPost,
    Category,
    Flashcard,
    FlashcardDeck,
    Lesson,
    Notification,
    Profile,
    Resource,
    Role,
    User,
)


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    """Seed roles, users, and representative domain data."""
    roles = ["student", "teacher", "expert", "admin", "marketing"]
    for name in roles:
        if not db.session.scalar(sa.select(Role).where(Role.name == name)):
            db.session.add(Role(name=name, description=f"{name.title()} role"))
    db.session.commit()

    config = current_app.config

    admin = _ensure_user(
        email=_config_or_env(config, "ADMIN_EMAIL", "admin@example.com"),
        username=_config_or_env(config, "ADMIN_USERNAME", "admin"),
        password=_config_or_env(config, "ADMIN_PASSWORD", "ChangeMe123!"),
        first_name="Avery",
        last_name="Admin",
        roles=["admin"],
    )

    teacher = _ensure_user(
        email=_config_or_env(config, "TEACHER_EMAIL", "teacher@example.com"),
        username=_config_or_env(config, "TEACHER_USERNAME", "teacher"),
        password=_config_or_env(config, "TEACHER_PASSWORD", "TeachMe123!"),
        first_name="Taylor",
        last_name="Teacher",
        roles=["teacher"],
    )

    expert = _ensure_user(
        email=_config_or_env(config, "EXPERT_EMAIL", "expert@example.com"),
        username=_config_or_env(config, "EXPERT_USERNAME", "expert"),
        password=_config_or_env(config, "EXPERT_PASSWORD", "Expert123!"),
        first_name="Elliott",
        last_name="Expert",
        roles=["expert"],
    )

    marketing = _ensure_user(
        email=_config_or_env(config, "MARKETING_EMAIL", "marketing@example.com"),
        username=_config_or_env(config, "MARKETING_USERNAME", "marketing"),
        password=_config_or_env(config, "MARKETING_PASSWORD", "Market123!"),
        first_name="Marin",
        last_name="Marketing",
        roles=["marketing"],
    )

    student = _ensure_user(
        email=_config_or_env(config, "USER_EMAIL", "student@example.com"),
        username=_config_or_env(config, "USER_USERNAME", "student"),
        password=_config_or_env(config, "USER_PASSWORD", "Study123!"),
        first_name="Sydney",
        last_name="Student",
        roles=["student"],
    )

    db.session.commit()

    ai_category = _ensure_category(
        name="AI Fundamentals",
        description="Core concepts for the Flashy onboarding curriculum",
    )

    upload_root = Path(config.get("UPLOAD_FOLDER", "uploads"))
    if not upload_root.is_absolute():
        upload_root = Path(current_app.root_path).joinpath(upload_root).resolve()
    seed_dir = upload_root / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)

    resource = _ensure_resource(
        owner=teacher,
        category=ai_category,
        storage_dir=seed_dir,
    )

    deck = _ensure_flashcard_deck(owner=teacher, resource=resource)

    _ensure_lesson(author=expert, resource=resource, summary_source=deck)

    _ensure_blog_post(author=marketing)
    _ensure_faq()
    _seed_notifications(
        admin=admin,
        teacher=teacher,
        expert=expert,
        marketing=marketing,
        student=student,
    )

    db.session.commit()

    click.echo("✅ Seed data applied with roles, users, and sample curriculum content")


def _ensure_user(
    *,
    email: str,
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    roles: list[str],
) -> User:
    user = db.session.scalar(sa.select(User).where(User.email == email))
    if user:
        return user

    user = User(email=email, username=username)
    user.set_password(password)

    profile = Profile(
        first_name=first_name, last_name=last_name, role_title=roles[0].title()
    )
    user.profile = profile

    for role_name in roles:
        role = db.session.scalar(sa.select(Role).where(Role.name == role_name))
        if role:
            user.roles.append(role)

    db.session.add(user)
    db.session.flush()
    return user


def _ensure_category(*, name: str, description: str) -> Category:
    category = db.session.scalar(sa.select(Category).where(Category.name == name))
    if category:
        return category
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.flush()
    return category


def _ensure_resource(*, owner: User, category: Category, storage_dir: Path) -> Resource:
    resource = db.session.scalar(
        sa.select(Resource).where(Resource.filename == "ai_fundamentals.txt")
    )
    if resource:
        return resource

    sample_text = dedent(
        """
        Artificial Intelligence (AI) combines data, algorithms, and computing power to
        create systems that learn from experience. Effective flashcards isolate single
        concepts—definitions, formulas, process steps—so the learner can practice active
        recall. Lessons should always close with a reflective prompt that checks for
        understanding and encourages knowledge transfer to real scenarios.
        """
    ).strip()

    sample_file = storage_dir / "ai_fundamentals.txt"
    if not sample_file.exists():
        sample_file.write_text(sample_text, encoding="utf-8")

    resource = Resource(
        owner=owner,
        filename=sample_file.name,
        original_name=sample_file.name,
        storage_url=str(sample_file),
        description="Foundational AI study pack used for the default Flashy walkthrough.",
        text_content=sample_text,
        mime_type="text/plain",
        ai_processing_status="complete",
    )
    resource.categories.append(category)
    db.session.add(resource)
    db.session.flush()
    return resource


def _ensure_flashcard_deck(*, owner: User, resource: Resource) -> FlashcardDeck:
    deck = db.session.scalar(
        sa.select(FlashcardDeck).where(FlashcardDeck.title == "AI Fundamentals Deck")
    )
    if deck:
        return deck

    deck = FlashcardDeck(
        title="AI Fundamentals Deck",
        description="Starter deck illustrating how Flashy structures AI core concepts.",
        owner=owner,
        resource=resource,
    )
    db.session.add(deck)

    flashcards = [
        {
            "question": "What is the primary goal of active recall?",
            "answer": "To strengthen memory by forcing the learner to retrieve information without cues.",
        },
        {
            "question": "Name one benefit of spacing flashcard reviews over several days.",
            "answer": "Spacing combats the forgetting curve and promotes long-term retention.",
        },
        {
            "question": "Which three ingredients power most AI systems?",
            "answer": "Large datasets, statistical algorithms, and scalable compute resources.",
        },
        {
            "question": "Why should lessons end with a reflection prompt?",
            "answer": "Reflection links new knowledge to real situations, improving transfer and mastery.",
        },
    ]

    for data in flashcards:
        db.session.add(
            Flashcard(question=data["question"], answer=data["answer"], deck=deck)
        )

    db.session.flush()
    return deck


def _ensure_lesson(
    *, author: User, resource: Resource, summary_source: FlashcardDeck
) -> Lesson:
    lesson = db.session.scalar(
        sa.select(Lesson).where(Lesson.title == "AI Fundamentals Lesson")
    )
    if lesson:
        return lesson

    lesson = Lesson(
        title="AI Fundamentals Lesson",
        content="\n\n".join(
            f"Q: {card.question}\nA: {card.answer}"
            for card in summary_source.flashcards
        ),
        summary=summary_source.description,
        author=author,
        resource=resource,
        status="published",
    )
    lesson.categories.extend(resource.categories)
    db.session.add(lesson)
    db.session.flush()
    return lesson


def _ensure_blog_post(*, author: User) -> BlogPost:
    post = db.session.scalar(
        sa.select(BlogPost).where(BlogPost.slug == "supercharge-your-study-habits")
    )
    if post:
        return post
    post = BlogPost(
        title="Supercharge Your Study Habits With Flashy",
        slug="supercharge-your-study-habits",
        content=dedent(
            """
            Learn how Flashy pairs AI-driven insights with evidence-backed pedagogy. Our admin
            dashboard helps educators moderate resources, while auto-generated flashcards give
            students a jump-start on practice. Try uploading your first resource to watch Gemini
            craft a lesson plan in minutes.
            """
        ).strip(),
        author=author,
        is_published=True,
    )
    db.session.add(post)
    db.session.flush()
    return post


def _ensure_faq() -> None:
    faq = db.session.scalar(
        sa.select(FAQ).where(FAQ.question == "How does Flashy generate flashcards?")
    )
    if faq:
        return
    faq = FAQ(
        question="How does Flashy generate flashcards?",
        answer="Flashy securely sends your approved resource text to Google Gemini and validates the response before saving.",
        is_active=True,
    )
    db.session.add(faq)


def _seed_notifications(
    *, admin: User, teacher: User, expert: User, marketing: User, student: User
) -> None:
    """Create sample notifications for each persona."""

    _ensure_notification(
        recipient=admin,
        subject="Daily moderation digest",
        message=(
            "Review new resources awaiting approval and publish outstanding AI-generated lessons."
        ),
    )

    _ensure_notification(
        recipient=teacher,
        subject="AI deck ready for review",
        message=(
            "Your AI Fundamentals upload produced a flashcard deck. Validate the questions before sharing."
        ),
    )

    _ensure_notification(
        recipient=expert,
        subject="Lesson published",
        message="The AI Fundamentals lesson is live. Monitor learner scores and iterate if needed.",
    )

    _ensure_notification(
        recipient=marketing,
        subject="Blog spotlight gaining traction",
        message=(
            "Traffic to 'Supercharge Your Study Habits' is climbing. Plan a follow-up campaign targeting educators."
        ),
    )

    _ensure_notification(
        recipient=student,
        subject="Welcome to Flashy",
        message="Start with the AI Fundamentals deck and schedule spaced reviews to maximize retention.",
    )


def _ensure_notification(
    *, recipient: User, subject: str, message: str
) -> Notification:
    notification = db.session.scalar(
        sa.select(Notification).where(
            Notification.recipient_id == recipient.id, Notification.subject == subject
        )
    )
    if notification:
        return notification
    notification = Notification(recipient=recipient, subject=subject, message=message)
    db.session.add(notification)
    db.session.flush()
    return notification


def _config_or_env(config, key: str, default: str) -> str:
    """Return a configuration value with an environment fallback."""
    return config.get(key) or os.getenv(key, default) or default
