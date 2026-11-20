"""Release entry point: python run_prod.py

Serves the app with waitress (a real WSGI server, no debug mode, no reloader)
on BSR_HOST:BSR_PORT, defaulting to all interfaces so a container or reverse
proxy can reach it. A production process with a placeholder secret fails here,
because `create_app` validates the configuration.
"""

from __future__ import annotations

import os

from waitress import serve

from wsgi import application

if __name__ == "__main__":
    serve(
        application,
        host=os.environ.get("BSR_HOST", "0.0.0.0"),
        port=int(os.environ.get("BSR_PORT", os.environ.get("PORT", "8000"))),
        threads=int(os.environ.get("BSR_THREADS", "4")),
        ident=None,
        # Peer-supplied X-Forwarded-* headers are dropped, so the login rate
        # limit keys on the real socket address. Internal errors are not echoed
        # to clients.
        expose_tracebacks=False,
        clear_untrusted_proxy_headers=True,
    )
