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
- By default the server uses SQLite at `./aios_cofounder_mcp.db`.
- Tools that modify external systems require approval before execution.
