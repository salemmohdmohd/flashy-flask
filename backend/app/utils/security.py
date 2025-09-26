"""Security utilities for RBAC and password policies."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort
from flask_jwt_extended import current_user


def roles_required(*roles: str) -> Callable:
    """Decorator enforcing that the current user possesses all roles."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user:
                abort(401, description="Authentication required")
            missing = [role for role in roles if not current_user.has_role(role)]
            if missing:
                abort(403, description="Insufficient permissions")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def roles_accepted(*roles: str) -> Callable:
    """Decorator enforcing that the user has at least one role from the list."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user:
                abort(401, description="Authentication required")
            if not any(current_user.has_role(role) for role in roles):
                abort(403, description="Insufficient permissions")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
