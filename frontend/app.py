import streamlit as st
import uuid
from datetime import datetime, date
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import load_db, save_db

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hospital Appointment System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
h1, h2, h3 { font-family: 'Syne', sans-serif; }

.stApp { background: #f0f4f8; }

.hero-card {
    background: linear-gradient(135deg, #1a3c5e 0%, #0f6b8a 60%, #00b4d8 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    color: white;
    margin-bottom: 1.5rem;
}
.hero-card h1 { color: white; font-size: 2rem; margin: 0; }
.hero-card p { color: rgba(255,255,255,0.8); margin: 0.5rem 0 0; }

.metric-card {
    background: white;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid #00b4d8;
}
.metric-card .label { color: #6b7280; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value { color: #1a3c5e; font-size: 1.8rem; font-weight: 700; font-family: 'Syne', sans-serif; }

.status-confirmed { background: #dbeafe; color: #1d4ed8; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.status-completed { background: #d1fae5; color: #065f46; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.status-cancelled { background: #fee2e2; color: #991b1b; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.status-noshow    { background: #fef3c7; color: #92400e; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    color: #1a3c5e;
    font-weight: 700;
    padding: 0.5rem 0;
    border-bottom: 2px solid #00b4d8;
    margin-bottom: 1rem;
}
div[data-testid="stSidebarContent"] { background: #1a3c5e; }
div[data-testid="stSidebarContent"] * { color: white !important; }
div[data-testid="stSidebarContent"] .stSelectbox label { color: rgba(255,255,255,0.7) !important; font-size: 0.8rem !important; }

.apt-card {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
    border-left: 3px solid #00b4d8;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def status_badge(status):
    cls = {"confirmed": "status-confirmed", "completed": "status-completed",
           "cancelled": "status-cancelled", "no-show": "status-noshow"}.get(status, "status-confirmed")
    return f'<span class="{cls}">{status.capitalize()}</span>'

def logout():
    st.session_state.user = None
    st.session_state.page = "login"

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════════════════════════════════════

def show_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="hero-card" style="text-align:center">
            <h1>🏥 Hospital System</h1>
            <p>Role-Based Medical Platform</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register as Patient"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
                if submitted:
                    db = load_db()
                    found = None
                    for uid, user in db["users"].items():
                        if user["username"] == username and user["password"] == password:
                            found = user
                            break
                    if found:
                        st.session_state.user = found
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials.")

        with tab2:
            with st.form("register_form"):
                name = st.text_input("Full Name")
                uname = st.text_input("Username")
                pwd = st.text_input("Password", type="password")
                age = st.text_input("Age")
                phone = st.text_input("Phone")
                reg = st.form_submit_button("Register", use_container_width=True, type="primary")
                if reg:
                    if not all([name, uname, pwd, age, phone]):
                        st.error("All fields required.")
                    else:
                        db = load_db()
                        if any(u["username"] == uname for u in db["users"].values()):
                            st.error("❌ Username already exists.")
                        else:
                            uid = "P" + str(uuid.uuid4())[:6].upper()
                            db["users"][uid] = {"id": uid, "username": uname, "password": pwd,
                                                "role": "patient", "name": name, "age": age, "phone": phone}
                            save_db(db)
                            st.success(f"✅ Registered! Patient ID: {uid}. Please login.")


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN PAGES
# ═══════════════════════════════════════════════════════════════════════════════

def admin_dashboard():
    db = load_db()
    apts = db["appointments"]
    today = datetime.now().strftime("%Y-%m-%d")

    st.markdown('<div class="hero-card"><h1>🏥 Admin Dashboard</h1><p>Hospital Management Overview</p></div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    metrics = [
        ("Total Appointments", len(apts)),
        ("Today's", len([a for a in apts.values() if a.get("date") == today])),
        ("Completed", len([a for a in apts.values() if a.get("status") == "completed"])),
        ("Cancelled", len([a for a in apts.values() if a.get("status") == "cancelled"])),
        ("Doctors", len(db["doctors"])),
        ("Patients", sum(1 for u in db["users"].values() if u["role"] == "patient")),
    ]
    for col, (label, val) in zip([c1, c2, c3, c4, c5, c6], metrics):
        with col:
            st.markdown(f'<div class="metric-card"><div class="label">{label}</div><div class="value">{val}</div></div>', unsafe_allow_html=True)


def admin_manage_doctors():
    db = load_db()
    st.markdown('<div class="section-header">👨‍⚕️ Manage Doctors</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["View All", "Add Doctor", "Update Doctor", "Deactivate"])

    with tab1:
        if not db["doctors"]:
            st.info("No doctors yet.")
        else:
            rows = []
            for d in db["doctors"].values():
                rows.append({"ID": d["id"], "Name": d["name"], "Speciality": d["speciality"],
                             "Mode": d["mode"], "Fee (₹)": d["fee"],
                             "Status": "✅ Active" if d.get("active", True) else "❌ Inactive"})
            st.dataframe(rows, use_container_width=True)

    with tab2:
        with st.form("add_doctor"):
            name = st.text_input("Doctor Name")
            speciality = st.selectbox("Speciality", db["specialities"])
            mode = st.radio("Consultation Mode", ["Online", "Offline"], horizontal=True)
            fee = st.number_input("Consultation Fee (₹)", min_value=0.0, step=50.0)
            username = st.text_input("Doctor Login Username")
            password = st.text_input("Doctor Login Password", type="password")
            add = st.form_submit_button("Add Doctor", type="primary")
            if add:
                if not all([name, username, password]):
                    st.error("All fields required.")
                else:
                    did = "D" + str(uuid.uuid4())[:6].upper()
                    db["doctors"][did] = {"id": did, "name": name, "speciality": speciality,
                                         "mode": mode, "fee": fee, "active": True}
                    db["users"][did] = {"id": did, "username": username, "password": password,
                                       "role": "doctor", "name": name}
                    save_db(db)
                    st.success(f"✅ Doctor added! ID: {did}")
                    st.rerun()

    with tab3:
        if db["doctors"]:
            doc_options = {f"{d['name']} ({did})": did for did, d in db["doctors"].items()}
            sel = st.selectbox("Select Doctor", list(doc_options.keys()))
            did = doc_options[sel]
            d = db["doctors"][did]
            with st.form("update_doctor"):
                new_name = st.text_input("Name", value=d["name"])
                new_fee = st.number_input("Fee (₹)", value=float(d["fee"]), step=50.0)
                upd = st.form_submit_button("Update", type="primary")
                if upd:
                    db["doctors"][did]["name"] = new_name
                    db["doctors"][did]["fee"] = new_fee
                    save_db(db)
                    st.success("✅ Doctor updated.")
                    st.rerun()

    with tab4:
        if db["doctors"]:
            doc_options = {f"{d['name']} ({did})": did for did, d in db["doctors"].items() if d.get("active", True)}
            if not doc_options:
                st.info("No active doctors.")
            else:
                sel = st.selectbox("Select Doctor to Deactivate", list(doc_options.keys()))
                if st.button("Deactivate", type="primary"):
                    db["doctors"][doc_options[sel]]["active"] = False
                    save_db(db)
                    st.success("✅ Doctor deactivated.")
                    st.rerun()


def admin_manage_shifts():
    db = load_db()
    st.markdown('<div class="section-header">📅 Manage Shifts</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["View Shifts", "Create Shift"])

    with tab1:
        shifts = list(db["shifts"].values())
        if not shifts:
            st.info("No shifts created yet.")
        else:
            rows = [{"ID": s["id"], "Doctor": s["doctor_name"], "Date": s["date"],
                     "Shift": s["shift_name"], "Start": s["start_time"],
                     "End": s["end_time"], "Mode": s["mode"]} for s in sorted(shifts, key=lambda x: x["date"])]
            st.dataframe(rows, use_container_width=True)

    with tab2:
        if not db["doctors"]:
            st.warning("Add a doctor first.")
        else:
            doc_options = {f"{d['name']} - {d['mode']} ({did})": did for did, d in db["doctors"].items() if d.get("active", True)}
            with st.form("create_shift"):
                sel = st.selectbox("Select Doctor", list(doc_options.keys()))
                shift_date = st.date_input("Date", min_value=date.today())
                shift_type = st.selectbox("Shift", ["Morning (9AM-1PM)", "Evening (2PM-6PM)", "Night (7PM-11PM)"])
                create = st.form_submit_button("Create Shift", type="primary")
                if create:
                    did = doc_options[sel]
                    shift_map = {
                        "Morning (9AM-1PM)": ("Morning", "09:00", "13:00"),
                        "Evening (2PM-6PM)": ("Evening", "14:00", "18:00"),
                        "Night (7PM-11PM)": ("Night", "19:00", "23:00")
                    }
                    sname, start, end = shift_map[shift_type]
                    sid = "SH" + str(uuid.uuid4())[:5].upper()
                    db["shifts"][sid] = {
                        "id": sid, "doctor_id": did,
                        "doctor_name": db["doctors"][did]["name"],
                        "date": str(shift_date), "shift_name": sname,
                        "start_time": start, "end_time": end,
                        "mode": db["doctors"][did]["mode"]
                    }
                    save_db(db)
                    st.success(f"✅ Shift created! ID: {sid}")
                    st.rerun()


def admin_manage_slots():
    db = load_db()
    st.markdown('<div class="section-header">🕐 Manage Slots & Tokens</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Generate Slots", "View Slots"])

    with tab1:
        if not db["shifts"]:
            st.warning("Create a shift first.")
        else:
            shift_options = {f"{s['doctor_name']} | {s['date']} | {s['shift_name']} ({sid})": sid
                             for sid, s in db["shifts"].items()}
            with st.form("gen_slots"):
                sel = st.selectbox("Select Shift", list(shift_options.keys()))
                duration = st.select_slider("Slot Duration (minutes)", options=[15, 20, 30])
                gen = st.form_submit_button("Generate Slots", type="primary")
                if gen:
                    sid = shift_options[sel]
                    shift = db["shifts"][sid]
                    start_h, start_m = map(int, shift["start_time"].split(":"))
                    end_h, end_m = map(int, shift["end_time"].split(":"))
                    start_mins = start_h * 60 + start_m
                    end_mins = end_h * 60 + end_m
                    token = 1
                    created = 0
                    current = start_mins
                    while current + duration <= end_mins:
                        h, m = current // 60, current % 60
                        es = current + duration
                        eh, em = es // 60, es % 60
                        time_str = f"{h:02d}:{m:02d}-{eh:02d}:{em:02d}"
                        slot_id = f"SL{sid}{token:02d}"
                        db["slots"][slot_id] = {
                            "id": slot_id, "shift_id": sid,
                            "doctor_id": shift["doctor_id"],
                            "doctor_name": shift["doctor_name"],
                            "date": shift["date"], "time": time_str,
                            "mode": shift["mode"], "token": token,
                            "booked": False, "patient_id": None
                        }
                        token += 1
                        current += duration
                        created += 1
                    save_db(db)
                    st.success(f"✅ {created} slots generated!")
                    st.rerun()

    with tab2:
        if not db["shifts"]:
            st.info("No shifts yet.")
        else:
            shift_options = {f"{s['doctor_name']} | {s['date']} | {s['shift_name']} ({sid})": sid
                             for sid, s in db["shifts"].items()}
            sel = st.selectbox("Select Shift", list(shift_options.keys()))
            sid = shift_options[sel]
            slots = [s for s in db["slots"].values() if s["shift_id"] == sid]
            if not slots:
                st.info("No slots generated for this shift.")
            else:
                rows = [{"Token": s["token"], "SlotID": s["id"], "Time": s["time"],
                         "Status": "🔴 Booked" if s["booked"] else "🟢 Available",
                         "Patient": s.get("patient_id") or "-"}
                        for s in sorted(slots, key=lambda x: x["token"])]
                st.dataframe(rows, use_container_width=True)


def admin_appointments():
    db = load_db()
    st.markdown('<div class="section-header">📋 All Appointments</div>', unsafe_allow_html=True)
    apts = db["appointments"]
    if not apts:
        st.info("No appointments found.")
        return
    rows = [{"ID": a["id"], "Patient": a["patient_name"], "Doctor": a["doctor_name"],
             "Date": a["date"], "Token": a.get("token", "-"), "Mode": a["mode"],
             "Status": a["status"]} for a in sorted(apts.values(), key=lambda x: x["date"])]
    st.dataframe(rows, use_container_width=True)


def admin_revenue():
    db = load_db()
    st.markdown('<div class="section-header">💰 Revenue Report</div>', unsafe_allow_html=True)
    apts = [a for a in db["appointments"].values() if a["status"] == "completed"]
    total = 0
    by_doctor = {}
    by_spec = {}
    for a in apts:
        fee = db["doctors"].get(a["doctor_id"], {}).get("fee", 0)
        total += fee
        by_doctor[a["doctor_name"]] = by_doctor.get(a["doctor_name"], 0) + fee
        spec = db["doctors"].get(a["doctor_id"], {}).get("speciality", "Unknown")
        by_spec[spec] = by_spec.get(spec, 0) + fee

    st.metric("💰 Total Revenue", f"₹{total:,.0f}")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("By Doctor")
        if by_doctor:
            rows = [{"Doctor": k, "Revenue (₹)": v} for k, v in sorted(by_doctor.items(), key=lambda x: -x[1])]
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No revenue yet.")
    with col2:
        st.subheader("By Speciality")
        if by_spec:
            rows = [{"Speciality": k, "Revenue (₹)": v} for k, v in sorted(by_spec.items(), key=lambda x: -x[1])]
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No revenue yet.")


def admin_patients():
    db = load_db()
    st.markdown('<div class="section-header">🧑‍🤝‍🧑 All Patients</div>', unsafe_allow_html=True)
    patients = [u for u in db["users"].values() if u["role"] == "patient"]
    if not patients:
        st.info("No patients registered.")
        return
    rows = [{"ID": p["id"], "Name": p["name"], "Age": p.get("age", "-"),
             "Phone": p.get("phone", "-"), "Username": p["username"]} for p in patients]
    st.dataframe(rows, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DOCTOR PAGES
# ═══════════════════════════════════════════════════════════════════════════════

def doctor_schedule(did):
    db = load_db()
    st.markdown('<div class="section-header">📅 My Schedule</div>', unsafe_allow_html=True)
    shifts = [s for s in db["shifts"].values() if s["doctor_id"] == did]
    if not shifts:
        st.info("No shifts assigned yet.")
        return
    for s in sorted(shifts, key=lambda x: x["date"]):
        with st.expander(f"📅 {s['date']} — {s['shift_name']} ({s['start_time']} to {s['end_time']}) | {s['mode']}"):
            slots = [sl for sl in db["slots"].values() if sl["shift_id"] == s["id"] and sl["booked"]]
            if not slots:
                st.write("No booked patients in this shift.")
            else:
                for sl in sorted(slots, key=lambda x: x["token"]):
                    pname = db["users"].get(sl["patient_id"], {}).get("name", "Unknown")
                    st.write(f"Token {sl['token']:02d}: **{pname}** | {sl['time']}")


def doctor_today(did):
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    st.markdown(f'<div class="section-header">🗓️ Today\'s Appointments ({today})</div>', unsafe_allow_html=True)
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did and a["date"] == today]
    if not apts:
        st.info(f"No appointments today.")
        return
    for a in sorted(apts, key=lambda x: x.get("token", 0)):
        st.markdown(f"""
        <div class="apt-card">
            <b>{a['patient_name']}</b> &nbsp;·&nbsp; Token {a.get('token','-')} &nbsp;·&nbsp; {a.get('time','N/A')}
            &nbsp; {status_badge(a['status'])}
        </div>
        """, unsafe_allow_html=True)


def doctor_update_status(did):
    db = load_db()
    st.markdown('<div class="section-header">✏️ Update Appointment Status</div>', unsafe_allow_html=True)
    apts = [a for a in db["appointments"].values()
            if a["doctor_id"] == did and a["status"] in ("confirmed", "no-show")]
    if not apts:
        st.info("No active appointments to update.")
        return
    apt_options = {f"{a['patient_name']} | {a['date']} | Token {a.get('token','-')} ({a['id']})": a["id"] for a in apts}
    sel = st.selectbox("Select Appointment", list(apt_options.keys()))
    new_status = st.selectbox("New Status", ["confirmed", "completed", "cancelled", "no-show"])
    if st.button("Update Status", type="primary"):
        db["appointments"][apt_options[sel]]["status"] = new_status
        save_db(db)
        st.success(f"✅ Status updated to '{new_status}'.")
        st.rerun()


def doctor_prescription(did):
    db = load_db()
    st.markdown('<div class="section-header">💊 Add Prescription</div>', unsafe_allow_html=True)
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did and a["status"] == "completed"]
    if not apts:
        st.info("No completed appointments.")
        return
    apt_options = {f"{a['patient_name']} | {a['date']} ({a['id']})": a["id"] for a in apts}
    with st.form("prescription_form"):
        sel = st.selectbox("Select Appointment", list(apt_options.keys()))
        diagnosis = st.text_area("Diagnosis")
        medicines = st.text_input("Medicines (comma-separated)")
        followup = st.text_area("Follow-up Instructions")
        sub = st.form_submit_button("Save Prescription", type="primary")
        if sub:
            apt_id = apt_options[sel]
            apt = db["appointments"][apt_id]
            pres_id = "PR" + str(uuid.uuid4())[:6].upper()
            db["prescriptions"][pres_id] = {
                "id": pres_id, "appointment_id": apt_id,
                "patient_id": apt["patient_id"], "doctor_id": did,
                "doctor_name": apt["doctor_name"], "date": apt["date"],
                "diagnosis": diagnosis, "medicines": medicines,
                "followup": followup,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_db(db)
            st.success(f"✅ Prescription saved! ID: {pres_id}")
            st.rerun()


def doctor_video_link(did):
    db = load_db()
    st.markdown('<div class="section-header">🎥 Add Video Link</div>', unsafe_allow_html=True)
    apts = [a for a in db["appointments"].values()
            if a["doctor_id"] == did and a["mode"] == "Online" and a["status"] == "confirmed"]
    if not apts:
        st.info("No online confirmed appointments.")
        return
    apt_options = {f"{a['patient_name']} | {a['date']} ({a['id']})": a["id"] for a in apts}
    with st.form("video_link_form"):
        sel = st.selectbox("Select Appointment", list(apt_options.keys()))
        link = st.text_input("Video Consultation Link (e.g., Google Meet / Zoom)")
        sub = st.form_submit_button("Save Link", type="primary")
        if sub:
            db["appointments"][apt_options[sel]]["video_link"] = link
            save_db(db)
            st.success("✅ Video link saved. Patient can now see it.")
            st.rerun()


def doctor_patient_history(did):
    db = load_db()
    st.markdown('<div class="section-header">📂 Patient History</div>', unsafe_allow_html=True)
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did]
    if not apts:
        st.info("No patient history.")
        return
    patient_ids = list(set(a["patient_id"] for a in apts))
    patient_options = {db["users"].get(pid, {}).get("name", pid) + f" ({pid})": pid for pid in patient_ids}
    sel = st.selectbox("Select Patient", list(patient_options.keys()))
    pid = patient_options[sel]
    patient_apts = [a for a in apts if a["patient_id"] == pid]
    for a in sorted(patient_apts, key=lambda x: x["date"], reverse=True):
        with st.expander(f"📅 {a['date']} — {a['status'].capitalize()} | Token {a.get('token','-')}"):
            pres = [p for p in db["prescriptions"].values() if p["appointment_id"] == a["id"]]
            if pres:
                for p in pres:
                    st.write(f"**Diagnosis:** {p['diagnosis']}")
                    st.write(f"**Medicines:** {p['medicines']}")
                    st.write(f"**Follow-up:** {p['followup']}")
            else:
                st.write("No prescription recorded.")


# ═══════════════════════════════════════════════════════════════════════════════
# PATIENT PAGES
# ═══════════════════════════════════════════════════════════════════════════════

def patient_book(patient):
    db = load_db()
    pid = patient["id"]
    mode = db["users"][pid].get("mode", "Online")
    st.markdown(f'<div class="section-header">🗓️ Book Appointment ({mode} Mode)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(f"Switch to {'Offline' if mode == 'Online' else 'Online'}", use_container_width=True):
            new_mode = "Offline" if mode == "Online" else "Online"
            db["users"][pid]["mode"] = new_mode
            st.session_state.user["mode"] = new_mode
            save_db(db)
            st.rerun()

    spec_options = ["All Specialities"] + db["specialities"]
    chosen_spec_label = st.selectbox("Filter by Speciality", spec_options)
    chosen_spec = None if chosen_spec_label == "All Specialities" else chosen_spec_label

    doctors = [d for d in db["doctors"].values()
               if d.get("active", True) and d["mode"] == mode
               and (chosen_spec is None or d["speciality"] == chosen_spec)]

    if not doctors:
        st.warning(f"No {mode} doctors found for the selected speciality.")
        return

    doc_options = {f"Dr. {d['name']} | {d['speciality']} | ₹{d['fee']:.0f} ({d['id']})": d["id"] for d in doctors}
    sel_doc = st.selectbox("Select Doctor", list(doc_options.keys()))
    did = doc_options[sel_doc]

    today_str = datetime.now().strftime("%Y-%m-%d")
    slots = [s for s in db["slots"].values()
             if s["doctor_id"] == did and not s["booked"] and s["date"] >= today_str]
    if not slots:
        st.warning("No available slots for this doctor.")
        return

    slot_options = {f"📅 {s['date']} | 🕐 {s['time']} | Token {s['token']} ({s['id']})": s["id"] for s in sorted(slots, key=lambda x: (x["date"], x["token"]))}
    sel_slot = st.selectbox("Select Slot", list(slot_options.keys()))
    slot_id = slot_options[sel_slot]
    chosen_slot = db["slots"][slot_id]

    conflict = [a for a in db["appointments"].values()
                if a["patient_id"] == pid and a["date"] == chosen_slot["date"]
                and a["status"] not in ("cancelled",)]
    if conflict:
        st.warning("⚠️ You already have an appointment on this date.")
        if not st.checkbox("Book anyway?"):
            return

    if st.button("✅ Confirm Booking", type="primary"):
        db2 = load_db()
        if db2["slots"][slot_id]["booked"]:
            st.error("❌ This slot was just booked by someone else.")
            return
        apt_id = "APT" + str(uuid.uuid4())[:6].upper()
        db2["slots"][slot_id]["booked"] = True
        db2["slots"][slot_id]["patient_id"] = pid
        doc = db2["doctors"][did]
        db2["appointments"][apt_id] = {
            "id": apt_id, "patient_id": pid,
            "patient_name": patient["name"], "doctor_id": did,
            "doctor_name": doc["name"], "speciality": doc["speciality"],
            "date": chosen_slot["date"], "time": chosen_slot["time"],
            "token": chosen_slot["token"], "mode": mode,
            "slot_id": slot_id, "status": "confirmed", "video_link": None
        }
        save_db(db2)
        st.success(f"✅ Booked! Appointment ID: **{apt_id}** | Token: **{chosen_slot['token']}** | Fee: ₹{doc['fee']:.0f}")
        if mode == "Offline":
            st.info("📍 Clinic Address: City Hospital, Main Road")
        st.rerun()


def patient_appointments(pid):
    db = load_db()
    st.markdown('<div class="section-header">📋 My Appointments</div>', unsafe_allow_html=True)
    apts = [a for a in db["appointments"].values() if a["patient_id"] == pid]
    if not apts:
        st.info("No appointments found.")
        return
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = [a for a in apts if a["date"] >= today and a["status"] not in ("cancelled",)]
    past = [a for a in apts if a["date"] < today or a["status"] in ("completed", "cancelled", "no-show")]

    if upcoming:
        st.subheader("📌 Upcoming")
        for a in sorted(upcoming, key=lambda x: x["date"]):
            link_info = ""
            if a["mode"] == "Online" and a.get("video_link"):
                link_info = f'&nbsp;·&nbsp; <a href="{a["video_link"]}" target="_blank">🔗 Join Video</a>'
            elif a["mode"] == "Offline":
                link_info = "&nbsp;·&nbsp; 📍 City Hospital, Main Road"
            st.markdown(f"""
            <div class="apt-card">
                <b>{a['doctor_name']}</b> &nbsp;·&nbsp; {a['date']} {a.get('time','')}
                &nbsp;·&nbsp; Token <b>{a.get('token','-')}</b>
                &nbsp;·&nbsp; {a['mode']} {status_badge(a['status'])} {link_info}
            </div>
            """, unsafe_allow_html=True)

    if past:
        st.subheader("🕓 Past")
        for a in sorted(past, key=lambda x: x["date"], reverse=True)[:10]:
            st.markdown(f"""
            <div class="apt-card" style="border-left-color:#9ca3af">
                <b>{a['doctor_name']}</b> &nbsp;·&nbsp; {a['date']} &nbsp; {status_badge(a['status'])}
            </div>
            """, unsafe_allow_html=True)


def patient_medical_history(pid):
    db = load_db()
    st.markdown('<div class="section-header">🩺 My Medical History</div>', unsafe_allow_html=True)
    prescriptions = [p for p in db["prescriptions"].values() if p["patient_id"] == pid]
    if not prescriptions:
        st.info("No medical records found.")
        return
    for p in sorted(prescriptions, key=lambda x: x["date"], reverse=True):
        with st.expander(f"📅 {p['date']} — Dr. {p['doctor_name']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Diagnosis:** {p['diagnosis']}")
                st.write(f"**Medicines:** {p['medicines']}")
            with col2:
                st.write(f"**Follow-up:** {p['followup']}")
                st.write(f"**Recorded:** {p['timestamp']}")


def patient_cancel(pid):
    db = load_db()
    st.markdown('<div class="section-header">❌ Cancel Appointment</div>', unsafe_allow_html=True)
    today = datetime.now().strftime("%Y-%m-%d")
    apts = [a for a in db["appointments"].values()
            if a["patient_id"] == pid and a["status"] == "confirmed" and a["date"] >= today]
    if not apts:
        st.info("No cancellable appointments.")
        return
    apt_options = {f"{a['doctor_name']} | {a['date']} | Token {a.get('token','-')} ({a['id']})": a["id"] for a in apts}
    sel = st.selectbox("Select Appointment to Cancel", list(apt_options.keys()))
    if st.button("Cancel Appointment", type="primary"):
        apt_id = apt_options[sel]
        db["appointments"][apt_id]["status"] = "cancelled"
        slot_id = db["appointments"][apt_id].get("slot_id")
        if slot_id and slot_id in db["slots"]:
            db["slots"][slot_id]["booked"] = False
            db["slots"][slot_id]["patient_id"] = None
        save_db(db)
        st.success("✅ Appointment cancelled. Slot is now available.")
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    user = st.session_state.user

    if user is None:
        show_login()
        return

    role = user["role"]

    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.markdown(f"*{role.upper()}*")
        st.divider()

        if role == "admin":
            page = st.radio("Navigation", [
                "🏠 Dashboard", "👨‍⚕️ Doctors", "📅 Shifts",
                "🕐 Slots & Tokens", "📋 Appointments",
                "💰 Revenue", "🧑‍🤝‍🧑 Patients"
            ])
        elif role == "doctor":
            page = st.radio("Navigation", [
                "📅 My Schedule", "🗓️ Today's Appointments",
                "✏️ Update Status", "💊 Add Prescription",
                "🎥 Video Link", "📂 Patient History"
            ])
        elif role == "patient":
            page = st.radio("Navigation", [
                "🗓️ Book Appointment", "📋 My Appointments",
                "🩺 Medical History", "❌ Cancel Appointment"
            ])

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    # Route
    if role == "admin":
        if page == "🏠 Dashboard": admin_dashboard()
        elif page == "👨‍⚕️ Doctors": admin_manage_doctors()
        elif page == "📅 Shifts": admin_manage_shifts()
        elif page == "🕐 Slots & Tokens": admin_manage_slots()
        elif page == "📋 Appointments": admin_appointments()
        elif page == "💰 Revenue": admin_revenue()
        elif page == "🧑‍🤝‍🧑 Patients": admin_patients()

    elif role == "doctor":
        did = user["id"]
        if page == "📅 My Schedule": doctor_schedule(did)
        elif page == "🗓️ Today's Appointments": doctor_today(did)
        elif page == "✏️ Update Status": doctor_update_status(did)
        elif page == "💊 Add Prescription": doctor_prescription(did)
        elif page == "🎥 Video Link": doctor_video_link(did)
        elif page == "📂 Patient History": doctor_patient_history(did)

    elif role == "patient":
        # Refresh user from db for mode toggle
        db = load_db()
        patient = db["users"].get(user["id"], user)
        if page == "🗓️ Book Appointment": patient_book(patient)
        elif page == "📋 My Appointments": patient_appointments(patient["id"])
        elif page == "🩺 Medical History": patient_medical_history(patient["id"])
        elif page == "❌ Cancel Appointment": patient_cancel(patient["id"])


if __name__ == "__main__":
    main()
