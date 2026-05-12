"""
mcp_tools/calendar_tool.py

Google Calendar MCP integration for the job search agent.
Tracks interviews, follow-up reminders, and application deadlines.

Requires Google Calendar MCP to be connected in Claude.ai.
MCP URL: https://calendarmcp.googleapis.com/mcp/v1

Usage:
    from mcp_tools.calendar_tool import CalendarJobTool
    
    cal = CalendarJobTool()
    
    # Add interview to calendar
    cal.add_interview(
        company="Acme Corp",
        date="2026-06-01",
        time="15:00",
        duration_minutes=45,
        notes="Advisory Consultant DS — virtual Teams"
    )
    
    # Get upcoming interviews
    interviews = cal.get_upcoming_interviews()
"""

import anthropic
from datetime import datetime, timedelta
from typing import Optional

try:
    import config
    CALENDAR_MCP_URL = config.CALENDAR_MCP_URL
    LLM_MODEL = config.LLM_MODEL
    LLM_MAX_TOKENS = config.LLM_MAX_TOKENS
    PROFILE = config.PROFILE
except ImportError:
    CALENDAR_MCP_URL = "https://calendarmcp.googleapis.com/mcp/v1"
    LLM_MODEL = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS = 1000
    PROFILE = {"name": "The candidate"}


class CalendarJobTool:
    """
    Google Calendar integration for interview and follow-up scheduling.
    Uses the Google Calendar MCP server connected in Claude.ai.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.mcp_server = {
            "type": "url",
            "url": CALENDAR_MCP_URL,
            "name": "google-calendar-mcp"
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

        text_blocks = [
            block.text for block in response.content
            if hasattr(block, "text")
        ]
        return "\n".join(text_blocks)

    def add_interview(
        self,
        company: str,
        date: str,
        time: str,
        duration_minutes: int = 60,
        round_number: int = 1,
        interview_type: str = "virtual",
        meeting_link: str = "",
        interviewer: str = "",
        notes: str = "",
        add_prep_reminder: bool = True,
    ) -> str:
        """
        Add an interview to Google Calendar.

        Args:
            company: Company name
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format (24hr, IST)
            duration_minutes: Interview duration
            round_number: Interview round number
            interview_type: virtual, phone, in-person
            meeting_link: Teams/Zoom/Meet link
            interviewer: Interviewer name
            notes: Additional notes
            add_prep_reminder: Add a 2-hour prep reminder before

        Returns:
            Confirmation from Calendar
        """
        title = f"Interview — {company} (Round {round_number})"
        description_parts = [
            f"Company: {company}",
            f"Round: {round_number}",
            f"Type: {interview_type}",
        ]
        if interviewer:
            description_parts.append(f"Interviewer: {interviewer}")
        if meeting_link:
            description_parts.append(f"Link: {meeting_link}")
        if notes:
            description_parts.append(f"Notes: {notes}")

        description = "\n".join(description_parts)

        prompt = f"""Add an interview event to my Google Calendar:

Title: {title}
Date: {date}
Time: {time} IST
Duration: {duration_minutes} minutes
Description: {description}

{'Also add a reminder 2 hours before titled: "Prep: ' + company + ' interview"' if add_prep_reminder else ''}

Confirm when added."""

        return self._call_with_mcp(prompt)

    def add_followup_reminder(
        self,
        company: str,
        reminder_date: str,
        notes: str = "",
    ) -> str:
        """
        Add a follow-up reminder to calendar.

        Args:
            company: Company name
            reminder_date: Date in YYYY-MM-DD format
            notes: What to follow up on

        Returns:
            Confirmation from Calendar
        """
        prompt = f"""Add a reminder to my Google Calendar:

Title: Follow up — {company}
Date: {reminder_date}
Time: 10:00 IST
Duration: 15 minutes
Description: {notes or f'Follow up on job application at {company}'}

Add a notification 30 minutes before.
Confirm when added."""

        return self._call_with_mcp(prompt)

    def get_upcoming_interviews(self, days: int = 14) -> str:
        """
        Get all upcoming interview events from calendar.

        Args:
            days: How many days ahead to look

        Returns:
            List of upcoming interviews
        """
        until_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        prompt = f"""Search my Google Calendar for events from today until {until_date} that are interviews or job-related meetings.

List each one with:
- Title
- Date and time
- Duration
- Any notes or description

Also list any follow-up reminders I have set."""

        return self._call_with_mcp(prompt)

    def add_application_deadline(
        self,
        company: str,
        deadline_date: str,
        role: str = "",
    ) -> str:
        """Add an application deadline reminder."""
        prompt = f"""Add a deadline reminder to my Google Calendar:

Title: Application deadline — {company}{f' ({role})' if role else ''}
Date: {deadline_date}
Time: 09:00 IST
Duration: 30 minutes
Description: Submit job application to {company} by end of day.

Add notification 2 days before and 1 day before.
Confirm when added."""

        return self._call_with_mcp(prompt)

    def get_job_search_schedule(self) -> str:
        """
        Get a summary of all job search events in the next 30 days.

        Returns:
            Formatted schedule summary
        """
        until_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        prompt = f"""Look at my Google Calendar from today to {until_date}.

Find all events related to:
- Job interviews
- Application deadlines
- Recruiter calls
- Follow-up reminders
- Career-related events

Organise them by date and provide a clean summary of my job search schedule."""

        return self._call_with_mcp(
            prompt,
            system="You are helping manage a senior data scientist's job search calendar. Be organised and concise."
        )


if __name__ == "__main__":
    print("Calendar Job Tool — requires Google Calendar MCP to be connected in Claude.ai")
    print("MCP URL:", CALENDAR_MCP_URL)
    print()
    print("Example usage:")
    print("  cal = CalendarJobTool()")
    print("  cal.add_interview('Acme Corp', '2026-06-15', '14:00', round_number=2)")
    print("  cal.get_upcoming_interviews()")
