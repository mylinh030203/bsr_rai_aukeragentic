"""Development entry point: python run.py"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    no_reload = os.environ.get("BSR_NO_RELOAD") == "1"
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("BSR_PORT", "5000")),
        debug=not no_reload,
        use_reloader=not no_reload,
    )
