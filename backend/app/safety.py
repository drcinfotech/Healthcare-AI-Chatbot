"""
Safety detection — runs BEFORE intent classification.

For a healthcare chatbot, missing an emergency is far worse than misclassifying
an intent. This module scans for indicators of:

  • Medical emergencies (cardiac, stroke, breathing, severe bleeding, overdose)
  • Mental health crises (suicide ideation, self-harm)

When detected, the engine SHORT-CIRCUITS the normal flow and returns an
emergency block with hotline numbers — no diagnosis, no advice, just routing.

This is intentionally conservative: false positives are acceptable
(we direct someone to call a hotline when they didn't need to); false
negatives are not.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class SafetyResult:
    flag: Optional[Literal["emergency", "mental_health"]]
    reason: str = ""


# ─── Medical emergency patterns ────────────────────────────
# Each pattern signals a likely medical emergency. We use word-boundary
# regex so "chest" doesn't match "chestnut", etc.
EMERGENCY_PATTERNS = [
    # Cardiac
    r"\bchest\s+pain\b",
    r"\bcrushing\s+chest\b",
    r"\bheart\s+attack\b",
    r"\bcardiac\s+arrest\b",
    # Stroke / neuro
    r"\bstroke\b",
    r"\bface\s+(is\s+)?(droop|sagging|paralys|saggin)",
    r"\b(droop|sagging)(ing|s)?\s+face\b",
    r"\bslurred\s+speech\b",
    r"\bspeech\s+(is\s+)?slurred\b",
    r"\bsudden\s+(weakness|numbness)\b",
    r"\bone\s+side\s+(weak|numb|paralyzed)",
    # Breathing
    r"\bcan'?t\s+breathe\b",
    r"\bcannot\s+breathe\b",
    r"\bnot\s+breathing\b",
    r"\bstopped\s+breathing\b",
    r"\bchoking\b",
    r"\bblue\s+lips\b",
    # Bleeding / trauma
    r"\bsevere\s+bleeding\b",
    r"\buncontroll(ed|able)\s+bleeding\b",
    r"\bcoughing\s+up\s+blood\b",
    r"\bvomiting\s+blood\b",
    # Overdose / poisoning
    r"\boverdos\w*\b",
    r"\bpoison(ed|ing)\b",
    r"\bswallowed\s+(too\s+many|all\s+the)\s+pills\b",
    # Unconsciousness / seizure
    r"\bunconscious\b",
    r"\bpassed\s+out\b",
    r"\bnot\s+responding\b",
    r"\bseizure\b",
    r"\bconvulsions?\b",
    # Severe allergic
    r"\banaphylax\w*\b",
    r"\bthroat\s+(closing|swelling\s+shut)\b",
    # General red-flag
    r"\bcall\s+(an?\s+)?ambulance\b",
    r"\b911\b",
    r"\b112\b",
    r"\b108\b",
    r"\bemergency\s+room\b",
]


# ─── Mental health crisis patterns ─────────────────────────
MENTAL_HEALTH_CRISIS_PATTERNS = [
    r"\bkill\s+myself\b",
    r"\bkill\s+my\s*self\b",
    r"\bsuicid(e|al)\b",
    r"\bend\s+(my\s+)?life\b",
    r"\bend\s+it\s+all\b",
    r"\bwant\s+to\s+die\b",
    r"\bdon'?t\s+want\s+to\s+live\b",
    r"\bcan'?t\s+go\s+on\b",
    r"\bharm(ing)?\s+my\s*self\b",
    r"\bself-?harm\b",
    r"\bcutting\s+my\s*self\b",
    r"\bno\s+reason\s+to\s+live\b",
    r"\beveryone'?d?\s+be\s+better\s+off\b",
]


# ─── India + International emergency hotlines ──────────────
EMERGENCY_HOTLINES = [
    {"label": "Emergency services (India)",       "number": "112"},
    {"label": "Ambulance (India)",                "number": "108"},
    {"label": "Fire & rescue (India)",            "number": "101"},
    {"label": "Women's helpline (India)",         "number": "1091"},
]

MENTAL_HEALTH_HOTLINES = [
    {"label": "iCall — Mental Health (India)",            "number": "+91-9152987821"},
    {"label": "Vandrevala Foundation (India, 24/7)",      "number": "1860-2662-345"},
    {"label": "AASRA Suicide Prevention (India, 24/7)",   "number": "+91-9820466726"},
    {"label": "Emergency services (India)",               "number": "112"},
]


def check_safety(text: str) -> SafetyResult:
    """
    Inspect the user's message for emergency or mental-health crisis signals.

    Mental health checks come first because some queries
    (e.g. "I want to die") would also match the emergency net otherwise.
    """
    text_lc = text.lower()

    for pat in MENTAL_HEALTH_CRISIS_PATTERNS:
        if re.search(pat, text_lc):
            return SafetyResult(flag="mental_health", reason=pat)

    for pat in EMERGENCY_PATTERNS:
        if re.search(pat, text_lc):
            return SafetyResult(flag="emergency", reason=pat)

    return SafetyResult(flag=None)


def build_emergency_block() -> dict:
    return {
        "type": "emergency",
        "headline": "This sounds like an emergency.",
        "message": (
            "Please call emergency services right now — every minute matters. "
            "I'm a chatbot and can't help with urgent medical situations. "
            "If someone is with you, ask them to call too."
        ),
        "hotlines": EMERGENCY_HOTLINES,
    }


def build_mental_health_block() -> dict:
    return {
        "type": "emergency",
        "headline": "I hear you, and I'm glad you reached out.",
        "message": (
            "What you're feeling matters, and you don't have to face it alone. "
            "Please reach out to a trained counselor — they're available 24/7, "
            "free, and confidential. You deserve support."
        ),
        "hotlines": MENTAL_HEALTH_HOTLINES,
    }
