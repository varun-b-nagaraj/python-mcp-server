# aios-cofounder-mcp

Production-ready MCP server for a Business Co-Founder / Executive Assistant.

## Features
- FastMCP server over STDIO by default
- Lightweight SQLite storage for assistant state
- Google OAuth + Gmail, Calendar, Contacts tools
- Web search + fetch helpers
- Approval gating for sensitive actions

## Setup
1. Create a virtual environment and install dependencies:

```bash
uv sync
```

2. Configure environment variables:

```bash
cp .env.example .env
```

3. Run the MCP server (STDIO transport):

```bash
uv run aios-cofounder-mcp
```

## Notes
- Google OAuth requires valid `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
- Set `OAUTH_REDIRECT_BASE_URL` to the public base URL for this server (e.g., an ngrok/cloudflared URL).
- Set `GOOGLE_OAUTH_SCOPES` to a space- or comma-separated list of scopes.
- The OAuth callback is served at `/oauth/google/callback` by this MCP server.
- For local dev, start a tunnel to port `8765` (default callback bind port) and set `OAUTH_REDIRECT_BASE_URL=https://<public-domain>`.
- By default the server uses SQLite at `./aios_cofounder_mcp.db`.
- Tools that modify external systems require approval before execution.

## Known limitations
- Free/busy uses the primary calendar only.
- OAuth callback listener is always started when `OAUTH_REDIRECT_BASE_URL` is set.

## TODO
- Consolidate OAuth error mapping for client display.
- Add pagination for repository list endpoints.

## Ops notes
- SQLite file and parent directory are created on first run.
- Keep `OAUTH_STATE_TTL_SECONDS` short in shared environments.
