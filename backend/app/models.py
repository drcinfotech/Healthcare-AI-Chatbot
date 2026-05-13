"""
Pydantic models for the healthcare chatbot API.
"""
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


# ─── Request ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None


# ─── Domain entities ───────────────────────────────────────
class Medication(BaseModel):
    id: str
    name: str
    category: str
    category_label: str
    type: str
    form: str
    uses: str
    common_dosing: str
    side_effects: list[str]
    warnings: list[str]
    interactions: list[str]
    price: int
    currency: str
    stock: int
    image: str


class Doctor(BaseModel):
    id: str
    name: str
    specialty: str
    specialty_key: str
    qualifications: str
    experience_years: int
    languages: list[str]
    clinic: str
    city: str
    rating: float
    reviews: int
    next_slot: str
    consultation_fee: int
    currency: str
    image: str
    available_today: bool
    consultation_modes: list[str]


class Pharmacy(BaseModel):
    id: str
    name: str
    address: str
    phone: str
    open_now: bool
    hours: str
    distance_km: float
    rating: float
    reviews: int
    services: list[str]
    delivery_available: bool
    delivery_eta_mins: Optional[int] = None


class AppointmentSlot(BaseModel):
    slot_id: str
    doctor_id: str
    doctor_name: str
    specialty: str
    date_label: str
    time_label: str
    mode: str  # In-person | Video
    fee: int


class Appointment(BaseModel):
    confirmation_id: str
    doctor_name: str
    specialty: str
    clinic: str
    date_label: str
    time_label: str
    mode: str
    fee: int
    instructions: str


class LabResult(BaseModel):
    test: str
    value: str
    unit: str
    range_label: str
    status: Literal["normal", "high", "low", "borderline"]


class LabReport(BaseModel):
    report_id: str
    date_label: str
    lab_name: str
    results: list[LabResult]


class VaccineEvent(BaseModel):
    name: str
    due_label: str
    status: Literal["completed", "due_soon", "overdue", "upcoming"]


class VaccineSchedule(BaseModel):
    title: str
    events: list[VaccineEvent]


class Prescription(BaseModel):
    rx_id: str
    medication: str
    prescribed_by: str
    refills_remaining: int
    last_filled: str
    status: Literal["active", "needs_refill", "expired"]


# ─── Rich message blocks ───────────────────────────────────
class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    content: str


class MedicationsBlock(BaseModel):
    type: Literal["medications"] = "medications"
    title: Optional[str] = None
    items: list[Medication]


class DoctorsBlock(BaseModel):
    type: Literal["doctors"] = "doctors"
    title: Optional[str] = None
    items: list[Doctor]


class PharmaciesBlock(BaseModel):
    type: Literal["pharmacies"] = "pharmacies"
    title: Optional[str] = None
    items: list[Pharmacy]


class AppointmentSlotsBlock(BaseModel):
    type: Literal["appointment_slots"] = "appointment_slots"
    title: Optional[str] = None
    slots: list[AppointmentSlot]


class AppointmentConfirmedBlock(BaseModel):
    type: Literal["appointment_confirmed"] = "appointment_confirmed"
    appointment: Appointment


class LabResultsBlock(BaseModel):
    type: Literal["lab_results"] = "lab_results"
    report: LabReport


class VaccineScheduleBlock(BaseModel):
    type: Literal["vaccine_schedule"] = "vaccine_schedule"
    schedule: VaccineSchedule


class PrescriptionsBlock(BaseModel):
    type: Literal["prescriptions"] = "prescriptions"
    title: Optional[str] = None
    items: list[Prescription]


class EmergencyBlock(BaseModel):
    type: Literal["emergency"] = "emergency"
    headline: str
    message: str
    hotlines: list[dict]   # [{label, number}]


class DisclaimerBlock(BaseModel):
    type: Literal["disclaimer"] = "disclaimer"
    content: str


MessageBlock = (
    TextBlock | MedicationsBlock | DoctorsBlock | PharmaciesBlock
    | AppointmentSlotsBlock | AppointmentConfirmedBlock
    | LabResultsBlock | VaccineScheduleBlock | PrescriptionsBlock
    | EmergencyBlock | DisclaimerBlock
)


# ─── Response ──────────────────────────────────────────────
class ChatResponse(BaseModel):
    session_id: str
    intent: str
    confidence: float
    blocks: list[MessageBlock]
    suggestions: list[str] = []
    safety_flag: Optional[str] = None  # None | "emergency" | "mental_health"
