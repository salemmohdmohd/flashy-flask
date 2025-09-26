"""Database seed command."""

from __future__ import annotations

import click
from flask.cli import with_appcontext

from ..extensions import db
from ..models import Role, User


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    """Seed base roles and admin user."""
    roles = ["student", "teacher", "expert", "admin", "marketing"]
    for name in roles:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name, description=f"{name.title()} role"))
    db.session.commit()

    from flask import current_app

    admin_email = current_app.config["ADMIN_EMAIL"]
    user = User.query.filter_by(email=admin_email).first()
    if not user:
        user = User(email=admin_email, username=current_app.config["ADMIN_USERNAME"])
        user.set_password(current_app.config["ADMIN_PASSWORD"])
        admin_role = Role.query.filter_by(name="admin").first()
        if admin_role:
            user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()
    click.echo("✅ Seed data applied")
