from __future__ import annotations

from .logging_conf import configure_logging
from .settings import settings
from .storage.db import init_db
from .server import mcp


def main() -> None:
    configure_logging(settings.log_level)
    init_db(settings.db_url)
    if hasattr(mcp, "run"):
        mcp.run()
    else:
        mcp.run_stdio()


if __name__ == "__main__":
    main()
