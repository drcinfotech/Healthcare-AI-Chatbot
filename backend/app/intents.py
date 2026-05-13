"""
Intent classifier for the healthcare chatbot.

Same hybrid pattern + keyword approach as the catalog version,
specialized for healthcare/medical/pharmacy queries.

Safety detection (see safety.py) runs BEFORE this classifier.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IntentSpec:
    name: str
    patterns: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


INTENTS: list[IntentSpec] = [
    IntentSpec(
        "greeting",
        patterns=[r"^\s*(hi|hello|hey|hola|namaste|good (morning|afternoon|evening))\b"],
        keywords=["hi", "hello", "hey", "hola", "namaste", "greetings"],
    ),
    IntentSpec(
        "goodbye",
        patterns=[r"\b(bye|goodbye|see ya|see you|cya|take care)\b"],
        keywords=["bye", "goodbye", "later"],
    ),
    IntentSpec(
        "thanks",
        patterns=[r"^\s*(thanks|thank you|thx|ty|appreciate it)\b"],
        keywords=["thanks", "thank", "appreciate"],
    ),
    IntentSpec(
        "book_appointment",
        patterns=[
            r"\b(book|schedule|make|set\s+up|arrange)\b.*\b(appointment|consult(ation)?|visit)\b",
            r"\b(appointment|consult(ation)?)\b.*\b(book|schedule|with)\b",
            r"\bsee\s+(a\s+)?(doctor|specialist|gp)\b",
            r"\bget\s+(an?\s+)?appointment\b",
        ],
        keywords=["appointment", "book", "schedule", "consultation"],
    ),
    IntentSpec(
        "find_doctor",
        patterns=[
            r"\b(find|search|looking for|need|recommend)\s+(a\s+)?(doctor|specialist|cardiologist|pediatrician|dermatologist|gynec\w+|psychiatrist|orthoped\w+|neurologist|endocrinolog\w+|ent|ophthalmolog\w+|gp|physician)\b",
            r"\b(doctor|specialist)\s+for\b",
            r"\bwhich\s+doctor\b",
        ],
        keywords=["doctor", "specialist", "cardiologist", "pediatrician", "dermatologist", "physician"],
    ),
    IntentSpec(
        "symptom_check",
        patterns=[
            r"\bi\s+(have|feel|am\s+having|am\s+experiencing|got)\s+\b",
            r"\bmy\s+(head|stomach|chest|back|throat|leg|arm|neck|eye|ear|tooth|teeth)\s+(hurts?|aches?|is\s+(painful|sore))",
            r"\b(headache|migraine|stomachache|fever|nausea|vomiting|diarrhea|rash|cough|cold|flu|sore\s+throat|dizzy|dizziness|fatigue|tired)\b",
            r"\bwhat'?s\s+wrong\s+with\s+me\b",
            r"\bdo\s+i\s+have\b",
        ],
        keywords=["symptom", "hurts", "pain", "feel", "fever", "headache", "cough", "rash", "nausea", "dizzy"],
    ),
    IntentSpec(
        "medication_info",
        patterns=[
            r"\b(what\s+is|tell\s+me\s+about|info\s+on|information\s+about|about)\s+\w+\b",
            r"\b(side\s+effects|interactions|dosage|how\s+to\s+take)\b",
            r"\bcan\s+i\s+take\b",
        ],
        keywords=["medication", "medicine", "drug", "tablet", "dosage", "dose", "side effects"],
    ),
    IntentSpec(
        "medication_search",
        patterns=[
            r"\b(find|search|looking for|need|show me|do you have)\s+.*\b(medicine|medication|tablet|syrup|pill|drug|cream|ointment|inhaler|drops)\b",
            r"\b(for|to\s+treat)\s+(pain|cough|cold|allergy|fever|acid|sleep|anxiety|skin)\b",
        ],
        keywords=["find medicine", "buy medicine", "need medication", "looking for"],
    ),
    IntentSpec(
        "prescription_refill",
        patterns=[
            r"\b(refill|re-fill|renew)\b.*\b(prescription|rx|medication|medicine)\b",
            r"\b(prescription|rx)\b.*\b(refill|renew|reorder)\b",
            r"\bneed\s+more\s+(of\s+my\s+)?(medication|medicine|pills?|prescription)\b",
            r"\brun(ning)?\s+out\s+of\s+(my\s+)?(medication|medicine|pills?|prescription)\b",
        ],
        keywords=["refill", "renew", "prescription", "rx"],
    ),
    IntentSpec(
        "prescription_status",
        patterns=[
            r"\b(my|view|see|show|check)\s+(prescriptions?|rx|medications?)\b",
            r"\b(what|which)\s+(am\s+i\s+taking|medications?\s+do\s+i\s+have)\b",
            r"\b(active|current)\s+prescriptions?\b",
        ],
        keywords=["prescription", "rx", "medications i take"],
    ),
    IntentSpec(
        "lab_results",
        patterns=[
            r"\b(lab|laboratory|blood|test|report)\s+(results?|reports?)\b",
            r"\b(my|view|show|see|check)\s+(lab|test|blood|reports?)\b",
            r"\bcholesterol\s+(level|result)\b",
            r"\bsugar\s+(level|result)\b",
            r"\bhba1c\b",
            r"\bcbc\b",
        ],
        keywords=["lab", "blood test", "results", "report", "cholesterol", "hba1c"],
    ),
    IntentSpec(
        "vaccine_info",
        patterns=[
            r"\b(vaccine|vaccination|immunization|shot|jab)\b",
            r"\b(due|need|schedule)\s+(my\s+)?(vaccine|vaccination|shot|jab|booster)\b",
            r"\bflu\s+shot\b",
            r"\bcovid\s+(vaccine|booster|jab)\b",
            r"\bvaccination\s+schedule\b",
        ],
        keywords=["vaccine", "vaccination", "immunization", "shot", "booster", "jab"],
    ),
    IntentSpec(
        "pharmacy_locator",
        patterns=[
            r"\b(nearest|nearby|closest|find|where)\s+(a\s+)?(pharmacy|chemist|drugstore|drug\s+store|medical\s+store)\b",
            r"\b(pharmacy|chemist|drugstore)\s+(near|nearby|close)\b",
            r"\bdelivery\s+pharmacy\b",
        ],
        keywords=["pharmacy", "chemist", "drugstore", "medical store"],
    ),
    IntentSpec(
        "insurance_info",
        patterns=[
            r"\binsurance\b",
            r"\b(cover(ed|age)?|claim|reimburse)\b",
            r"\bcashless\b",
            r"\bmediclaim\b",
        ],
        keywords=["insurance", "coverage", "claim", "cashless", "policy"],
    ),
    IntentSpec(
        "video_consult",
        patterns=[
            r"\b(video|online|virtual|tele)(\s+|-)?consult(ation)?\b",
            r"\btelemedicine\b",
            r"\b(call|talk\s+to)\s+(a\s+)?doctor\s+(online|on\s+video|virtually)\b",
        ],
        keywords=["video consult", "telemedicine", "online doctor"],
    ),
    IntentSpec(
        "mental_health_general",
        patterns=[
            r"\bstress(ed)?\b",
            r"\banxious\b",
            r"\banxiety\b",
            r"\bdepress(ed|ion)\b",
            r"\b(feel(ing)?|been)\s+(down|low|sad)\b",
            r"\bcan'?t\s+sleep\b",
            r"\bpanic\s+attacks?\b",
            r"\bovercoming\s+(stress|anxiety)\b",
            r"\bmental\s+health\b",
            r"\btherap(y|ist)\b",
        ],
        keywords=["stress", "anxiety", "depressed", "depression", "therapy", "counseling"],
    ),
    IntentSpec(
        "talk_to_human",
        patterns=[
            r"\b(speak|talk|connect)\s+to\s+(a\s+)?(human|nurse|doctor|pharmacist|agent|person|representative)\b",
            r"\b(real|live)\s+(person|doctor|nurse)\b",
            r"\bhuman\s+support\b",
        ],
        keywords=["human", "nurse", "agent", "representative", "live support"],
    ),
]


# ─── Entity extraction ─────────────────────────────────────
SPECIALTIES = {
    "cardiology":      ["cardiologist", "cardiology", "heart doctor", "heart specialist"],
    "pediatrics":      ["pediatrician", "paediatrician", "pediatrics", "child doctor", "kids doctor"],
    "dermatology":     ["dermatologist", "dermatology", "skin doctor", "skin specialist"],
    "orthopedics":     ["orthopedist", "orthopaedist", "orthopedics", "bone doctor", "ortho"],
    "general":         ["gp", "general physician", "family doctor", "internist", "general medicine"],
    "psychiatry":      ["psychiatrist", "psychiatry"],
    "gynecology":      ["gynecologist", "gynaecologist", "gynecology", "obgyn", "ob/gyn", "women's doctor"],
    "ent":             ["ent", "ear nose throat", "otolaryngologist"],
    "ophthalmology":   ["ophthalmologist", "eye doctor", "eye specialist"],
    "endocrinology":   ["endocrinologist", "endocrinology", "hormone doctor", "diabetes specialist"],
    "neurology":       ["neurologist", "neurology", "brain doctor", "nerve doctor"],
    "gastroenterology": ["gastroenterologist", "gastroenterology", "gi doctor", "stomach doctor"],
}

MEDICATION_CATEGORIES = {
    "pain_relief":    ["pain", "headache", "ache", "migraine", "body pain", "muscle pain"],
    "cough_cold":     ["cough", "cold", "flu", "sore throat", "sneez"],
    "allergy":        ["allergy", "allergies", "hay fever", "hives", "itch"],
    "digestive":      ["acid", "heartburn", "indigestion", "acidity", "stomach", "gas"],
    "antibiotic":     ["antibiotic", "bacterial", "infection"],
    "vitamin":        ["vitamin", "supplement", "deficiency"],
    "diabetes":       ["diabetes", "blood sugar", "sugar", "glucose"],
    "cholesterol":    ["cholesterol", "lipid", "ldl", "hdl"],
    "blood_pressure": ["bp", "blood pressure", "hypertension"],
    "anxiety":        ["anxiety", "panic"],
    "sleep":          ["sleep", "insomnia"],
    "eye_care":       ["eye drops", "dry eyes", "redness"],
    "thyroid":        ["thyroid", "hypothyroid"],
    "asthma":         ["asthma", "inhaler", "breathing"],
    "skin":           ["skin", "rash", "eczema", "acne", "pimple"],
    "womens_health":  ["periods", "menstrual", "pms", "cramps"],
    "pediatric":      ["child", "kid", "baby", "infant"],
}

SYMPTOM_KEYWORDS = [
    "headache", "migraine", "fever", "cough", "cold", "sore throat",
    "nausea", "vomiting", "diarrhea", "constipation", "rash", "itching",
    "back pain", "joint pain", "muscle pain", "stomach pain", "abdominal pain",
    "dizziness", "fatigue", "tiredness", "shortness of breath",
    "runny nose", "sneezing", "sinus", "earache", "toothache",
]


def extract_specialty(text: str) -> Optional[str]:
    t = text.lower()
    for spec, words in SPECIALTIES.items():
        if any(w in t for w in words):
            return spec
    return None


def extract_med_category(text: str) -> Optional[str]:
    t = text.lower()
    for cat, words in MEDICATION_CATEGORIES.items():
        if any(w in t for w in words):
            return cat
    return None


def extract_symptoms(text: str) -> list[str]:
    t = text.lower()
    return [s for s in SYMPTOM_KEYWORDS if s in t]


def extract_med_name(text: str, known_med_names: list[str]) -> Optional[str]:
    """Find a known medication name in the user's text (case-insensitive)."""
    t = text.lower()
    for name in known_med_names:
        if name.lower() in t:
            return name
    return None


# ─── Classifier ────────────────────────────────────────────
@dataclass
class Classification:
    intent: str
    confidence: float
    entities: dict


def classify(text: str, known_med_names: Optional[list[str]] = None) -> Classification:
    raw = text
    text_lc = text.lower().strip()
    known_med_names = known_med_names or []

    scores: dict[str, float] = {}

    for spec in INTENTS:
        score = 0.0
        for p in spec.patterns:
            if re.search(p, text_lc, re.IGNORECASE):
                score += 2.0
        for kw in spec.keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lc):
                score += 0.6
        if score > 0:
            scores[spec.name] = score

    if not scores:
        intent, conf = "unknown", 0.0
    else:
        intent = max(scores, key=scores.get)
        top = scores[intent]
        rest = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0.1
        conf = min(1.0, top / (top + rest))

    entities = {
        "specialty":      extract_specialty(raw),
        "med_category":   extract_med_category(raw),
        "symptoms":       extract_symptoms(raw),
        "med_name":       extract_med_name(raw, known_med_names),
    }

    return Classification(intent=intent, confidence=round(conf, 2), entities=entities)
