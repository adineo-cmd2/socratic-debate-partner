"""Socratic question engine: LLM when keys exist, mock templates otherwise.

Works out-of-the-box with an empty .env (mock mode). Every returned question
ends with "?" and is at most 25 words (enforced by ensure_question).
"""

import os

MAX_WORDS = 25

_MOCK_FOLLOWUPS = [
    "What evidence supports your view on {topic}?",
    "What assumption might your reasoning depend on here?",
    "How would someone who disagrees challenge that point?",
    "What would change your mind about this claim?",
    "What follows if that claim turns out to be false?",
]


def ensure_question(text: str) -> str:
    """Guardrail: truncate to <=25 words and force a trailing "?"."""
    words = (text or "").strip().split()
    if not words:
        return "What makes you hold that view?"
    words = words[:MAX_WORDS]
    out = " ".join(words).rstrip(".! ")
    if not out.endswith("?"):
        out += "?"
    return out


def _mock_question(history: list, fallacies: list, topic: str) -> str:
    depth = len(history or [])
    if fallacies:
        first = (fallacies[0] or {}).get("fallacy_type", "weak reasoning")
        label = str(first).replace("_", " ")
        return ensure_question(
            f"Could {label} be shaping that claim, and what evidence avoids it?"
        )
    template = _MOCK_FOLLOWUPS[depth % len(_MOCK_FOLLOWUPS)]
    return ensure_question(template.format(topic=topic or "this topic"))


def _llm_question(history: list, fallacies: list, topic: str) -> str | None:
    """Try real providers; return None when unavailable so caller uses mock."""
    fallacy_names = [str((f or {}).get("fallacy_type", "")) for f in (fallacies or [])]
    prompt = (
        "Ask exactly one Socratic question (max 25 words, ends with '?') "
        f"about '{topic}'. History: {history}. Detected fallacies: {fallacy_names}."
    )
    try:
        if os.getenv("ANTHROPIC_API_KEY"):
            from anthropic import Anthropic

            client = Anthropic()
            msg = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )
            return ensure_question(msg.content[0].text)
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI

            client = OpenAI()
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )
            return ensure_question(resp.choices[0].message.content or "")
    except Exception:
        return None
    return None


def generate_question(history: list, fallacies: list, topic: str) -> str:
    """Generate one Socratic follow-up; never raises (falls back to mock)."""
    try:
        question = _llm_question(history, fallacies, topic)
    except Exception:
        question = None
    if not question:
        question = _mock_question(history, fallacies, topic)
    return ensure_question(question)
