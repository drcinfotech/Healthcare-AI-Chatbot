import {
  AlertTriangle, Phone, Stethoscope, Pill, MapPin, Calendar, Clock,
  Star, CheckCircle2, Video, Building2, ShieldAlert, Info,
  Activity, Syringe, FileText, ChevronRight, AlertCircle, Truck,
} from "lucide-react";

const ACCENT = "#5EEAD4";

/* ─── TextBlock ────────────────────────────────────────── */
export function TextBlock({ content }) {
  // Render **bold** inline
  const parts = content.split(/(\*\*[^*]+\*\*)/g);
  return (
    <div
      className="text-sm leading-relaxed px-4 py-2.5 rounded-2xl rounded-tl-md"
      style={{ background: "rgba(255,255,255,0.03)", color: "rgba(255,255,255,0.88)" }}
    >
      {parts.map((p, i) =>
        p.startsWith("**") && p.endsWith("**") ? (
          <strong key={i} className="text-white font-medium">{p.slice(2, -2)}</strong>
        ) : (
          <span key={i}>{p}</span>
        )
      )}
    </div>
  );
}

/* ─── DisclaimerBlock ──────────────────────────────────── */
export function DisclaimerBlock({ content }) {
  return (
    <div
      className="flex items-start gap-2.5 px-4 py-2.5 rounded-2xl border"
      style={{
        background: "rgba(250, 204, 21, 0.04)",
        borderColor: "rgba(250, 204, 21, 0.18)",
        color: "rgba(250, 204, 21, 0.85)",
      }}
    >
      <Info size={14} className="mt-0.5 flex-shrink-0" />
      <div className="text-11 leading-relaxed">{content}</div>
    </div>
  );
}

