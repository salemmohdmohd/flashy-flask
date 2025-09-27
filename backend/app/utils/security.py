"""Security utilities for RBAC and password policies."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort
from flask_jwt_extended import get_jwt


def roles_required(*roles: str) -> Callable:
    """Decorator enforcing that the current user possesses all roles."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            token_roles = set(claims.get("roles", []))
            required_roles = set(roles)

            if not token_roles:
                abort(401, description="Authentication required")
            if not required_roles.issubset(token_roles):
                abort(403, description="Insufficient permissions")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def roles_accepted(*roles: str) -> Callable:
    """Decorator enforcing that the user has at least one role from the list."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            token_roles = set(claims.get("roles", []))
            accepted_roles = set(roles)

            if not token_roles:
                abort(401, description="Authentication required")
            if not token_roles.intersection(accepted_roles):
                abort(403, description="Insufficient permissions")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
