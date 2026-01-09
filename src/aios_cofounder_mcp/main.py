from __future__ import annotations

import threading
from urllib.parse import urlparse

import uvicorn

from .logging_conf import configure_logging
from .settings import settings
from .storage.db import init_db
from .server import mcp


def _start_oauth_callback_server() -> None:
    if not settings.oauth_redirect_base_url:
        return
    parsed = urlparse(settings.oauth_redirect_base_url)
    host = "0.0.0.0"
    port = parsed.port or 8765
    app = mcp.http_app(path="/mcp")
    config = uvicorn.Config(app, host=host, port=port, log_level=settings.log_level.lower())
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()


def main() -> None:
    configure_logging(settings.log_level)
    init_db(settings.db_url)
    _start_oauth_callback_server()
    if hasattr(mcp, "run"):
        mcp.run()
    else:
        mcp.run_stdio()


if __name__ == "__main__":
    main()
