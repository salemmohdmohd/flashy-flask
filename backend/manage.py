"""Management script for CLI operations."""

from __future__ import annotations

from app import create_app
from flask.cli import FlaskGroup

app = create_app()
cli = FlaskGroup(create_app=create_app)


if __name__ == "__main__":
    cli()
