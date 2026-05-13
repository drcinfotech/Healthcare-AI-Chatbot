"""
Healthcare chatbot engine.

Flow:
  1. Safety check first — emergencies & mental-health crises short-circuit
  2. Otherwise, classify intent
  3. Dispatch to handler
  4. Return rich blocks

The engine NEVER:
  • Diagnoses conditions
  • Recommends specific dosages outside what's already in the catalog
  • Tells anyone to discontinue prescribed medication
  • Replaces a doctor's judgment

The engine ALWAYS:
  • Surfaces a disclaimer for medical info responses
  • Routes urgent cases to emergency hotlines
  • Encourages professional consultation
"""
from __future__ import annotations

import secrets
from typing import Optional

from .catalog import catalog
from .intents import Classification, classify
from .safety import check_safety, build_emergency_block, build_mental_health_block
from .sessions import Session


# ─── Block builders ────────────────────────────────────────
def _text(content: str) -> dict:
    return {"type": "text", "content": content}


def _disclaimer(content: str) -> dict:
    return {"type": "disclaimer", "content": content}


def _meds(items: list[dict], title: Optional[str] = None) -> dict:
    return {"type": "medications", "title": title, "items": items}


def _doctors(items: list[dict], title: Optional[str] = None) -> dict:
    return {"type": "doctors", "title": title, "items": items}


def _pharmacies(items: list[dict], title: Optional[str] = None) -> dict:
    return {"type": "pharmacies", "title": title, "items": items}


def _appointment_slots(doctor: dict) -> dict:
    """Build a set of available slots from a doctor record."""
    base_date = doctor.get("next_slot", "Tomorrow, 10:00 AM").split(",")[0].strip()
    slots = []
    for i, time in enumerate(["10:00 AM", "11:30 AM", "2:00 PM", "4:30 PM"]):
        slots.append({
            "slot_id": f"{doctor['id']}-slot-{i+1}",
            "doctor_id": doctor["id"],
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "date_label": base_date,
            "time_label": time,
            "mode": doctor["consultation_modes"][0],
            "fee": doctor["consultation_fee"],
        })
    return {"type": "appointment_slots", "title": f"Available slots — {doctor['name']}", "slots": slots}


def _appointment_confirmed(doctor: dict) -> dict:
    return {
        "type": "appointment_confirmed",
        "appointment": {
            "confirmation_id": "APT-" + secrets.token_hex(4).upper(),
            "doctor_name": doctor["name"],
            "specialty": doctor["specialty"],
            "clinic": doctor["clinic"],
            "date_label": doctor.get("next_slot", "Tomorrow").split(",")[0],
            "time_label": doctor.get("next_slot", "10:00 AM").split(",")[-1].strip(),
            "mode": doctor["consultation_modes"][0],
            "fee": doctor["consultation_fee"],
            "instructions": "Arrive 10 minutes early with photo ID and prior reports. You'll receive an SMS reminder 2 hours before."
        }
    }


def _lab_report() -> dict:
    return {
        "type": "lab_results",
        "report": {
            "report_id": "LAB-2024-08821",
            "date_label": "Nov 28, 2025",
            "lab_name": "Helix Diagnostics",
            "results": [
                {"test": "Hemoglobin",      "value": "13.8", "unit": "g/dL",   "range_label": "12.0 – 16.0",  "status": "normal"},
                {"test": "Total Cholesterol","value": "215", "unit": "mg/dL",  "range_label": "< 200",         "status": "borderline"},
                {"test": "LDL Cholesterol", "value": "138", "unit": "mg/dL",  "range_label": "< 130",         "status": "borderline"},
                {"test": "HDL Cholesterol", "value": "52",  "unit": "mg/dL",  "range_label": "> 40",          "status": "normal"},
                {"test": "Fasting Glucose", "value": "94",  "unit": "mg/dL",  "range_label": "70 – 99",       "status": "normal"},
                {"test": "HbA1c",           "value": "5.4", "unit": "%",      "range_label": "< 5.7",         "status": "normal"},
                {"test": "Vitamin D",       "value": "18",  "unit": "ng/mL",  "range_label": "30 – 100",      "status": "low"},
                {"test": "TSH",             "value": "2.1", "unit": "mIU/L",  "range_label": "0.4 – 4.0",     "status": "normal"},
            ]
        }
    }