/* ─── EmergencyBlock (highest priority UI) ─────────────── */
export function EmergencyBlock({ headline, message, hotlines }) {
  return (
    <div
      className="rounded-2xl border-2 p-4 emergency-pulse"
      style={{
        background: "linear-gradient(180deg, rgba(248,113,113,0.10), rgba(248,113,113,0.02))",
        borderColor: "rgba(248,113,113,0.4)",
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle size={18} style={{ color: "#fca5a5" }} />
        <div className="text-sm font-semibold" style={{ color: "#fca5a5" }}>{headline}</div>
      </div>
      <div className="text-xs leading-relaxed mb-3" style={{ color: "rgba(255,255,255,0.85)" }}>
        {message}
      </div>
      <div className="space-y-1.5">
        {hotlines.map((h, i) => (
          <a
            key={i}
            href={`tel:${h.number.replace(/[^+0-9]/g, "")}`}
            className="flex items-center justify-between px-3 py-2 rounded-lg border transition hover:bg-white/5"
            style={{
              background: "rgba(255,255,255,0.04)",
              borderColor: "rgba(248,113,113,0.25)",
            }}
          >
            <div className="flex items-center gap-2">
              <Phone size={12} style={{ color: "#fca5a5" }} />
              <span className="text-xs" style={{ color: "rgba(255,255,255,0.85)" }}>{h.label}</span>
            </div>
            <span className="text-xs font-mono font-medium" style={{ color: "#fca5a5" }}>{h.number}</span>
          </a>
        ))}
      </div>
    </div>
  );
}

/* ─── DoctorsBlock ─────────────────────────────────────── */
export function DoctorsBlock({ title, items }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>
          {title}
        </div>
      )}
      <div className="space-y-2">
        {items.map((d) => (
          <div
            key={d.id}
            className="rounded-xl p-3 border"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
          >
            <div className="flex items-start gap-3">
              <div
                className="rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ width: 44, height: 44, background: ACCENT + "14", fontSize: 22 }}
              >
                {d.image}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-0.5">
                  <div className="text-sm font-medium truncate" style={{ color: "rgba(255,255,255,0.92)" }}>
                    {d.name}
                  </div>
                  {d.available_today && (
                    <span
                      className="text-9 px-1.5 py-0.5 rounded-full font-medium flex-shrink-0"
                      style={{ background: ACCENT + "22", color: ACCENT }}
                    >
                      AVAILABLE TODAY
                    </span>
                  )}
                </div>
                <div className="text-11 mb-1" style={{ color: "rgba(255,255,255,0.55)" }}>
                  {d.specialty} · {d.qualifications} · {d.experience_years}y exp
                </div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex items-center gap-1">
                    <Star size={9} fill={ACCENT} stroke="none" />
                    <span className="text-10" style={{ color: "rgba(255,255,255,0.65)" }}>
                      {d.rating} · {d.reviews.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Building2 size={9} style={{ color: "rgba(255,255,255,0.5)" }} />
                    <span className="text-10 truncate" style={{ color: "rgba(255,255,255,0.55)" }}>
                      {d.clinic}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between gap-2 pt-2 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1">
                      <Clock size={10} style={{ color: ACCENT }} />
                      <span className="text-10" style={{ color: "rgba(255,255,255,0.7)" }}>{d.next_slot}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {d.consultation_modes.includes("Video") && (
                        <Video size={10} style={{ color: "rgba(255,255,255,0.5)" }} />
                      )}
                      <span className="text-10 font-medium" style={{ color: "rgba(255,255,255,0.9)" }}>
                        ₹{d.consultation_fee}
                      </span>
                    </div>
                  </div>
                  <button
                    className="flex items-center gap-1 text-10 font-medium px-2.5 py-1 rounded-md"
                    style={{ background: ACCENT, color: "#0A0A0A" }}
                  >
                    Book <ChevronRight size={10} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── MedicationsBlock ─────────────────────────────────── */
export function MedicationsBlock({ title, items }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>
          {title}
        </div>
      )}
      <div className="space-y-2">
        {items.map((m) => {
          const isRx = m.form === "Prescription";
          const inStock = m.stock > 0;
          return (
            <div
              key={m.id}
              className="rounded-xl p-3 border"
              style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
            >
              <div className="flex items-start gap-3">
                <div
                  className="rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ width: 44, height: 44, background: ACCENT + "14", fontSize: 22 }}
                >
                  {m.image}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-0.5">
                    <div className="text-sm font-medium truncate" style={{ color: "rgba(255,255,255,0.92)" }}>
                      {m.name}
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <span
                        className="text-9 px-1.5 py-0.5 rounded-full font-medium"
                        style={{
                          background: isRx ? "rgba(248,113,113,0.15)" : ACCENT + "22",
                          color:      isRx ? "#fca5a5"               : ACCENT,
                        }}
                      >
                        {isRx ? "Rx" : "OTC"}
                      </span>
                      <span
                        className="text-9 px-1.5 py-0.5 rounded-full font-medium"
                        style={{
                          background: inStock ? "rgba(74,222,128,0.15)" : "rgba(255,255,255,0.06)",
                          color:      inStock ? "#86efac"               : "rgba(255,255,255,0.4)",
                        }}
                      >
                        {inStock ? "IN STOCK" : "OUT OF STOCK"}
                      </span>
                    </div>
                  </div>
                  <div className="text-11 mb-1.5" style={{ color: "rgba(255,255,255,0.55)" }}>
                    {m.category_label} · {m.type}
                  </div>
                  <div className="text-11 mb-1.5" style={{ color: "rgba(255,255,255,0.7)" }}>
                    <span style={{ color: "rgba(255,255,255,0.45)" }}>Used for: </span>
                    {m.uses}
                  </div>
                  <div className="text-10 mb-2" style={{ color: "rgba(255,255,255,0.55)" }}>
                    <span style={{ color: "rgba(255,255,255,0.4)" }}>Dosing: </span>
                    {m.common_dosing}
                  </div>
                  {m.warnings && m.warnings.length > 0 && (
                    <div className="flex items-start gap-1.5 mb-2">
                      <AlertCircle size={10} style={{ color: "#fbbf24", marginTop: 2 }} />
                      <div className="text-10" style={{ color: "rgba(251,191,36,0.85)" }}>
                        {m.warnings.join(" · ")}
                      </div>
                    </div>
                  )}
                  <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
                    <div className="text-sm font-semibold" style={{ color: "white" }}>
                      ₹{m.price.toLocaleString("en-IN")}
                    </div>
                    <button
                      className="flex items-center gap-1 text-10 font-medium px-2.5 py-1 rounded-md"
                      style={{
                        background: inStock ? ACCENT : "rgba(255,255,255,0.08)",
                        color:      inStock ? "#0A0A0A" : "rgba(255,255,255,0.4)",
                        cursor:     inStock ? "pointer" : "not-allowed",
                      }}
                      disabled={!inStock}
                    >
                      {inStock ? "Find nearby" : "Notify when in stock"} <ChevronRight size={10} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── PharmaciesBlock ──────────────────────────────────── */
export function PharmaciesBlock({ title, items }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>
          {title}
        </div>
      )}
      <div className="space-y-2">
        {items.map((p) => (
          <div
            key={p.id}
            className="rounded-xl p-3 border"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
          >
            <div className="flex items-start gap-3">
              <div
                className="rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ width: 44, height: 44, background: ACCENT + "14" }}
              >
                <MapPin size={18} style={{ color: ACCENT }} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-0.5">
                  <div className="text-sm font-medium truncate" style={{ color: "rgba(255,255,255,0.92)" }}>
                    {p.name}
                  </div>
                  <span
                    className="text-9 px-1.5 py-0.5 rounded-full font-medium flex-shrink-0"
                    style={{
                      background: p.open_now ? "rgba(74,222,128,0.15)" : "rgba(248,113,113,0.15)",
                      color:      p.open_now ? "#86efac"               : "#fca5a5",
                    }}
                  >
                    {p.open_now ? "OPEN NOW" : "CLOSED"}
                  </span>
                </div>
                <div className="text-11 mb-1" style={{ color: "rgba(255,255,255,0.55)" }}>
                  {p.address}
                </div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex items-center gap-1">
                    <Clock size={9} style={{ color: "rgba(255,255,255,0.5)" }} />
                    <span className="text-10" style={{ color: "rgba(255,255,255,0.6)" }}>{p.hours}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star size={9} fill={ACCENT} stroke="none" />
                    <span className="text-10" style={{ color: "rgba(255,255,255,0.6)" }}>{p.rating}</span>
                  </div>
                  <div className="text-10" style={{ color: "rgba(255,255,255,0.6)" }}>
                    {p.distance_km} km away
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
                  <div className="flex items-center gap-2">
                    {p.delivery_available && (
                      <div className="flex items-center gap-1">
                        <Truck size={10} style={{ color: ACCENT }} />
                        <span className="text-10" style={{ color: ACCENT }}>
                          Delivery {p.delivery_eta_mins}min
                        </span>
                      </div>
                    )}
                  </div>
                  <button
                    className="flex items-center gap-1 text-10 font-medium px-2.5 py-1 rounded-md"
                    style={{ background: ACCENT, color: "#0A0A0A" }}
                  >
                    {p.delivery_available ? "Order" : "Directions"} <ChevronRight size={10} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── LabResultsBlock ──────────────────────────────────── */
export function LabResultsBlock({ report }) {
  const statusColor = {
    normal:     { bg: "rgba(74,222,128,0.15)",  text: "#86efac"  },
    high:       { bg: "rgba(248,113,113,0.15)", text: "#fca5a5" },
    low:        { bg: "rgba(248,113,113,0.15)", text: "#fca5a5" },
    borderline: { bg: "rgba(250,204,21,0.15)",  text: "#fde047"  },
  };
  return (
    <div
      className="rounded-xl p-4 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <FileText size={14} style={{ color: ACCENT }} />
          <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>
            Lab Report · {report.report_id}
          </div>
        </div>
        <div className="text-10" style={{ color: "rgba(255,255,255,0.45)" }}>
          {report.date_label} · {report.lab_name}
        </div>
      </div>
      <div className="space-y-1.5">
        {report.results.map((r, i) => {
          const c = statusColor[r.status] || statusColor.normal;
          return (
            <div
              key={i}
              className="flex items-center justify-between px-3 py-2 rounded-md"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <div className="flex-1 min-w-0">
                <div className="text-xs" style={{ color: "rgba(255,255,255,0.85)" }}>{r.test}</div>
                <div className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.4)" }}>
                  Ref: {r.range_label}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-xs font-mono font-medium" style={{ color: "white" }}>
                  {r.value} <span style={{ color: "rgba(255,255,255,0.4)" }}>{r.unit}</span>
                </div>
                <span
                  className="text-9 px-1.5 py-0.5 rounded-full font-medium uppercase"
                  style={{ background: c.bg, color: c.text }}
                >
                  {r.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── VaccineScheduleBlock ─────────────────────────────── */
export function VaccineScheduleBlock({ schedule }) {
  const statusColor = {
    completed: { bg: "rgba(74,222,128,0.15)",  text: "#86efac" },
    due_soon:  { bg: "rgba(250,204,21,0.15)",  text: "#fde047" },
    overdue:   { bg: "rgba(248,113,113,0.15)", text: "#fca5a5" },
    upcoming:  { bg: "rgba(255,255,255,0.06)", text: "rgba(255,255,255,0.6)" },
  };
  const statusLabel = {
    completed: "DONE", due_soon: "DUE SOON", overdue: "OVERDUE", upcoming: "RECOMMENDED",
  };
  return (
    <div
      className="rounded-xl p-4 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
    >
      <div className="flex items-center gap-2 mb-3">
        <Syringe size={14} style={{ color: ACCENT }} />
        <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>
          {schedule.title}
        </div>
      </div>
      <div className="space-y-1.5">
        {schedule.events.map((e, i) => {
          const c = statusColor[e.status] || statusColor.upcoming;
          return (
            <div
              key={i}
              className="flex items-center justify-between px-3 py-2 rounded-md"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <div>
                <div className="text-xs" style={{ color: "rgba(255,255,255,0.85)" }}>{e.name}</div>
                <div className="text-10" style={{ color: "rgba(255,255,255,0.45)" }}>{e.due_label}</div>
              </div>
              <span
                className="text-9 px-1.5 py-0.5 rounded-full font-medium"
                style={{ background: c.bg, color: c.text }}
              >
                {statusLabel[e.status]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── PrescriptionsBlock ───────────────────────────────── */
export function PrescriptionsBlock({ title, items }) {
  const statusColor = {
    active:        { bg: "rgba(74,222,128,0.15)",  text: "#86efac"  },
    needs_refill:  { bg: "rgba(250,204,21,0.15)",  text: "#fde047"  },
    expired:       { bg: "rgba(248,113,113,0.15)", text: "#fca5a5" },
  };
  const statusLabel = { active: "ACTIVE", needs_refill: "NEEDS REFILL", expired: "EXPIRED" };
  return (
    <div
      className="rounded-xl p-4 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
    >
      {title && (
        <div className="flex items-center gap-2 mb-3">
          <Pill size={14} style={{ color: ACCENT }} />
          <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>
            {title}
          </div>
        </div>
      )}
      <div className="space-y-1.5">
        {items.map((p) => {
          const c = statusColor[p.status] || statusColor.active;
          return (
            <div
              key={p.rx_id}
              className="flex items-center justify-between px-3 py-2 rounded-md"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium truncate" style={{ color: "rgba(255,255,255,0.9)" }}>
                  {p.medication}
                </div>
                <div className="text-10" style={{ color: "rgba(255,255,255,0.45)" }}>
                  {p.rx_id} · {p.prescribed_by} · last filled {p.last_filled}
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <div className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.6)" }}>
                  {p.refills_remaining} refills left
                </div>
                <span
                  className="text-9 px-1.5 py-0.5 rounded-full font-medium"
                  style={{ background: c.bg, color: c.text }}
                >
                  {statusLabel[p.status]}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── AppointmentSlotsBlock ────────────────────────────── */
export function AppointmentSlotsBlock({ title, slots }) {
  return (
    <div
      className="rounded-xl p-3 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
    >
      {title && (
        <div className="text-10 uppercase tracking-tightest2 mb-2.5" style={{ color: "rgba(255,255,255,0.4)" }}>
          {title}
        </div>
      )}
      <div className="grid grid-cols-2 gap-1.5">
        {slots.map((s) => (
          <button
            key={s.slot_id}
            className="flex items-center justify-between px-3 py-2 rounded-lg border text-left"
            style={{ background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.08)" }}
          >
            <div>
              <div className="text-11" style={{ color: "rgba(255,255,255,0.5)" }}>{s.date_label}</div>
              <div className="text-xs font-medium" style={{ color: "white" }}>{s.time_label}</div>
            </div>
            <Calendar size={12} style={{ color: ACCENT }} />
          </button>
        ))}
      </div>
    </div>
  );
}

/* ─── AppointmentConfirmedBlock ────────────────────────── */
export function AppointmentConfirmedBlock({ appointment }) {
  const a = appointment;
  return (
    <div
      className="rounded-xl p-4 border-2"
      style={{
        background: "linear-gradient(180deg, rgba(94,234,212,0.10), rgba(94,234,212,0.02))",
        borderColor: ACCENT + "44",
      }}
    >
      <div className="flex items-center gap-2 mb-3">
        <CheckCircle2 size={16} style={{ color: ACCENT }} />
        <div className="text-sm font-medium" style={{ color: "white" }}>Appointment confirmed</div>
        <span className="text-10 font-mono ml-auto" style={{ color: ACCENT }}>{a.confirmation_id}</span>
      </div>
      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          <Stethoscope size={11} style={{ color: "rgba(255,255,255,0.5)" }} />
          <div className="text-xs" style={{ color: "rgba(255,255,255,0.9)" }}>
            {a.doctor_name} <span style={{ color: "rgba(255,255,255,0.5)" }}>· {a.specialty}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Calendar size={11} style={{ color: "rgba(255,255,255,0.5)" }} />
          <div className="text-xs" style={{ color: "rgba(255,255,255,0.9)" }}>
            {a.date_label} at {a.time_label}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {a.mode === "Video" ? (
            <Video size={11} style={{ color: "rgba(255,255,255,0.5)" }} />
          ) : (
            <Building2 size={11} style={{ color: "rgba(255,255,255,0.5)" }} />
          )}
          <div className="text-xs" style={{ color: "rgba(255,255,255,0.9)" }}>
            {a.mode} · {a.clinic}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Activity size={11} style={{ color: "rgba(255,255,255,0.5)" }} />
          <div className="text-xs" style={{ color: "rgba(255,255,255,0.9)" }}>₹{a.fee} consultation fee</div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t text-11 leading-relaxed" style={{ borderColor: "rgba(255,255,255,0.08)", color: "rgba(255,255,255,0.6)" }}>
        {a.instructions}
      </div>
    </div>
  );
}

/* ─── Dispatcher ───────────────────────────────────────── */
export default function Block({ block }) {
  switch (block.type) {
    case "text":                  return <TextBlock {...block} />;
    case "disclaimer":            return <DisclaimerBlock {...block} />;
    case "emergency":             return <EmergencyBlock {...block} />;
    case "doctors":               return <DoctorsBlock {...block} />;
    case "medications":           return <MedicationsBlock {...block} />;
    case "pharmacies":            return <PharmaciesBlock {...block} />;
    case "lab_results":           return <LabResultsBlock {...block} />;
    case "vaccine_schedule":      return <VaccineScheduleBlock {...block} />;
    case "prescriptions":         return <PrescriptionsBlock {...block} />;
    case "appointment_slots":     return <AppointmentSlotsBlock {...block} />;
    case "appointment_confirmed": return <AppointmentConfirmedBlock {...block} />;
    default:
      return (
        <div className="text-xs px-3 py-2 rounded-md" style={{ background: "rgba(255,255,255,0.04)", color: "rgba(255,255,255,0.5)" }}>
          [Unknown block type: {block.type}]
        </div>
      );
  }
}
