# Job Search Campaign Agent

A personal AI-powered job search assistant built with Claude, LangChain, and MCP.

Covers the full campaign: tailored cover letters, application tracking,
technical interview coaching, and professional follow-up drafting.

---

## What it does

| Feature | Description |
|---|---|
| Cover Letter Agent | Generates tailored cover letters from JD + your profile |
| Application Tracker | SQLite-backed tracker with status, contacts, follow-up alerts |
| Interview Coach | Multi-turn technical coaching — asks, evaluates, gives ideal answers |
| Follow-up Drafter | Post-interview thank you, status checks, referral asks |
| Gmail MCP | Scans job emails, identifies pending actions (optional) |
| Calendar MCP | Adds interviews and follow-up reminders to Google Calendar (optional) |
| Streamlit UI | Single-page app tying everything together |

---

## Architecture

```
job_search_agent/
├── app.py                    # Streamlit UI
├── config_template.py        # Copy to config.py and fill in your details
├── agents/
│   ├── cover_letter_agent.py # Cover letter generation
│   ├── interview_coach.py    # Multi-turn interview coaching
│   └── followup_drafter.py   # Follow-up email drafting
├── mcp_tools/
│   ├── gmail_tool.py         # Gmail MCP integration
│   └── calendar_tool.py      # Google Calendar MCP integration
├── tracker/
│   └── tracker.py            # SQLite application tracker
└── requirements.txt
```

---

## Quickstart

```bash
# Clone and install
git clone https://github.com/yourusername/job_search_agent.git
cd job_search_agent
pip install -r requirements.txt

# Configure your profile
cp config_template.py config.py
# Edit config.py with your details — this file is in .gitignore

# Run the Streamlit app
streamlit run app.py
```

---

## Configuration

Copy `config_template.py` to `config.py` and fill in:

```python
PROFILE = {
    "name": "Your Name",
    "current_title": "Senior Data Scientist",
    "years_experience": 15,
    "achievements": [
        "Built RAG pipeline used by 400 engineers...",
    ],
    ...
}
```

`config.py` is in `.gitignore` — your personal data never gets committed.

---

## Gmail and Calendar MCP (optional)

Connect your Gmail and Google Calendar in Claude.ai settings, then:

```python
from mcp_tools.gmail_tool import GmailJobTool
from mcp_tools.calendar_tool import CalendarJobTool

gmail = GmailJobTool()
emails = gmail.find_application_emails(days=30)
actions = gmail.get_pending_actions()

cal = CalendarJobTool()
cal.add_interview("Company Name", "2026-05-19", "14:00", round_number=2)
cal.get_upcoming_interviews()
```

---

## Interview Coach Topics

The coach covers:

- Transformer architecture and attention mechanisms
- RAG system design for enterprise
- Fine-tuning and LoRA
- Bias-variance tradeoff and regularisation
- Python coding (medium difficulty)
- LLM evaluation frameworks
- Behavioural questions (STAR format)
- System design (compound AI systems)
- Knowledge graphs and MCP agents
- Recruiter pitch practice

---

## Using agents standalone

```python
# Cover letter
from agents.cover_letter_agent import CoverLetterAgent
agent = CoverLetterAgent()
letter = agent.generate(
    role="Senior AI Engineer",
    company="Acme Corp",
    jd="We are looking for...",
    tone="senior-confident",
)

# Interview coaching
from agents.interview_coach import InterviewCoach
coach = InterviewCoach()
question = coach.start_topic("rag")
evaluation = coach.chat("I would chunk documents and embed them...")

# Follow-up drafting
from agents.followup_drafter import FollowUpDrafter
drafter = FollowUpDrafter()
email = drafter.draft(
    follow_up_type="post-interview",
    company="Acme Corp",
    days_since=1,
    notes="Discussed RAG evaluation and compound AI systems",
)

# Application tracking
from tracker.tracker import ApplicationTracker
tracker = ApplicationTracker()
tracker.add(company="Acme Corp", role="Senior AI Engineer", status="interview")
tracker.print_summary()
```

---

## Adapting for your background

Everything is driven by `config.py`. The more specific your achievements and skills,
the better the cover letters and interview prep will be.

The agents are deliberately generic — they work for any senior technical role,
not just AI/ML. Adjust `TOPIC_PROMPTS` in `interview_coach.py` for your domain.

---

## Author

Built for personal use during a senior AI/ML job search.
Adapt freely for your own campaign.