def _vaccine_schedule() -> dict:
    return {
        "type": "vaccine_schedule",
        "schedule": {
            "title": "Adult vaccination schedule",
            "events": [
                {"name": "Tetanus booster (Td)",   "due_label": "Completed Mar 2023",  "status": "completed"},
                {"name": "Influenza (annual)",     "due_label": "Due in 2 weeks",      "status": "due_soon"},
                {"name": "COVID-19 booster",       "due_label": "Overdue by 3 months", "status": "overdue"},
                {"name": "Hepatitis B (3rd dose)", "due_label": "Completed Jul 2024",  "status": "completed"},
                {"name": "HPV catch-up",           "due_label": "Recommended",         "status": "upcoming"},
            ]
        }
    }


def _prescriptions() -> dict:
    return {
        "type": "prescriptions",
        "title": "Your active prescriptions",
        "items": [
            {"rx_id": "RX-08821", "medication": "Cardiotone 5",  "prescribed_by": "Dr. Anika Sharma", "refills_remaining": 2, "last_filled": "Nov 12, 2025", "status": "active"},
            {"rx_id": "RX-08822", "medication": "Glycostat M",   "prescribed_by": "Dr. Karim Hassan", "refills_remaining": 0, "last_filled": "Oct 04, 2025", "status": "needs_refill"},
            {"rx_id": "RX-08823", "medication": "VitaPure D3",   "prescribed_by": "Dr. Sara Lee",     "refills_remaining": 5, "last_filled": "Nov 20, 2025", "status": "active"},
        ]
    }


# ─── Intent handlers ───────────────────────────────────────
def _handle_greeting(_session: Session):
    blocks = [_text(
        "Hi, I'm Aira — your health companion. I can help you find doctors, "
        "book appointments, look up medications, check your lab results, manage "
        "prescriptions, and answer general health questions. How can I help today?"
    )]
    suggestions = ["Book a doctor appointment", "What's in my lab results?", "Find a pharmacy near me", "I'm not feeling well"]
    return blocks, suggestions


def _handle_book_appointment(c: Classification, session: Session):
    specialty = c.entities.get("specialty")
    if specialty:
        candidates = catalog.doctors_by_specialty(specialty, limit=3)
        intro = f"Here are top-rated {candidates[0]['specialty'].lower()} specialists. Pick one to see available slots:"
    else:
        candidates = catalog.doctors_general(limit=3)
        intro = "Here are highly-rated doctors available soon. Pick one to see available slots:"

    if not candidates:
        candidates = catalog.doctors_general(limit=3)

    session.last_doctors_shown = [d["id"] for d in candidates]
    blocks = [_text(intro), _doctors(candidates)]
    suggestions = ["Book the first one", "Show video consult only", "Different specialty", "Cancel"]
    return blocks, suggestions


def _handle_find_doctor(c: Classification, session: Session):
    return _handle_book_appointment(c, session)


def _handle_symptom_check(c: Classification, session: Session):
    symptoms = c.entities.get("symptoms") or []
    sym_text = ", ".join(symptoms) if symptoms else "what you described"

    blocks = [
        _text(
            f"I hear you mentioned **{sym_text}**. I can't diagnose, but I can help "
            "you take the right next step. Symptoms that are sudden, severe, or paired "
            "with high fever, chest pain, breathing trouble, or confusion need urgent care."
        ),
        _disclaimer(
            "I'm an AI assistant, not a medical professional. The information I share is "
            "general and shouldn't replace advice from your doctor."
        ),
        _text("Would you like to see general physicians available today, or skip ahead to a specialist?"),
    ]
    # Surface a couple of GP options
    gps = [d for d in catalog.all_doctors() if d["specialty_key"] == "general"][:2]
    if gps:
        blocks.append(_doctors(gps, title="General physicians available"))
        session.last_doctors_shown = [d["id"] for d in gps]
    suggestions = ["Book the first GP", "Find a specialist", "Video consult", "What should I watch for?"]
    return blocks, suggestions


def _handle_medication_info(c: Classification, session: Session):
    name = c.entities.get("med_name")
    if name:
        med = catalog.find_med_by_name(name)
        if med:
            session.last_meds_shown = [med["id"]]
            return [
                _text(f"Here's general information about **{med['name']}**:"),
                _meds([med]),
                _disclaimer(
                    "Information shown is general and for awareness only. Always follow your doctor's or "
                    "pharmacist's instructions. Don't start, stop, or change medications without their advice."
                ),
            ], ["Find this nearby", "Cheaper alternatives", "Talk to a pharmacist", "Set a reminder"]

    # Fall back to category search
    category = c.entities.get("med_category")
    if category:
        items = catalog.meds_by_category(category, limit=3)
        if items:
            session.last_meds_shown = [m["id"] for m in items]
            cat_label = items[0]["category_label"]
            return [
                _text(f"Here are some {cat_label.lower()} options. I'm showing general information only — your pharmacist can guide you on the best fit for you."),
                _meds(items),
                _disclaimer("Don't self-prescribe. For prescription-only items, you'll need a valid prescription."),
            ], ["Find the first nearby", "Talk to a pharmacist", "See a doctor", "OTC vs prescription?"]

    # Otherwise generic help
    return [
        _text(
            "I can share general info on common medications — pain relief, allergies, "
            "vitamins, digestive aids, and more. What are you looking for?"
        )
    ], ["Pain relief options", "Allergy medications", "Vitamins & supplements", "Talk to a pharmacist"]


