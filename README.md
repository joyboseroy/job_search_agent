# Job Search Campaign Agent

A personal AI-powered job search assistant that works two ways:

- **Skill-based** — markdown skill files for Kiro, Claude Code, or any Agent Skills compatible tool. No coding needed.
- **Python/Streamlit** — full Python agents with a Streamlit UI. Works anywhere with `pip install`.

Both share a single source of truth: `steering/profile.md`.

---

## How it works

```
steering/profile.md  (fill this in once)
        │
        ├── Kiro / Claude Code
        │   └── skills/*.md read it as steering context
        │       No code. Just markdown. Agent activates automatically.
        │
        └── Python / Streamlit
            └── profile_loader.py parses it at runtime
                └── agents use it in system prompts
                    └── streamlit run app.py
```

---

## What it does

| Feature | Description |
|---|---|
| Cover Letter | Tailored cover letters from JD + your profile |
| Interview Coach | Multi-turn technical coaching — asks, evaluates, gives ideal answers |
| Follow-up Drafter | Post-interview thank you, status checks, referral asks, cold outreach |
| Application Tracker | SQLite-backed tracker with status, contacts, follow-up alerts |
| Gmail MCP | Scans job emails, identifies pending actions (optional) |
| Calendar MCP | Adds interviews and follow-up reminders to Google Calendar (optional) |

---

## Repository structure

```
job_search_agent/
├── steering/
│   └── profile.md              # Your background — shared by both approaches
├── skills/                     # Skill-based approach (Kiro / Claude Code)
│   ├── cover_letter/SKILL.md
│   ├── interview_coach/SKILL.md
│   ├── followup_drafter/SKILL.md
│   └── application_tracker/SKILL.md
├── agents/                     # Python approach
│   ├── cover_letter_agent.py
│   ├── interview_coach.py
│   └── followup_drafter.py
├── mcp_tools/                  # Optional MCP integrations
│   ├── gmail_tool.py
│   └── calendar_tool.py
├── tracker/
│   └── tracker.py              # SQLite application tracker
├── app.py                      # Streamlit UI
├── profile_loader.py           # Parses profile.md for Python agents
├── config_template.py          # Fallback if no profile.md
└── requirements.txt
```

---

## Step 1 — Fill in your profile (do this first, either way)

Edit `steering/profile.md` with your actual details:

```markdown
**Name:** Your Name
**Current title:** Senior Data Scientist at Your Company
**Experience:** 15+ years in ML/AI
**Location:** Your City, India

## Core technical skills
- RAG pipelines
- LLM orchestration (LangChain, MCP)
- Knowledge graphs

## Key achievements
- Built X system adopted by N engineers saving M minutes per cycle
- Deployed RAG pipeline for Y use case with Z% improvement

## Education
- PhD, Computer Science, University Name
```

This is your single source of truth. Edit once, works everywhere.

---

## Approach 1 — Skill-based (Kiro or Claude Code)

No Python needed. Skills activate automatically based on what you say.

### In Kiro

1. Copy `skills/` into your project's `.kiro/skills/`
2. Copy `steering/profile.md` into `.kiro/steering/`
3. Open Kiro and start talking:
   - "Help me apply to Nokia for Senior AI Engineer" — cover letter skill activates
   - "Quiz me on transformer architecture" — interview coach activates
   - "Write a follow-up to the Dell recruiter" — followup drafter activates
   - "I just applied to Acme Corp" — application tracker activates

### In Claude Code

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Use a skill directly
claude --skill skills/interview_coach
claude --skill skills/cover_letter

