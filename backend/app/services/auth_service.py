"""Authentication and authorization services."""

from __future__ import annotations

from typing import Optional

import requests
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from ..extensions import db
from ..models import Profile, Role, User


class AuthServiceError(Exception):
    """Raised when an auth-related operation fails."""


class AuthService:
    """Service encapsulating authentication logic."""

    def register_user(
        self,
        *,
        email: str,
        username: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        role_name: str | None = None,
    ) -> User:
        """Register a new user and assign default roles."""
        if User.query.filter_by(email=email).first():
            raise AuthServiceError("Email already registered")
        if User.query.filter_by(username=username).first():
            raise AuthServiceError("Username already taken")

        user = User(email=email, username=username)
        user.set_password(password)

        profile = Profile(first_name=first_name, last_name=last_name)
        user.profile = profile

        roles = self._resolve_roles(role_name)
        user.roles.extend(roles)

        db.session.add(user)
        db.session.commit()

        return user

    def authenticate(self, *, email: str, password: str) -> tuple[str, str, User]:
        """Authenticate user credentials and issue JWT tokens."""
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise AuthServiceError("Invalid credentials")
        if not user.is_active:
            raise AuthServiceError("Account disabled")

        access_token = create_access_token(
            identity=user.id,
            additional_claims={"roles": [role.name for role in user.roles]},
        )
        refresh_token = create_refresh_token(identity=user.id)
        return access_token, refresh_token, user

    def google_oauth_login(self, *, code: str) -> tuple[str, str, User]:
        """Authenticate a user using Google OAuth authorization code."""
        token_endpoint = "https://oauth2.googleapis.com/token"
        config = current_app.config

        client_id = config.get("GOOGLE_OAUTH_CLIENT_ID")
        client_secret = config.get("GOOGLE_OAUTH_CLIENT_SECRET")
        redirect_uri = config.get("GOOGLE_OAUTH_REDIRECT_URI")
        if not all([client_id, client_secret, redirect_uri]):
            raise AuthServiceError("Google OAuth configuration missing")

        payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(token_endpoint, data=payload, timeout=10)
        if response.status_code != 200:
            raise AuthServiceError("Failed to exchange authorization code")
        token_data = response.json()

        userinfo_resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
            timeout=10,
        )
        if userinfo_resp.status_code != 200:
            raise AuthServiceError("Failed to fetch user info")
        userinfo = userinfo_resp.json()

        email = userinfo.get("email")
        if not email:
            raise AuthServiceError("Email not found in Google profile")

        user = User.query.filter_by(email=email).first()
        if not user:
            username = userinfo.get("given_name") or email.split("@")[0]
            user = User(email=email, username=username)
            user.password_hash = "oauth"
            profile = Profile(
                first_name=userinfo.get("given_name"),
                last_name=userinfo.get("family_name"),
            )
            user.profile = profile
            user.roles.extend(self._resolve_roles("student"))
            db.session.add(user)
            db.session.commit()

        access_token = create_access_token(
            identity=user.id,
            additional_claims={"roles": [role.name for role in user.roles]},
        )
        refresh_token = create_refresh_token(identity=user.id)
        return access_token, refresh_token, user

    def _resolve_roles(self, requested_role: Optional[str]) -> list[Role]:
        """Resolve roles ensuring at least the student role exists."""
        default_role = Role.query.filter_by(name="student").first()
        roles: list[Role] = []
        if default_role:
            roles.append(default_role)
        if requested_role and requested_role != "student":
            role = Role.query.filter_by(name=requested_role).first()
            if not role:
                raise AuthServiceError("Requested role is invalid")
            roles.append(role)
        return roles


auth_service = AuthService()