def _handle_medication_search(c: Classification, session: Session):
    return _handle_medication_info(c, session)


def _handle_prescription_refill(_c: Classification, _session: Session):
    blocks = [
        _text("Sure — here are your prescriptions. The one marked **'Needs refill'** is ready to reorder:"),
        _prescriptions(),
        _text("Want me to send the refill to your usual pharmacy, or pick a different one?"),
    ]
    return blocks, ["Refill at usual pharmacy", "Pick a different pharmacy", "Refill all eligible", "Talk to a pharmacist"]


def _handle_prescription_status(_c: Classification, _session: Session):
    blocks = [
        _text("Here are your active prescriptions on file:"),
        _prescriptions(),
        _disclaimer("If anything here looks wrong or outdated, please confirm with your prescribing doctor before making changes."),
    ]
    return blocks, ["Refill the ones I need", "Add a new prescription", "Talk to my doctor", "Set reminders"]


def _handle_lab_results(_c: Classification, _session: Session):
    blocks = [
        _text("Here's your most recent lab report. I've flagged values outside the reference range:"),
        _lab_report(),
        _disclaimer(
            "These results are for informational reference. Your doctor will interpret them in the "
            "context of your full health history. Please discuss flagged values with them."
        ),
        _text("Want me to book a follow-up with a doctor to discuss the borderline cholesterol and low vitamin D?"),
    ]
    return blocks, ["Book a follow-up", "Explain HbA1c", "Compare to last report", "Download PDF"]


def _handle_vaccine_info(_c: Classification, _session: Session):
    blocks = [
        _text("Here's your vaccination summary. You have one overdue and one due soon:"),
        _vaccine_schedule(),
        _disclaimer("Your doctor or pharmacist can confirm what's appropriate for your age, conditions, and travel plans."),
        _text("Want me to find a pharmacy that offers walk-in vaccinations?"),
    ]
    return blocks, ["Find vaccination pharmacy", "Book a vaccine appointment", "Why is this recommended?", "Travel vaccines"]


def _handle_pharmacy_locator(_c: Classification, session: Session):
    pharmacies = catalog.pharmacies(limit=3)
    blocks = [
        _text("Here are the closest pharmacies based on your location. Two are open right now and deliver:"),
        _pharmacies(pharmacies),
    ]
    return blocks, ["Order delivery", "Call the closest one", "24-hour pharmacies", "Get directions"]


def _handle_insurance_info(_c: Classification, _session: Session):
    blocks = [
        _text(
            "I can help you check what's covered. Most plans cover doctor consultations, "
            "lab tests, and prescription medications, with co-pays varying by tier."
        ),
        _disclaimer("For exact coverage details, I'd recommend checking your policy document or calling your insurance provider directly."),
        _text("Would you like me to send a cashless pre-authorization for an upcoming appointment, or help you understand a claim?"),
    ]
    return blocks, ["Cashless pre-auth", "Help with a claim", "Find network hospitals", "Talk to a human"]


def _handle_video_consult(_c: Classification, session: Session):
    video_doctors = [d for d in catalog.all_doctors() if "Video" in d["consultation_modes"]][:3]
    session.last_doctors_shown = [d["id"] for d in video_doctors]
    blocks = [
        _text("Here are doctors available for video consult. You can connect within minutes from your phone or laptop:"),
        _doctors(video_doctors),
        _disclaimer("Video consults are great for follow-ups, common symptoms, and prescriptions — but in-person care is better for physical exams or anything urgent."),
    ]
    return blocks, ["Book first available", "Try a different specialty", "How does video consult work?", "Switch to in-person"]


