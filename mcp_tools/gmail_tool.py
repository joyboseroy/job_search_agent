"""
mcp_tools/gmail_tool.py

Gmail MCP integration for the job search agent.
Reads application-related emails and can send follow-ups.

Requires Gmail MCP to be connected in Claude.ai.
MCP URL: https://gmailmcp.googleapis.com/mcp/v1

Usage:
    from mcp_tools.gmail_tool import GmailJobTool
    
    gmail = GmailJobTool()
    
    # Find application-related emails
    emails = gmail.find_application_emails(days=30)
    
    # Send a follow-up
    gmail.send_followup(
        to="recruiter@company.com",
        subject="Re: Senior AI Engineer role",
        body="Thank you for the interview..."
    )
"""

import anthropic
from datetime import datetime, timedelta
from typing import Optional

try:
    import config
    GMAIL_MCP_URL = config.GMAIL_MCP_URL
    LLM_MODEL = config.LLM_MODEL
    LLM_MAX_TOKENS = config.LLM_MAX_TOKENS
except ImportError:
    GMAIL_MCP_URL = "https://gmailmcp.googleapis.com/mcp/v1"
    LLM_MODEL = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS = 1000

# Keywords to identify job-related emails
JOB_EMAIL_KEYWORDS = [
    "interview", "application", "recruitment", "hiring",
    "recruiter", "talent", "HR", "offer", "shortlisted",
    "assessment", "opportunity", "position", "role",
    "data scientist", "AI engineer", "machine learning",
]


class GmailJobTool:
    """
    Gmail integration for job search email management.
    Uses the Gmail MCP server connected in Claude.ai.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.mcp_server = {
            "type": "url",
            "url": GMAIL_MCP_URL,
            "name": "gmail-mcp"
        }

    def _call_with_mcp(self, prompt: str, system: str = "") -> str:
        """Make an MCP-powered API call."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": LLM_MODEL,
            "max_tokens": LLM_MAX_TOKENS,
            "messages": messages,
            "mcp_servers": [self.mcp_server],
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)

        # Extract text from response
        text_blocks = [
            block.text for block in response.content
            if hasattr(block, "text")
        ]
        return "\n".join(text_blocks)

    def find_application_emails(
        self,
        days: int = 30,
        company: Optional[str] = None
    ) -> str:
        """
        Search Gmail for job application related emails.

        Args:
            days: How many days back to search
            company: Optional company name to filter by

        Returns:
            Summary of relevant emails found
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")

        company_filter = f" from or about {company}" if company else ""
        keywords_str = " OR ".join(JOB_EMAIL_KEYWORDS[:8])

        prompt = f"""Search my Gmail for job application related emails{company_filter}.

Search for emails from the last {days} days (since {since_date}) containing keywords like:
{keywords_str}

For each relevant email found, summarise:
- From / sender
- Subject
- Date
- Key content (1-2 sentences)
- Any action needed

List the 10 most recent relevant emails."""

        return self._call_with_mcp(
            prompt,
            system="You are helping manage a job search. Focus only on emails related to job applications, interviews, and recruitment."
        )

    def get_application_status_from_email(
        self, company: str, role: str = ""
    ) -> str:
        """
        Check email for latest status on a specific application.

        Args:
            company: Company name
            role: Optional role title

        Returns:
            Summary of email thread status
        """
        prompt = f"""Search my Gmail for all emails related to my job application at {company}{f' for the {role} role' if role else ''}.

Find:
1. The most recent email in this thread
2. Who sent it and when
3. What the current status appears to be
4. Whether a reply or action is needed from me

Summarise in 3-5 sentences."""

        return self._call_with_mcp(prompt)

    def draft_and_send_followup(
        self,
        to: str,
        subject: str,
        body: str,
        send: bool = False
    ) -> str:
        """
        Draft a follow-up email via Gmail MCP.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            send: If True, actually send. If False, just draft.

        Returns:
            Confirmation message
        """
        action = "send" if send else "draft (do not send yet)"

        prompt = f"""Please {action} an email with these details:

To: {to}
Subject: {subject}

Body:
{body}

{'Send the email now.' if send else 'Save as draft only. Do not send.'}"""

        return self._call_with_mcp(prompt)

    def get_pending_actions(self) -> str:
        """
        Scan recent job emails and identify what actions are needed.

        Returns:
            List of pending actions from email
        """
        prompt = """Search my Gmail for job application emails from the last 30 days.

Identify emails where:
1. A recruiter is waiting for my response
2. I need to schedule something
3. I received a rejection (to update my tracker)
4. I received good news (interview invitation, offer, etc.)
5. I should follow up because it has been more than 7 days

List each action needed, the company, and the urgency."""

        return self._call_with_mcp(
            prompt,
            system="You are a job search assistant. Identify pending actions from emails clearly and concisely."
        )


if __name__ == "__main__":
    print("Gmail Job Tool — requires Gmail MCP to be connected in Claude.ai")
    print("MCP URL:", GMAIL_MCP_URL)
    print()
    print("Example usage:")
    print("  gmail = GmailJobTool()")
    print("  emails = gmail.find_application_emails(days=30)")
    print("  actions = gmail.get_pending_actions()")
