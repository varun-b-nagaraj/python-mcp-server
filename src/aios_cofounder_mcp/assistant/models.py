from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    ok: bool = Field(..., description="Whether the tool completed successfully")
    data: dict[str, Any] | None = Field(default=None, description="Tool output payload")
    error: str | None = Field(default=None, description="Machine-readable error")
    status: str | None = Field(default=None, description="Status hint for next action")
    approval_id: int | None = Field(default=None, description="Approval id if required")


class EmailSummary(BaseModel):
    message_id: str
    summary: str
    note_id: int


class MeetingBrief(BaseModel):
    event_id: str
    attendees: list[str]
    purpose: str | None = None
    recent_emails: list[dict[str, Any]] = Field(default_factory=list)
    talking_points: list[str] = Field(default_factory=list)


class DraftEmail(BaseModel):
    subject: str
    body: str
    tone: str | None = None
