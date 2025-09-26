"""Authentication-related schemas."""
from __future__ import annotations

from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """Schema for user registration."""

    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    first_name = fields.Str(validate=validate.Length(max=120))
    last_name = fields.Str(validate=validate.Length(max=120))
    role = fields.Str(validate=validate.OneOf(["student", "teacher", "expert", "admin"]))


class LoginSchema(Schema):
    """Schema for user login."""

    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
