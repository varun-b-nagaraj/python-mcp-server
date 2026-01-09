from __future__ import annotations

import logging
from typing import Any

from ..assistant.models import ToolResponse

_logger = logging.getLogger("aios_cofounder_mcp.tools")
_SENSITIVE_KEYS = {"code", "access_token", "refresh_token", "id_token", "authorization", "token"}
# previous implementation (kept for reference)
# _SENSITIVE_KEYS = {"token", "authorization"}


def _redact_value(value: Any, *, max_len: int = 200, depth: int = 0) -> Any:
    # TODO: tune max depth once payloads grow.
    if depth > 2:
        return "<truncated>"
    if isinstance(value, str):
        if len(value) > max_len:
            return f"<{len(value)} chars>"
        return value
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, val in value.items():
            if key.lower() in _SENSITIVE_KEYS:
                redacted[key] = "<redacted>"
            else:
                redacted[key] = _redact_value(val, max_len=max_len, depth=depth + 1)
        return redacted
    if isinstance(value, list):
        return [_redact_value(item, max_len=max_len, depth=depth + 1) for item in value]
    return value


def log_tool_call(tool_name: str, payload: dict[str, Any]) -> None:
    # wrapper exists to keep audit logs consistent across tools
    _logger.info("tool_call %s payload=%s", tool_name, _redact_value(payload))


def response_ok(data: dict[str, Any]) -> dict[str, Any]:
    return ToolResponse(ok=True, data=data).model_dump()


def response_error(
    error: str,
    status: str | None = None,
    approval_id: int | None = None,
) -> dict[str, Any]:
    return ToolResponse(ok=False, error=error, status=status, approval_id=approval_id).model_dump()