def _handle_mental_health_general(_c: Classification, _session: Session):
    """
    For NON-CRISIS mental health queries (stressed, anxious, etc.).
    Crisis-level concerns are caught in safety.py before reaching here.
    """
    psychiatrists = [d for d in catalog.all_doctors() if d["specialty_key"] == "psychiatry"][:2]
    blocks = [
        _text(
            "Thanks for sharing — what you're feeling is more common than people realize, "
            "and reaching out is a strong step. Talking to a professional can really help."
        ),
        _doctors(psychiatrists, title="Mental health specialists"),
        _text(
            "If you ever feel like you can't cope or are having thoughts of hurting yourself, "
            "please call **iCall (+91-9152987821)** or **Vandrevala Foundation (1860-2662-345)** — "
            "both are free, confidential, and 24/7."
        ),
        _disclaimer("I'm an AI assistant. For ongoing care, working with a qualified therapist or psychiatrist is the right path."),
    ]
    return blocks, ["Book a session", "Try a guided breathing exercise", "Self-care resources", "Talk to a human"]


def _handle_talk_to_human(_c: Classification, _session: Session):
    blocks = [_text(
        "Of course — I can connect you to a nurse on call. Typical wait time is about 3 minutes. "
        "If your concern is about a specific prescription, a pharmacist is also available. Which would you prefer?"
    )]
    return blocks, ["Talk to a nurse", "Talk to a pharmacist", "Schedule a callback", "Wait for a doctor"]


def _handle_thanks(_session: Session):
    return [_text("You're welcome. Take care, and don't hesitate to come back if you have more questions.")], \
           ["Book an appointment", "Check my prescriptions", "View lab results"]


def _handle_goodbye(_session: Session):
    return [_text("Take care of yourself. I'm here whenever you need me. 💙")], []


def _handle_unknown(_c: Classification, _session: Session):
    blocks = [
        _text(
            "I'm not sure I caught that. I'm best at helping with appointments, doctors, "
            "medications, lab results, prescriptions, and pharmacies. Could you rephrase, "
            "or pick from the options below?"
        )
    ]
    return blocks, ["Book an appointment", "Find a pharmacy", "View my prescriptions", "Talk to a human"]


# ─── Engine ────────────────────────────────────────────────
class ChatbotEngine:
    def respond(self, message: str, session: Session) -> dict:
        # 1️⃣ Safety check first
        safety = check_safety(message)
        if safety.flag == "emergency":
            return {
                "session_id": session.session_id,
                "intent": "emergency",
                "confidence": 1.0,
                "blocks": [build_emergency_block()],
                "suggestions": ["Call 112 now", "Call 108 ambulance", "Talk to a human"],
                "safety_flag": "emergency",
            }
        if safety.flag == "mental_health":
            return {
                "session_id": session.session_id,
                "intent": "mental_health_crisis",
                "confidence": 1.0,
                "blocks": [build_mental_health_block()],
                "suggestions": ["Call iCall now", "Talk to a psychiatrist", "I want to keep talking"],
                "safety_flag": "mental_health",
            }

        # 2️⃣ Classify intent
        med_names = catalog.med_names()
        c = classify(message, known_med_names=med_names)
        session.last_intent = c.intent
        session.history.append({"role": "user", "text": message})

        handler_map = {
            "greeting":              lambda: _handle_greeting(session),
            "goodbye":               lambda: _handle_goodbye(session),
            "thanks":                lambda: _handle_thanks(session),
            "book_appointment":      lambda: _handle_book_appointment(c, session),
            "find_doctor":           lambda: _handle_find_doctor(c, session),
            "symptom_check":         lambda: _handle_symptom_check(c, session),
            "medication_info":       lambda: _handle_medication_info(c, session),
            "medication_search":     lambda: _handle_medication_search(c, session),
            "prescription_refill":   lambda: _handle_prescription_refill(c, session),
            "prescription_status":   lambda: _handle_prescription_status(c, session),
            "lab_results":           lambda: _handle_lab_results(c, session),
            "vaccine_info":          lambda: _handle_vaccine_info(c, session),
            "pharmacy_locator":      lambda: _handle_pharmacy_locator(c, session),
            "insurance_info":        lambda: _handle_insurance_info(c, session),
            "video_consult":         lambda: _handle_video_consult(c, session),
            "mental_health_general": lambda: _handle_mental_health_general(c, session),
            "talk_to_human":         lambda: _handle_talk_to_human(c, session),
        }

        handler = handler_map.get(c.intent, lambda: _handle_unknown(c, session))
        blocks, suggestions = handler()

        # Record bot text for history
        bot_text = " | ".join(b.get("content", "") for b in blocks if b.get("type") == "text")
        session.history.append({"role": "bot", "text": bot_text})

        return {
            "session_id": session.session_id,
            "intent": c.intent,
            "confidence": c.confidence,
            "blocks": blocks,
            "suggestions": suggestions,
            "safety_flag": None,
        }


engine = ChatbotEngine()
