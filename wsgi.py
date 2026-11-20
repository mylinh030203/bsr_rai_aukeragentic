"""WSGI entry point for a deployed process.

`waitress-serve --call wsgi:application` (or gunicorn on Linux) imports this
module. Production validation lives in `create_app`, so this file only has to
expose the application.
"""

from __future__ import annotations

from app import create_app

application = create_app()

app = application