# Or point to the steering file for full context
claude --steering steering/profile.md
```

### In Claude.ai (no install)

Paste the contents of any `SKILL.md` into the conversation along with
your `profile.md`. The skill instructions activate immediately.

### How skills work

Each `SKILL.md` has a frontmatter description that tells the agent
when to activate. The cover letter skill activates whenever you paste
a JD or mention a company you want to apply to — without you having
to say "use the cover letter skill".

Skills follow the open [Agent Skills standard](https://kiro.dev/docs/skills/)
and are compatible with any tool that supports it.

---

## Approach 2 — Python / Streamlit

Full Python agents with a Streamlit UI. Works without any agentic IDE.

### Setup

```bash
git clone https://github.com/yourusername/job_search_agent
cd job_search_agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
# Edit steering/profile.md with your details
```

### Run the Streamlit app

```bash
streamlit run app.py
```

Opens at `localhost:8501`. Five tabs: Cover Letter, Application Tracker,
Interview Prep, Follow-up Drafter, Dashboard.

### Use agents directly in Python

```python
# Cover letter
from agents.cover_letter_agent import CoverLetterAgent
agent = CoverLetterAgent()
letter = agent.generate(
    role="Senior AI Engineer",
    company="Nokia",
    jd="We need someone with RAG and LLM experience...",
    tone="senior-confident",
)
print(letter)
```

```python
# Interview coaching
from agents.interview_coach import InterviewCoach
coach = InterviewCoach()
question = coach.start_topic("rag")
evaluation = coach.chat("I would chunk documents and embed them...")
summary = coach.get_summary()
```

```python
# Follow-up drafter
from agents.followup_drafter import FollowUpDrafter
drafter = FollowUpDrafter()
email = drafter.draft(
    follow_up_type="post-interview",
    company="Nokia",
    contact="Recruiter Name",
    days_since=1,
    notes="Discussed RAG pipeline design and telecom AI",
)
print(f"Subject: {email['subject']}")
print(email["body"])
```

```python
# Application tracker
from tracker.tracker import ApplicationTracker
tracker = ApplicationTracker()
tracker.add(company="Nokia", role="Senior AI Engineer", status="applied")
stale = tracker.get_stale(days=7)
tracker.print_summary()
```

### Daily workflow script

```python
# Run every morning to draft follow-ups for stale applications
from tracker.tracker import ApplicationTracker
from agents.followup_drafter import FollowUpDrafter

tracker = ApplicationTracker()
drafter = FollowUpDrafter()

for app in tracker.get_stale(days=7):
    email = drafter.draft(
        follow_up_type="no-response",
        company=app["company"],
        role=app.get("role", ""),
        days_since=7,
    )
    print(f"\n--- {app['company']} ---")
    print(f"Subject: {email['subject']}")
    print(email["body"])
```

---

## Optional — Gmail and Calendar MCP

Requires Gmail and Calendar MCP connected in Claude.ai settings.

```python
from mcp_tools.gmail_tool import GmailJobTool
from mcp_tools.calendar_tool import CalendarJobTool

gmail = GmailJobTool()
print(gmail.get_pending_actions())

cal = CalendarJobTool()
cal.add_interview("Nokia", "2026-05-19", "14:00", round_number=2)
```

---

## Profile — single source of truth

`steering/profile.md` drives both approaches.

`profile_loader.py` parses it for the Python agents:

```python
from profile_loader import parse_profile_md, get_profile_context

profile = parse_profile_md()    # dict: name, skills, achievements etc
context = get_profile_context() # formatted string for LLM system prompts
```

Falls back to `config.py` then `config_template.py` if `profile.md` not found.

---

## Choosing your approach

| | Skill-based | Python/Streamlit |
|---|---|---|
| Setup | Copy .md files | pip install + API key |
| Requires | Kiro, Claude Code, or compatible IDE | Python 3.10+ |
| UI | Natural language in IDE | Streamlit web app |
| MCP integration | Native | Via mcp_tools/ |
| Portable | Any Agent Skills compatible tool | Anywhere with Python |
| Best for | Daily use inside an IDE | Standalone tool |

Most users will want both — skills for daily use in their IDE,
Python fallback for when no IDE is available.

---

## Privacy

`config.py` is in `.gitignore` and will never be committed.

`steering/profile.md` is in the repo as a template with placeholder
values. If you want to keep your filled-in profile private, add this
to `.gitignore`:

```
steering/profile.md
```

Then keep your real copy locally only.
