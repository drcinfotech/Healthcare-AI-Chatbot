"""
FastAPI entry point for the Healthcare AI Chatbot.

Routes:
  POST /chat              Main chat endpoint
  GET  /doctors           Browse the doctor directory
  GET  /medications       Browse the medication catalog
  GET  /pharmacies        Nearby pharmacies
  GET  /health            Liveness check
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.catalog import catalog
from app.chatbot import engine
from app.models import ChatRequest, ChatResponse
from app.sessions import store

app = FastAPI(
    title="Healthcare AI Chatbot",
    description=(
        "A demo conversational AI for healthcare, medical, and pharmacy services. "
        "Includes intent classification, safety guardrails (emergency & mental health "
        "crisis detection), and rich response blocks for appointments, prescriptions, "
        "lab results, and more. NOT a substitute for medical advice."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "medications": len(catalog.all_meds()),
        "doctors": len(catalog.all_doctors()),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = store.get_or_create(req.session_id)
    return engine.respond(req.message, session)


@app.get("/doctors")
def list_doctors(specialty: str | None = None, limit: int = 20):
    if specialty:
        return catalog.doctors_by_specialty(specialty, limit=limit)
    return catalog.all_doctors()[:limit]


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    d = catalog.doctor(doctor_id)
    if not d:
        raise HTTPException(404, f"Doctor {doctor_id} not found")
    return d


@app.get("/medications")
def list_medications(category: str | None = None, limit: int = 30):
    if category:
        return catalog.meds_by_category(category, limit=limit)
    return catalog.all_meds()[:limit]


@app.get("/medications/{med_id}")
def get_medication(med_id: str):
    m = catalog.med(med_id)
    if not m:
        raise HTTPException(404, f"Medication {med_id} not found")
    return m


@app.get("/pharmacies")
def list_pharmacies(limit: int = 10):
    return catalog.pharmacies(limit=limit)


@app.get("/")
def root():
    return {
        "name": "Healthcare AI Chatbot",
        "version": app.version,
        "docs": "/docs",
        "disclaimer": "This is a demo. Not a substitute for medical advice.",
    }
