from __future__ import annotations

from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse

from .server import mcp
from .settings import settings
from .storage.repo import Repository
from .google import oauth as oauth_flow


_repo = Repository(settings.db_url)


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
    return HTMLResponse(
        "<html><body><h3>Authorization complete.</h3>"
        "<p>You can close this tab and return to the app.</p></body></html>"
    )
