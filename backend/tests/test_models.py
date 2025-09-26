"""Basic model tests."""

from __future__ import annotations

from app import create_app
from app.extensions import db
from app.models import Role, User


def test_user_password_hashing(tmp_path):
    app = create_app("backend.config.TestingConfig")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path}/test.db"
    with app.app_context():
        db.create_all()
        role = Role(name="student")
        db.session.add(role)
        db.session.commit()

        user = User(email="user@example.com", username="user")
        user.set_password("Password123!")
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()

        assert user.check_password("Password123!")
        assert not user.check_password("WrongPassword")

        db.drop_all()
