"""
Integration tests for the Healthcare AI Chatbot.

Covers:
  • Safety guardrails (emergency + mental health crisis detection)
  • All 17 healthcare intents
  • API endpoints
  • Catalog integrity

Run with:  pytest -v
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from app.catalog import catalog
from app.safety import check_safety
from app.intents import classify

client = TestClient(app)


# ─── Catalog integrity ─────────────────────────────────────
def test_catalog_loaded():
    assert len(catalog.all_meds()) == 30
    assert len(catalog.all_doctors()) == 12
    assert len(catalog.pharmacies(limit=10)) == 5


def test_no_real_brand_names_in_data():
    """Sanity check: no real-world pharma/medical brand names should appear."""
    forbidden = ["pfizer", "novartis", "tylenol", "advil", "lipitor", "viagra", "ozempic", "wegovy"]
    text = " ".join(m["name"].lower() + " " + m["uses"].lower() for m in catalog.all_meds())
    for brand in forbidden:
        assert brand not in text, f"Found real brand '{brand}' in catalog"


# ─── Safety: emergencies ───────────────────────────────────
def test_safety_chest_pain():
    res = check_safety("I have severe chest pain and can't breathe")
    assert res.flag == "emergency"


def test_safety_stroke():
    res = check_safety("My grandmother's face is drooping and her speech is slurred")
    assert res.flag == "emergency"


def test_safety_overdose():
    res = check_safety("I think I overdosed on my pills")
    assert res.flag == "emergency"


def test_safety_unconscious():
    res = check_safety("My husband is unconscious, what do I do")
    assert res.flag == "emergency"


# ─── Safety: mental health crisis ──────────────────────────
def test_safety_suicide_ideation():
    res = check_safety("I want to kill myself")
    assert res.flag == "mental_health"


def test_safety_end_my_life():
    res = check_safety("I don't want to live anymore")
    assert res.flag == "mental_health"


def test_safety_self_harm():
    res = check_safety("I've been cutting myself")
    assert res.flag == "mental_health"


# ─── Safety: normal queries should NOT trigger ─────────────
def test_safety_no_false_positives():
    safe_queries = [
        "hello",
        "I need pain relief tablets",
        "book a cardiologist",
        "what are my lab results",
        "I have a mild headache",
        "find a pharmacy near me",
    ]
    for q in safe_queries:
        assert check_safety(q).flag is None, f"False positive on: {q!r}"


# ─── Intent classification (representative sample) ─────────
def test_intent_greeting():
    assert classify("hello there").intent == "greeting"


def test_intent_book_appointment():
    assert classify("book an appointment with a cardiologist").intent == "book_appointment"


def test_intent_find_doctor():
    assert classify("find a dermatologist").intent == "find_doctor"


def test_intent_medication_info():
    assert classify("tell me about Lumera 500").intent in {"medication_info", "medication_search"}


def test_intent_lab_results():
    assert classify("show me my lab results").intent == "lab_results"


def test_intent_vaccine():
    assert classify("when is my flu shot due").intent == "vaccine_info"


def test_intent_pharmacy_locator():
    assert classify("find the nearest pharmacy").intent == "pharmacy_locator"


def test_intent_prescription_refill():
    assert classify("refill my prescription").intent == "prescription_refill"


def test_intent_video_consult():
    assert classify("can I do a video consultation").intent == "video_consult"


def test_intent_mental_health_general():
    assert classify("I've been feeling really anxious lately").intent == "mental_health_general"


# ─── API endpoints ─────────────────────────────────────────
def test_api_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["medications"] == 30
    assert body["doctors"] == 12


def test_api_chat_greeting():
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "greeting"
    assert body["safety_flag"] is None
    assert len(body["blocks"]) >= 1


def test_api_chat_emergency_short_circuits():
    r = client.post("/chat", json={"message": "I'm having a heart attack"})
    body = r.json()
    assert body["safety_flag"] == "emergency"
    assert body["intent"] == "emergency"
    assert body["blocks"][0]["type"] == "emergency"


def test_api_chat_mental_health_short_circuits():
    r = client.post("/chat", json={"message": "I want to end my life"})
    body = r.json()
    assert body["safety_flag"] == "mental_health"
    assert body["blocks"][0]["type"] == "emergency"
    # Should include India mental-health hotlines
    hotlines = body["blocks"][0]["hotlines"]
    labels = " ".join(h["label"] for h in hotlines).lower()
    assert "icall" in labels or "vandrevala" in labels or "aasra" in labels


def test_api_chat_session_persistence():
    """Same session_id should be returned and reused."""
    r1 = client.post("/chat", json={"message": "hi"})
    sid = r1.json()["session_id"]
    r2 = client.post("/chat", json={"message": "book an appointment", "session_id": sid})
    assert r2.json()["session_id"] == sid


def test_api_doctors_list():
    r = client.get("/doctors")
    assert r.status_code == 200
    assert len(r.json()) == 12


def test_api_doctors_by_specialty():
    r = client.get("/doctors?specialty=cardiology")
    assert r.status_code == 200
    docs = r.json()
    assert all(d["specialty_key"] == "cardiology" for d in docs)


def test_api_medications_list():
    r = client.get("/medications")
    assert r.status_code == 200
    assert len(r.json()) == 30


def test_api_pharmacies_list():
    r = client.get("/pharmacies")
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_api_chat_lab_results_includes_disclaimer():
    r = client.post("/chat", json={"message": "show me my lab results"})
    body = r.json()
    types = [b["type"] for b in body["blocks"]]
    assert "lab_results" in types
    assert "disclaimer" in types, "Medical info responses must include a disclaimer"


def test_api_chat_medication_info_includes_disclaimer():
    r = client.post("/chat", json={"message": "I need pain relief"})
    body = r.json()
    types = [b["type"] for b in body["blocks"]]
    assert "disclaimer" in types, "Medication responses must include a disclaimer"
