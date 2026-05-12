"""
agents/cover_letter_agent.py

Cover letter generation agent.
Takes a job description and generates a tailored cover letter
using the user's profile from config.py.

Usage:
    from agents.cover_letter_agent import CoverLetterAgent
    agent = CoverLetterAgent()
    letter = agent.generate(
        role="Senior AI Engineer",
        company="Acme Corp",
        jd="We are looking for...",
        tone="senior-confident",
        emphasis=["RAG", "knowledge graphs"]
    )
    print(letter)
"""

import anthropic
from typing import Optional

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


TONE_INSTRUCTIONS = {
    "senior-confident": "Write with quiet authority. Lead with impact. Assume the reader knows you are qualified.",
    "warm-collaborative": "Warm, human tone. Emphasise teamwork, mentorship, and shared goals.",
    "technical-precise": "Precise and technical. Reference specific systems, frameworks, and metrics.",
    "concise-direct": "Maximum 250 words. Every sentence earns its place. No filler.",
}


def build_profile_context(profile: dict) -> str:
    """Convert profile dict to a rich context string for the system prompt."""
    lines = [
        f"Name: {profile.get('name', 'The candidate')}",
        f"Current role: {profile.get('current_title')} at {profile.get('current_company')}",
        f"Experience: {profile.get('years_experience')}+ years in ML/AI",
        f"Location: {profile.get('location')}",
        "",
        "Core skills: " + ", ".join(profile.get("core_skills", [])),
        "",
        "Key achievements:",
    ]
    for ach in profile.get("achievements", []):
        lines.append(f"  - {ach}")

    lines.append("")
    lines.append("Education:")
    for edu in profile.get("education", []):
        lines.append(f"  - {edu}")

    lines.append("")
    lines.append("Previous companies: " + ", ".join(profile.get("companies", [])))

    return "\n".join(lines)


class CoverLetterAgent:
    """
    Agent that generates tailored cover letters.

    Persona: a senior career strategist who knows how to
    translate deep technical experience into compelling narratives
    without corporate fluff.
    """

    def __init__(self, profile: Optional[dict] = None):
        self.client = anthropic.Anthropic()
        self.profile = profile or PROFILE
        self.profile_context = build_profile_context(self.profile)

    def generate(
        self,
        role: str,
        company: str,
        jd: str = "",
        tone: str = "senior-confident",
        emphasis: Optional[list] = None,
        max_words: int = 350,
    ) -> str:
        """
        Generate a tailored cover letter.

        Args:
            role: Job title
            company: Company name
            jd: Job description text (or key requirements)
            tone: One of senior-confident, warm-collaborative,
                  technical-precise, concise-direct
            emphasis: List of skills/topics to emphasise
            max_words: Maximum word count

        Returns:
            Cover letter body text (no headers/addresses)
        """
        tone_instruction = TONE_INSTRUCTIONS.get(
            tone, TONE_INSTRUCTIONS["senior-confident"]
        )

        system = f"""You write cover letters for a senior AI professional.

CANDIDATE PROFILE:
{self.profile_context}

WRITING RULES:
- {tone_instruction}
- Maximum {max_words} words
- 3 to 4 paragraphs
- Do NOT start with "I am writing to..."
- Do NOT use em dashes
- Lead with value, not with "I"
- Reference specific projects and metrics from the profile
- End with a confident, non-desperate close
- No address headers, no date — body paragraphs only
- Be specific: name the company and role"""

        emphasis_str = ""
        if emphasis:
            emphasis_str = f"\nEmphasise in particular: {', '.join(emphasis)}"

        user = f"""Write a cover letter for this application:

Role: {role}
Company: {company}
{f'Job Description:{chr(10)}{jd}' if jd else ''}
{emphasis_str}"""

        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        return response.content[0].text

    def generate_variants(
        self,
        role: str,
        company: str,
        jd: str = "",
        n: int = 2,
    ) -> list[str]:
        """Generate N variants of a cover letter for comparison."""
        tones = ["senior-confident", "technical-precise", "warm-collaborative", "concise-direct"]
        return [
            self.generate(role, company, jd, tone=tones[i % len(tones)])
            for i in range(n)
        ]


if __name__ == "__main__":
    agent = CoverLetterAgent()
    letter = agent.generate(
        role="Senior Applied AI Engineer",
        company="Example Corp",
        jd="We are looking for a senior AI engineer with RAG and LLM experience.",
        tone="senior-confident",
        emphasis=["RAG", "knowledge graphs", "telecom AI"],
    )
    print(letter)
