from __future__ import annotations

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse
from starlette.routing import Route

from .server import mcp
from .settings import settings
from .storage.repo import Repository
from .google import oauth as oauth_flow


_repo = Repository(settings.db_url)
# module-level repo avoids reconnect per callback
# TODO: consolidate OAuth error templates across providers.


@mcp.custom_route("/oauth/google/callback", methods=["GET"], include_in_schema=False)
async def google_oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code or not state:
        return PlainTextResponse("Missing code or state", status_code=400)
    result = oauth_flow.handle_oauth_callback(settings, _repo, code, state)
    if not result.get("ok"):
        return HTMLResponse(
            "<html><body><h3>Authorization failed.</h3>"
            "<p>You can close this tab and try again.</p></body></html>",
            status_code=400,
        )
    # previous implementation (kept for reference)
    # return PlainTextResponse("Authorization complete. You can close this tab.", status_code=200)
    return HTMLResponse(
        "<html><body><h3>Authorization complete.</h3>"
        "<p>You can close this tab and return to the app.</p></body></html>"
    )


def build_oauth_callback_app() -> Starlette:
    return Starlette(
        routes=[
            Route(
                "/oauth/google/callback",
                endpoint=google_oauth_callback,
                methods=["GET"],
            )
        ]
    )
