"""Notification dispatch utilities."""

from __future__ import annotations

from flask import current_app
from flask_mail import Message

from ..extensions import db, mail
from ..models import Notification, User


class NotificationService:
    """Handle in-app and email notifications."""

    def send_notification(
        self, *, user: User, subject: str, message: str
    ) -> Notification:
        notification = Notification(recipient=user, subject=subject, message=message)
        db.session.add(notification)
        db.session.commit()

        if current_app.config.get("MAIL_USERNAME") and user.email:
            msg = Message(subject=subject, recipients=[user.email], body=message)
            mail.send(msg)
        return notification


notification_service = NotificationService()
