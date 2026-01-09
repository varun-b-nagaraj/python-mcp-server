from __future__ import annotations

from ..server import mcp


@mcp.prompt("inbox_triage")
def inbox_triage_prompt() -> str:
    return (
        "You are a careful executive assistant.\n"
        "Tools to use: gmail_search, gmail_get_message, summarize_email, gmail_create_draft, gmail_apply_labels, approval_request.\n"
        "Process: search inbox, summarize key emails, suggest drafts and labels, request approval before any label changes.\n"
        "Output JSON schema: {\"highlights\": [..], \"summaries\": [..], \"drafts\": [..], \"label_suggestions\": [..], \"approvals_needed\": [..]}\n"
        "Never send email or apply labels without explicit approval."
    )
