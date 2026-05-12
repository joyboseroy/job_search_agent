---
name: application-tracker
description: Track and manage job applications during a search campaign. Use this skill whenever the user wants to add an application, update a status, check what needs follow-up, see their pipeline, ask "what have I applied to", "which companies haven't replied", "what's my interview pipeline", "how many applications do I have", or says they just applied somewhere or heard back from a company. Also activate when the user asks for a daily or weekly job search summary.
---

# Application Tracker Skill

Manages the job search pipeline — applications, statuses, follow-up dates,
and contacts. Works with a simple markdown table or the SQLite tracker
in tracker/tracker.py depending on what is available.

---

## Data model

Each application has:
- **Company** — name
- **Role** — job title
- **Status** — one of: applied / screening / interview / offer / rejected / withdrawn / no_response
- **Applied date** — when submitted
- **Last contact** — most recent interaction date
- **Contact** — recruiter or hiring manager name
- **Notes** — anything relevant
- **Next action** — what needs to happen next

---

## Status definitions

| Status | Meaning |
|---|---|
| applied | Submitted, no response yet |
| screening | Recruiter call done or scheduled |
| interview | Technical or panel round in progress |
| offer | Offer received |
| rejected | Explicitly rejected |
| withdrawn | Candidate withdrew |
| no_response | Applied 14+ days ago, no reply |

---

## Commands the user might give

### Add application
"I just applied to Nokia for Senior AI Engineer"
→ Add entry with status=applied, today's date

### Update status
"Dell moved me to round 2" / "I got rejected by Acme"
→ Update status, update last_contact date

### Check pipeline
"What's my current pipeline?" / "Show me all active applications"
→ List all non-rejected, non-withdrawn applications with status

### Find stale applications
"What needs follow-up?" / "Who hasn't replied in 2 weeks?"
→ List applications where last_contact > 14 days ago and status not in (offer, rejected, withdrawn)

### Daily summary
"Give me my job search summary"
→ Stats: total applications, by status, stale count, next actions

---

## If using the Python tracker

The tracker lives at `tracker/tracker.py`. Run operations as:

```python
from tracker.tracker import ApplicationTracker
tracker = ApplicationTracker()

# Add
tracker.add(company="Nokia", role="Senior AI Engineer", status="applied")

# Update
tracker.update_status(app_id=1, status="interview", notes="Round 1 done")

# Stale
stale = tracker.get_stale(days=14)

# Summary
tracker.print_summary()
```

---

## If no database available

Maintain the tracker as a markdown table in the conversation:

```
| Company | Role | Status | Applied | Last Contact | Notes |
|---|---|---|---|---|---|
| Nokia | Senior AI Engineer | applied | 12 May | 12 May | Applied via LinkedIn |
| Acme Corp | AI Architect | interview | 8 May | 11 May | Round 2 scheduled |
```

Update the table as the user gives new information.

---

## Follow-up alerts

When showing the pipeline, always flag applications where:
- Status is `applied` or `no_response` and last contact > 7 days
- Status is `screening` and last contact > 5 days
- Status is `interview` and last contact > 3 days

Flag these with: "⚠ Follow-up needed"

Offer to draft the follow-up using the followup-drafter skill.

---

## Daily target reminders

When giving a summary, include:
- Applications sent today vs daily target (default: 5)
- Network messages sent today vs daily target (default: 3)
- Any interviews in the next 7 days

Keep the summary concise — bullet points, under 150 words.
