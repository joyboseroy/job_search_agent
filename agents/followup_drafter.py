"""
agents/followup_drafter.py

Follow-up email drafting agent.
Generates professional follow-up messages for various job search scenarios.

Usage:
    from agents.followup_drafter import FollowUpDrafter
    drafter = FollowUpDrafter()
    
    email = drafter.draft(
        follow_up_type="post-interview",
        company="Acme Corp",
        contact="Alex Johnson",
        days_since=1,
        notes="Discussed compound AI systems and RAG evaluation"
    )
    print(email)
"""

import anthropic
from typing import Optional
from dataclasses import dataclass

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from profile_loader import parse_profile_md, build_profile_context

try:
    import config
    LLM_MODEL = config.LLM_MODEL
    LLM_MAX_TOKENS = config.LLM_MAX_TOKENS
except ImportError:
    LLM_MODEL = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS = 1000

PROFILE = parse_profile_md()


FOLLOW_UP_TYPES = {
    "post-interview": {
        "description": "Thank you email after an interview",
        "tone": "warm and professional",
        "length": "100-150 words",
        "guidance": "Reference something specific from the conversation. Express genuine interest without desperation.",
    },
    "no-response": {
        "description": "Chase after no response to application",
        "tone": "polite and confident",
        "length": "80-100 words",
        "guidance": "One gentle nudge. Not apologetic. Assume they are busy, not uninterested.",
    },
    "status-check": {
        "description": "Friendly status update request",
        "tone": "casual and professional",
        "length": "60-80 words",
        "guidance": "Keep it short. Make it easy for them to reply with one sentence.",
    },
    "withdraw": {
        "description": "Politely withdraw from the process",
        "tone": "gracious and brief",
        "length": "60-80 words",
        "guidance": "Leave the door open for future opportunities. No explanation needed.",
    },
    "referral-ask": {
        "description": "Ask a contact for a referral or introduction",
        "tone": "warm and direct",
        "length": "100-120 words",
        "guidance": "Make it easy to say yes or no. Be specific about what you are asking for.",
    },
    "networking": {
        "description": "Cold outreach to someone at a target company",
        "tone": "warm, respectful, brief",
        "length": "80-100 words",
        "guidance": "Lead with a genuine connection or reason for reaching out. Ask for a 15-minute conversation, not a job.",
    },
}


@dataclass
class FollowUpRequest:
    follow_up_type: str
    company: str
    contact: str = ""
    days_since: int = 0
    role: str = ""
    notes: str = ""
    interview_date: str = ""


class FollowUpDrafter:
    """
    Agent that drafts professional follow-up emails for job search.

    Persona: a calm, strategic career advisor who writes emails
    that are warm without being desperate, direct without being rude.
    """

    def __init__(self, profile: Optional[dict] = None):
        self.client = anthropic.Anthropic()
        self.profile = profile or PROFILE

        self.system = f"""You draft professional follow-up emails for a senior AI professional's job search.

SENDER:
Name: {self.profile.get('name', 'The candidate')}
Role: {self.profile.get('current_title')} at {self.profile.get('current_company')}

WRITING RULES:
- Never sound desperate or over-apologetic
- Be specific where possible — reference real context given
- No em dashes
- No generic openers like "I hope this email finds you well"
- End with a clear, low-pressure close
- Provide subject line for emails
- Keep within the specified word count
- Leave the door open for future contact in all messages"""

    def draft(
        self,
        follow_up_type: str,
        company: str,
        contact: str = "",
        days_since: int = 0,
        role: str = "",
        notes: str = "",
        interview_date: str = "",
    ) -> dict:
        """
        Draft a follow-up email.

        Args:
            follow_up_type: One of the keys in FOLLOW_UP_TYPES
            company: Company name
            contact: Contact person name and title
            days_since: Days since last contact
            role: Role applied for
            notes: Context from interview or interaction
            interview_date: Date of interview (for post-interview)

        Returns:
            Dict with keys: subject, body, type
        """
        if follow_up_type not in FOLLOW_UP_TYPES:
            raise ValueError(f"Unknown type. Choose from: {list(FOLLOW_UP_TYPES.keys())}")

        ft = FOLLOW_UP_TYPES[follow_up_type]

        context_parts = []
        if company:
            context_parts.append(f"Company: {company}")
        if role:
            context_parts.append(f"Role: {role}")
        if contact:
            context_parts.append(f"Contact: {contact}")
        if days_since:
            context_parts.append(f"Days since last contact: {days_since}")
        if interview_date:
            context_parts.append(f"Interview date: {interview_date}")
        if notes:
            context_parts.append(f"Context/notes: {notes}")

        prompt = f"""Draft {ft['description']}.

Context:
{chr(10).join(context_parts)}

Requirements:
- Tone: {ft['tone']}
- Length: {ft['length']}
- Guidance: {ft['guidance']}

Return in this exact format:
SUBJECT: <subject line>
BODY:
<email body>"""

        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            system=self.system,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text
        subject = ""
        body = raw

        if "SUBJECT:" in raw and "BODY:" in raw:
            lines = raw.split("\n")
            subject_line = next((l for l in lines if l.startswith("SUBJECT:")), "")
            subject = subject_line.replace("SUBJECT:", "").strip()
            body_start = raw.find("BODY:") + 5
            body = raw[body_start:].strip()

        return {
            "type": follow_up_type,
            "subject": subject,
            "body": body,
            "company": company,
            "contact": contact,
        }

    def draft_all_variants(
        self, company: str, role: str = "", notes: str = ""
    ) -> dict:
        """Draft all follow-up types for a given company — useful to have ready."""
        results = {}
        for ft in FOLLOW_UP_TYPES:
            try:
                results[ft] = self.draft(ft, company, role=role, notes=notes)
            except Exception as e:
                results[ft] = {"error": str(e)}
        return results


if __name__ == "__main__":
    drafter = FollowUpDrafter()

    email = drafter.draft(
        follow_up_type="post-interview",
        company="Acme Corp",
        contact="Alex Johnson, Talent Acquisition (example)",
        days_since=1,
        role="Senior AI Engineer",
        notes="Discussed compound AI systems, RAG evaluation frameworks, and customer-facing delivery",
        interview_date="12 May 2026",
    )

    print(f"Subject: {email['subject']}")
    print()
    print(email["body"])
