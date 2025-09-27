"""Server-rendered pages for admin login and dashboard."""

from __future__ import annotations

from flask import Blueprint, redirect, render_template, url_for

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def admin_login() -> str:
    """Render the admin login page."""
    return render_template("admin_login.html")


@web_bp.get("/dashboard")
def admin_dashboard() -> str:
    """Render the admin dashboard shell.

    Authorization is handled client-side via JWT checks against the API.
    """
    return render_template("admin_dashboard.html")


@web_bp.get("/logout")
def logout_redirect() -> str:
    """Clear client tokens by redirecting back to the login page."""
    return redirect(url_for("web.admin_login"))
