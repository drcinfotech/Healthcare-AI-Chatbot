"""
Data catalog — loads medications, doctors, and pharmacies from JSON.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


DATA_DIR = Path(__file__).parent.parent / "data"


class Catalog:
    def __init__(self):
        with open(DATA_DIR / "medications.json", "r", encoding="utf-8") as f:
            self._meds: list[dict] = json.load(f)
        with open(DATA_DIR / "doctors.json", "r", encoding="utf-8") as f:
            self._doctors: list[dict] = json.load(f)
        with open(DATA_DIR / "pharmacies.json", "r", encoding="utf-8") as f:
            self._pharmacies: list[dict] = json.load(f)

        self._meds_by_id = {m["id"]: m for m in self._meds}
        self._doctors_by_id = {d["id"]: d for d in self._doctors}

    # ── Medications ────────────────────────────────────
    def all_meds(self) -> list[dict]:
        return list(self._meds)

    def med(self, mid: str) -> Optional[dict]:
        return self._meds_by_id.get(mid)

    def med_names(self) -> list[str]:
        return [m["name"] for m in self._meds]

    def find_med_by_name(self, name: str) -> Optional[dict]:
        n = name.lower()
        for m in self._meds:
            if m["name"].lower() == n:
                return m
        # Loose match
        for m in self._meds:
            if n in m["name"].lower():
                return m
        return None

    def meds_by_category(self, category: str, limit: int = 3) -> list[dict]:
        out = [m for m in self._meds if m["category"] == category]
        out.sort(key=lambda m: -m["stock"])    # prefer in-stock first
        return out[:limit]

    # ── Doctors ────────────────────────────────────────
    def all_doctors(self) -> list[dict]:
        return list(self._doctors)

    def doctor(self, did: str) -> Optional[dict]:
        return self._doctors_by_id.get(did)

    def doctors_by_specialty(self, specialty_key: str, limit: int = 3) -> list[dict]:
        out = [d for d in self._doctors if d["specialty_key"] == specialty_key]
        out.sort(key=lambda d: (-int(d["available_today"]), -d["rating"]))
        return out[:limit]

    def doctors_general(self, limit: int = 3) -> list[dict]:
        out = sorted(
            self._doctors,
            key=lambda d: (-int(d["available_today"]), -d["rating"], -d["reviews"]),
        )
        return out[:limit]

    # ── Pharmacies ─────────────────────────────────────
    def pharmacies(self, limit: int = 3) -> list[dict]:
        # Sort by open + distance
        out = sorted(
            self._pharmacies,
            key=lambda p: (not p["open_now"], p["distance_km"]),
        )
        return out[:limit]


catalog = Catalog()
