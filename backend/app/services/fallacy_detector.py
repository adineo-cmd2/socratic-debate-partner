"""Rule-based fallacy detector with optional LLM confirmation.

Runs offline with regex/keyword patterns only, so the backend works with an
empty .env (mock mode). Returns a list of {fallacy_type, snippet, confidence}.
"""

import re

_PATTERNS: list[tuple[str, list[str]]] = [
    ("ad_hominem", [r"you are an? (idiot|stupid|dumb|moron|fool|ignorant|liar|coward)",
                    r"you'?re (an? )?(idiot|stupid|dumb|moron|fool|ignorant)",
                    r"attack(ing)? (you|the person|him|her|them)( instead of| rather than)?( the argument)?",
                    r"shut up", r"nobody likes you"]),
    ("straw_man", [r"so you('re| are) saying", r"so you think (everyone|nobody|all|we should)",
                   r"misrepresent", r"that's not what .+ (said|meant)",
                   r"you want us all to"]),
    ("false_dichotomy", [r"\beither .+ or .+", r"with us or against us",
                          r"only two (options|choices)", r"no middle ground",
                          r"you'?re either .+ or .+"]),
    ("appeal_to_authority", [r"(expert|scientist|doctor|professor|celebrity|pastor|guru|coach).{0,40}said",
                              r"because .{0,20}(he|she|they) (is|are) (an? )?(expert|authority|famous)",
                              r"as an? (expert|authority)", r"my (doctor|professor) says?"]),
    ("slippery_slope", [r"slippery slope", r"next thing you know", r"before long",
                         r"(will |would )?inevitably lead to", r"it starts with .+ (and ends|then)",
                         r"then .+ will (lead to|cause|result in)"]),
    ("circular_reasoning", [r"it'?s true because it'?s", r"because (it )?is (true|right|correct)",
                             r"is true because (the|it|he|she|they)", r"begging the question"]),
    ("appeal_to_emotion", [r"think of the children", r"how dare you",
                            r"it'?s (sad|scary|outrageous|disgusting) (that|how)",
                            r"you should be (ashamed|afraid)"]),
    ("emotional_reasoning", [r"\bi feel (it|that|like)\b", r"in my heart",
                              r"my gut (tells me|says)", r"i just (know|feel)"]),
    ("overgeneralisation", [r"\b(always|never|everyone|everybody|nobody|no one)\b",
                             r"all .+ are (stupid|wrong|evil|good|right|corrupt)"]),
]

_COMPILED: list[tuple[str, re.Pattern[str]]] = [
    (name, re.compile(r"(?:%s)" % "|".join(parts), re.IGNORECASE))
    for name, parts in _PATTERNS
]

CONFIDENCE = 0.8
_SNIPPET_LEN = 120


def detect_fallacies(text: str) -> list[dict]:
    """Flag known fallacies in text via local patterns.

    Returns a list of {"fallacy_type": str, "snippet": str, "confidence": float}.
    Clean text yields [].
    """
    if not text or not text.strip():
        return []
    snippet = text.strip()[:_SNIPPET_LEN]
    found: list[dict] = []
    for name, pattern in _COMPILED:
        if pattern.search(text):
            found.append(
                {"fallacy_type": name, "snippet": snippet, "confidence": CONFIDENCE}
            )
    return found
