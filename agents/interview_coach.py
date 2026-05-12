"""
agents/interview_coach.py

Multi-turn technical interview coaching agent.
Asks questions, evaluates answers, gives ideal responses.

Usage:
    from agents.interview_coach import InterviewCoach
    coach = InterviewCoach()
    
    # Start a session
    coach.start_session(topic="RAG system design")
    
    # Multi-turn conversation
    response = coach.ask("How would you design a RAG system for telecom?")
    print(response)
    
    answer = "I would start by chunking the documents..."
    evaluation = coach.evaluate(answer)
    print(evaluation)
"""

import anthropic
from typing import Optional
from enum import Enum

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from profile_loader import parse_profile_md, build_profile_context

try:
    import config
    LLM_MODEL = config.LLM_MODEL
    LLM_MAX_TOKENS = config.LLM_MAX_TOKENS
    COACH_PERSONA = config.COACH_PERSONA
except ImportError:
    LLM_MODEL = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS = 1000
    COACH_PERSONA = "You are a senior staff engineer who has conducted 200+ technical interviews."

PROFILE = parse_profile_md()


TOPIC_PROMPTS = {
    "transformer": "Ask a senior-level question about transformer architecture, attention mechanisms, or positional encoding.",
    "rag": "Ask about RAG system design for enterprise — chunking, retrieval, reranking, evaluation.",
    "finetuning": "Ask about fine-tuning, LoRA, PEFT, or when to use fine-tuning vs prompting vs RAG.",
    "python": "Give a Python coding question — medium difficulty, data science context. Hashmaps, strings, or pandas.",
    "system_design": "Ask the candidate to design a compound AI system for a telecom or enterprise use case.",
    "behavioural": "Ask a behavioural question in STAR format about leading an AI project under constraints.",
    "llm_eval": "Ask about LLM evaluation — RAGAS, G-Eval, LLM-as-judge, hallucination detection.",
    "knowledge_graph": "Ask about knowledge graphs, MCP-based agentic systems, or graph-based retrieval.",
    "mlops": "Ask about MLOps, model monitoring, drift detection, or production ML deployment.",
    "recruiter": "Simulate a recruiter screening call. Ask the opening question and wait for the candidate's pitch.",
}


class CoachMode(Enum):
    ASKING = "asking"
    EVALUATING = "evaluating"
    IDLE = "idle"


class InterviewCoach:
    """
    Multi-turn interview coaching agent.

    Persona: senior staff engineer, precise and direct.
    Evaluates answers honestly. Gives ideal answers after each response.
    """

    def __init__(self, profile: Optional[dict] = None):
        self.client = anthropic.Anthropic()
        self.profile = profile or PROFILE
        self.history = []
        self.mode = CoachMode.IDLE
        self.current_topic = None

        self.system = f"""You are an expert technical interview coach for senior AI/ML roles.
{COACH_PERSONA}

CANDIDATE BACKGROUND:
Name: {self.profile.get('name', 'The candidate')}
Role: {self.profile.get('current_title')} at {self.profile.get('current_company')}
Skills: {', '.join(self.profile.get('core_skills', []))}
Education: {'; '.join(self.profile.get('education', [])[:2])}
Achievements: {'; '.join(self.profile.get('achievements', [])[:2])}

COACHING RULES:
- Ask ONE clear question at a time and wait for the answer
- When evaluating: say what was strong, what was missing, then give ideal answer in 3-5 bullets
- For coding: ask for approach explanation first, then provide clean Python solution
- For system design: use Data > Retrieval > Reasoning > Evaluation > Cost/Latency framework
- Keep responses under 250 words
- Be direct. No filler. No em dashes.
- Never give the answer before the candidate tries"""

    def chat(self, user_message: str) -> str:
        """Send a message and get a response. Maintains full conversation history."""
        self.history.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            system=self.system,
            messages=self.history,
        )

        reply = response.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def start_topic(self, topic: str) -> str:
        """Start a drill on a specific topic."""
        self.current_topic = topic
        prompt = TOPIC_PROMPTS.get(topic, f"Ask a senior-level question about {topic}.")
        return self.chat(prompt)

    def reset(self):
        """Clear conversation history and start fresh."""
        self.history = []
        self.mode = CoachMode.IDLE
        self.current_topic = None
        return "Session reset. Ready for a new topic."

    def get_summary(self) -> str:
        """Get a summary of the session — strong areas and gaps."""
        if len(self.history) < 4:
            return "Not enough conversation to summarise yet."

        return self.chat(
            "Summarise this coaching session. List: (1) topics covered, "
            "(2) strongest answers, (3) gaps to address before interviews. "
            "Be specific and actionable."
        )

    def get_history(self) -> list:
        """Return conversation history."""
        return self.history.copy()


class BatchQuestionGenerator:
    """
    Generate a batch of interview questions for a given role and JD.
    Useful for prep before a specific interview.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()

    def generate(
        self,
        role: str,
        jd: str = "",
        n_technical: int = 5,
        n_behavioural: int = 3,
        n_system_design: int = 2,
    ) -> dict:
        """
        Generate interview questions tailored to a role and JD.

        Returns dict with keys: technical, behavioural, system_design
        """
        prompt = f"""Generate interview questions for this role:

Role: {role}
{f'JD excerpt: {jd[:500]}' if jd else ''}

Generate:
- {n_technical} technical questions (ML/AI, increasing difficulty)
- {n_behavioural} behavioural questions (STAR format prompts)
- {n_system_design} system design questions

Return as JSON with keys: technical, behavioural, system_design.
Each value is a list of question strings.
Return ONLY valid JSON, no markdown, no preamble."""

        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

        import json
        try:
            return json.loads(response.content[0].text)
        except json.JSONDecodeError:
            return {"error": "Could not parse questions", "raw": response.content[0].text}


if __name__ == "__main__":
    coach = InterviewCoach()
    print("Starting RAG system design drill...\n")
    question = coach.start_topic("rag")
    print(f"Coach: {question}\n")

    answer = "I would chunk documents, embed them with sentence transformers, store in ChromaDB, and retrieve top-k using cosine similarity."
    print(f"Candidate: {answer}\n")

    evaluation = coach.chat(answer)
    print(f"Coach: {evaluation}\n")
