"""
config_template.py

Copy this file to config.py and fill in your own details.
config.py is in .gitignore — never commit personal data.

This is the ONLY file you need to edit to personalise the agent.
"""

# ── Your Profile ──────────────────────────────────────────────────────────────
# This becomes the system prompt context for all agents.
# Be specific — the more concrete your achievements, the better the output.

PROFILE = {
    "name": "Your Name",
    "current_title": "Senior Data Scientist",
    "years_experience": 15,
    "current_company": "Your Company",
    "location": "Your City, Country",

    # Core technical skills — be specific
    "core_skills": [
        "RAG pipelines",
        "LLM orchestration (LangChain, LlamaIndex)",
        "Knowledge graphs",
        "Agentic AI (MCP)",
        "Python",
        "Azure ML / AWS SageMaker",
    ],

    # Key achievements with metrics — used in cover letters
    "achievements": [
        "Built X system used by N engineers saving M minutes per cycle",
        "Deployed RAG pipeline for Y use case",
        "Filed Z patents across companies A, B, C",
    ],

    # Education
    "education": [
        "PhD, Computer Science, University Name (thesis topic)",
        "MSc, Field, University Name",
    ],

    # Previous companies — used to signal credibility
    "companies": ["Company A", "Company B", "Company C"],

    # Target roles
    "target_roles": [
        "Senior Applied AI Engineer",
        "AI Architect",
        "Director of Data Science",
    ],

    # Target locations
    "target_locations": ["Your City", "Remote", "Hybrid"],
}

# ── LLM Settings ──────────────────────────────────────────────────────────────
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_MAX_TOKENS = 1000
LLM_TEMPERATURE = 0.7

# ── Tracker Settings ──────────────────────────────────────────────────────────
TRACKER_DB_PATH = "tracker/applications.db"

# ── Gmail MCP Settings ───────────────────────────────────────────────────────
# Only needed if you want Gmail integration
# Your Gmail MCP server URL (from Claude.ai connected apps)
GMAIL_MCP_URL = "https://gmailmcp.googleapis.com/mcp/v1"

# ── Calendar MCP Settings ────────────────────────────────────────────────────
CALENDAR_MCP_URL = "https://calendarmcp.googleapis.com/mcp/v1"

# ── Follow-up Settings ───────────────────────────────────────────────────────
# Number of days after which to flag an application as "no response"
NO_RESPONSE_DAYS = 14

# ── Persona for Interview Coach ───────────────────────────────────────────────
COACH_PERSONA = """
You are a senior staff engineer who has conducted 200+ technical interviews
at top AI companies. You are precise, direct, and constructive.
You evaluate answers honestly and give the ideal answer after each response.
"""
