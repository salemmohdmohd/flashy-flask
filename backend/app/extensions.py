"""Centralized Flask extension initialization."""

from __future__ import annotations

from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
jwt = JWTManager()
bcrypt = Bcrypt()
limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)
ma = Marshmallow()
admin = Admin(name="Flashy Admin", template_mode="bootstrap4")

__all__ = ["db", "migrate", "mail", "jwt", "bcrypt", "limiter", "ma", "admin"]
