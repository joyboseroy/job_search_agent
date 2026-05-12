"""
profile_loader.py

Loads the candidate profile from steering/profile.md.
Used by all Python agents so they share the same source of truth
as the skill .md files.

Falls back to config.py if steering/profile.md is not found.
"""

import os
import re
from pathlib import Path


def load_profile_md(path: str = "steering/profile.md") -> str:
    """
    Load the raw markdown profile text.
    Returns empty string if not found.
    """
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def parse_profile_md(path: str = "steering/profile.md") -> dict:
    """
    Parse steering/profile.md into a dict compatible with config.py PROFILE.

    Reads the markdown sections and extracts key fields.
    Falls back to config.py if file not found or unparseable.
    """
    raw = load_profile_md(path)

    if not raw:
        return _fallback_profile()

    profile = {}

    # Name
    name_match = re.search(r"\*\*Name:\*\*\s*(.+)", raw)
    profile["name"] = name_match.group(1).strip() if name_match else "The candidate"

    # Current title
    title_match = re.search(r"\*\*Current title:\*\*\s*(.+)", raw)
    if title_match:
        title_line = title_match.group(1).strip()
        # "Senior Data Scientist at Ericsson Global" -> split on " at "
        if " at " in title_line:
            parts = title_line.split(" at ", 1)
            profile["current_title"] = parts[0].strip()
            profile["current_company"] = parts[1].strip()
        else:
            profile["current_title"] = title_line
            profile["current_company"] = ""

    # Years experience
    years_match = re.search(r"\*\*Experience:\*\*\s*(\d+)", raw)
    profile["years_experience"] = int(years_match.group(1)) if years_match else 15

    # Location
    loc_match = re.search(r"\*\*Location:\*\*\s*(.+)", raw)
    profile["location"] = loc_match.group(1).strip() if loc_match else ""

    # Core skills — list items under "## Core technical skills"
    profile["core_skills"] = _extract_list_section(raw, "Core technical skills")

    # Achievements
    profile["achievements"] = _extract_list_section(raw, "Key achievements")

    # Education
    profile["education"] = _extract_list_section(raw, "Education")

    # Companies
    companies_match = re.search(r"## Previous companies\s*\n+(.+)", raw)
    if companies_match:
        line = companies_match.group(1).strip()
        profile["companies"] = [c.strip() for c in re.split(r"[·\|,]", line) if c.strip()]
    else:
        profile["companies"] = []

    # Target roles
    profile["target_roles"] = _extract_list_section(raw, "Target roles")

    # Target locations
    profile["target_locations"] = _extract_list_section(raw, "Target locations")

    return profile


def _extract_list_section(text: str, section_name: str) -> list:
    """Extract bullet list items from a markdown section."""
    pattern = rf"## {section_name}\s*\n((?:.*\n)*?)(?=\n##|\Z)"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return []

    section = match.group(1)
    items = []
    for line in section.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            item = line[2:].strip()
            # Skip template placeholders
            if not item.startswith("[") and item:
                items.append(item)
    return items


def _fallback_profile() -> dict:
    """Fall back to config.py if profile.md not found."""
    try:
        import config
        return config.PROFILE
    except ImportError:
        try:
            import config_template
            return config_template.PROFILE
        except ImportError:
            return {
                "name": "The candidate",
                "current_title": "Senior Data Scientist",
                "years_experience": 15,
                "current_company": "Your Company",
                "location": "Bengaluru, India",
                "core_skills": [],
                "achievements": [],
                "education": [],
                "companies": [],
                "target_roles": [],
                "target_locations": [],
            }


def build_profile_context(profile: dict) -> str:
    """
    Convert profile dict to rich context string for LLM system prompts.
    Used by all Python agents.
    """
    lines = [
        f"Name: {profile.get('name', 'The candidate')}",
        f"Current role: {profile.get('current_title')} at {profile.get('current_company')}",
        f"Experience: {profile.get('years_experience')}+ years in ML/AI",
        f"Location: {profile.get('location')}",
        "",
    ]

    skills = profile.get("core_skills", [])
    if skills:
        lines.append("Core skills: " + ", ".join(skills))
        lines.append("")

    achievements = profile.get("achievements", [])
    if achievements:
        lines.append("Key achievements:")
        for a in achievements:
            lines.append(f"  - {a}")
        lines.append("")

    education = profile.get("education", [])
    if education:
        lines.append("Education:")
        for e in education:
            lines.append(f"  - {e}")
        lines.append("")

    companies = profile.get("companies", [])
    if companies:
        lines.append("Previous companies: " + ", ".join(companies))

    target_roles = profile.get("target_roles", [])
    if target_roles:
        lines.append("Target roles: " + ", ".join(target_roles))

    return "\n".join(lines)


def get_profile_context() -> str:
    """
    One-liner to get the full profile context string.
    Used at the top of every Python agent.
    """
    profile = parse_profile_md()
    return build_profile_context(profile)


if __name__ == "__main__":
    profile = parse_profile_md()
    print("Parsed profile:")
    for k, v in profile.items():
        print(f"  {k}: {v}")
    print()
    print("Context string:")
    print(build_profile_context(profile))
