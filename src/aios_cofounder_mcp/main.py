from __future__ import annotations

import threading
from urllib.parse import urlparse

import uvicorn

from .logging_conf import configure_logging
from .settings import settings
from .storage.db import init_db
from .server import mcp
from .oauth_routes import build_oauth_callback_app


def _start_oauth_callback_server() -> None:
    if not settings.oauth_redirect_base_url:
        return
    parsed = urlparse(settings.oauth_redirect_base_url)
    # bind to all interfaces to support local tunnels
    host = "0.0.0.0"
    port = parsed.port or 8765
    app = build_oauth_callback_app()
    config = uvicorn.Config(app, host=host, port=port, log_level=settings.log_level.lower())
    server = uvicorn.Server(config)
    # previous implementation (kept for reference)
    # uvicorn.run(app, host=host, port=port, log_level=settings.log_level.lower())
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()


def main() -> None:
    configure_logging(settings.log_level)
    init_db(settings.db_url)
    # intentionally started in a background thread to avoid blocking stdio transport
    _start_oauth_callback_server()
    if hasattr(mcp, "run"):
        # legacy fastmcp versions exposed run() only
        mcp.run()
    else:
        mcp.run_stdio()


if __name__ == "__main__":
    main()
