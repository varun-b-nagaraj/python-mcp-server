from __future__ import annotations

from ..server import mcp


@mcp.prompt("email_followup")
def email_followup_prompt() -> str:
    return (
        "You are drafting polite, concise follow-ups.\n"
        "Tools to use: gmail_search, gmail_get_thread, compose_email_reply, gmail_create_draft.\n"
        "Process: identify stalled threads, draft a follow-up, create a Gmail draft only.\n"
        "Output JSON schema: {\"thread_id\": \"...\", \"draft\": {\"subject\": \"...\", \"body\": \"...\"}}\n"
        "Never send email; only create drafts."
    )
