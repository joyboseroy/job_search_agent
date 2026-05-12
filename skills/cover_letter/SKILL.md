---
name: cover-letter
description: Generate tailored cover letters for job applications. Use this skill whenever the user pastes a job description, mentions a company they are applying to, asks for a cover letter, application letter, or says things like "help me apply to X", "write something for this role", "I want to apply here". Activate even if the user just pastes a JD with no explicit request — they almost certainly want a cover letter drafted.
---

# Cover Letter Skill

Generates tailored, professional cover letters using the candidate's
profile from the steering file.

---

## When activated

The user has:
- Pasted a job description
- Named a company and role they want to apply to
- Asked for a cover letter or application letter
- Said something like "help me apply to X" or "write something for this JD"

---

## What to do

### Step 1 — Extract from the JD

Read the job description carefully and identify:

- **Role title** — exact title as written
- **Company name**
- **Key requirements** — top 5 technical and soft skills they want
- **Keywords** — specific tools, frameworks, methodologies mentioned
- **Tone** — formal enterprise vs startup casual vs academic

### Step 2 — Match to profile

From the steering file, identify:

- Which achievements are most relevant to this specific role
- Which skills directly match the JD keywords
- Any domain overlap (telecom, enterprise AI, research, etc.)

### Step 3 — Write the letter

**Structure:**
- Paragraph 1: Hook — lead with the most relevant achievement or value proposition. Never start with "I am writing to..."
- Paragraph 2: Technical fit — connect 2-3 specific experiences to the JD requirements with metrics
- Paragraph 3: Why this company/role specifically — show you've read the JD, not just sent a template
- Paragraph 4 (optional): Broader fit — research background, domain expertise, or unique angle
- Close: Confident, brief, no "I look forward to hearing from you at your earliest convenience"

**Rules:**
- Maximum 350 words
- No em dashes
- No bullet points inside the letter
- No address headers or date — body only
- Every sentence earns its place
- Be specific — name actual projects, not vague descriptions

### Step 4 — Ask for tone preference if not obvious

If the user hasn't specified, ask:
> "Should this be senior and confident, warm and collaborative, or technical and precise?"

Default to senior-confident if they say just "write it".

---

## Variants

If the user asks for options or seems unsure, generate 2 variants:
- One leading with technical depth
- One leading with business impact

Label them clearly and let the user choose.

---

## Output format

Just the letter body. No subject line unless asked.
No "Here is your cover letter:" preamble — just output the letter directly.

If asked to also provide a subject line for email:
`Subject: Application — [Role Title], [Your Name]`
