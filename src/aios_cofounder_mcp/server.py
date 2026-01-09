try:
    from fastmcp import FastMCP
except ModuleNotFoundError:  # pragma: no cover - fallback for test environments
    # TODO: remove shim once fastmcp is bundled in test deps.
    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, name: str) -> None:
            self.name = name

        def tool(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def resource(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def prompt(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def custom_route(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def run(self, *args, **kwargs):
            raise RuntimeError("fastmcp_not_installed")

        def run_stdio(self, *args, **kwargs):
            raise RuntimeError("fastmcp_not_installed")

# previous implementation (kept for reference)
# mcp = FastMCP("aios-cofounder-mcp")
mcp = FastMCP("aios-cofounder")

# Imports below register tools/resources on module import; keep ordering stable.
from .tools import (  # noqa: E402
    auth_tools,
    gmail_tools,
    calendar_tools,
    contacts_tools,
    web_tools,
    assistant_tools,
    approval_tools,
)
from .resources import (  # noqa: E402
    state_resources,
    gmail_resources,
    calendar_resources,
)
from .prompts import (  # noqa: E402
    inbox_triage,
    meeting_prep,
    email_followup,
    weekly_review,
)
from . import oauth_routes  # noqa: E402
