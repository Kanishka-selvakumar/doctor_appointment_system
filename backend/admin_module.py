from database import load_db, save_db
import uuid
from datetime import datetime

def admin_menu(admin):
    while True:
        print("\n╔══════════════════════════════════════╗")
        print("║           ADMIN DASHBOARD             ║")
        print("╠══════════════════════════════════════╣")
        print("║  1. Dashboard Overview                ║")
        print("║  2. Manage Doctors                    ║")
        print("║  3. Manage Shifts                     ║")
        print("║  4. Manage Slots & Tokens             ║")
        print("║  5. View All Appointments             ║")
        print("║  6. Revenue Report                    ║")
        print("║  7. View All Patients                 ║")
        print("║  8. Logout                            ║")
        print("╚══════════════════════════════════════╝")
        choice = input("Select option: ").strip()

        if choice == "1": dashboard_overview()
        elif choice == "2": manage_doctors()
        elif choice == "3": manage_shifts()
        elif choice == "4": manage_slots()
        elif choice == "5": view_all_appointments()
        elif choice == "6": revenue_report()
        elif choice == "7": view_all_patients()
        elif choice == "8":
            print("👋 Logged out.")
            break
        else:
            print("❌ Invalid option.")

# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def dashboard_overview():
    db = load_db()
    apts = db["appointments"]
    today = datetime.now().strftime("%Y-%m-%d")

    total = len(apts)
    today_apts = [a for a in apts.values() if a.get("date") == today]
    online = [a for a in apts.values() if a.get("mode") == "Online"]
    offline = [a for a in apts.values() if a.get("mode") == "Offline"]
    completed = [a for a in apts.values() if a.get("status") == "completed"]
    cancelled = [a for a in apts.values() if a.get("status") == "cancelled"]

    print("\n╔══════════════════════════════════════╗")
    print("║         DASHBOARD OVERVIEW            ║")
    print("╠══════════════════════════════════════╣")
    print(f"║  Total Appointments     : {total:<11}║")
    print(f"║  Today's Appointments   : {len(today_apts):<11}║")
    print(f"║  Online  Appointments   : {len(online):<11}║")
    print(f"║  Offline Appointments   : {len(offline):<11}║")
    print(f"║  Completed              : {len(completed):<11}║")
    print(f"║  Cancelled              : {len(cancelled):<11}║")
    print(f"║  Total Doctors          : {len(db['doctors']):<11}║")
    print(f"║  Total Patients         : {sum(1 for u in db['users'].values() if u['role']=='patient'):<11}║")
    print("╚══════════════════════════════════════╝")

# ─── DOCTOR MANAGEMENT ────────────────────────────────────────────────────────

def manage_doctors():
    while True:
        print("\n── Doctor Management ──")
        print("1. Add Doctor")
        print("2. View All Doctors")
        print("3. Update Doctor")
        print("4. Deactivate Doctor")
        print("5. Back")
        ch = input("Select: ").strip()
        if ch == "1": add_doctor()
        elif ch == "2": view_doctors()
        elif ch == "3": update_doctor()
        elif ch == "4": deactivate_doctor()
        elif ch == "5": break

def add_doctor():
    db = load_db()
    print("\n── Add New Doctor ──")
    name = input("Doctor Name: ").strip()
    speciality = choose_speciality(db)
    mode = choose_mode()
    fee = input("Consultation Fee (₹): ").strip()
    username = input("Set Username for Doctor: ").strip()
    password = input("Set Password: ").strip()

    did = "D" + str(uuid.uuid4())[:6].upper()
    db["doctors"][did] = {
        "id": did,
        "name": name,
        "speciality": speciality,
        "mode": mode,
        "fee": float(fee),
        "active": True
    }
    db["users"][did] = {
        "id": did,
        "username": username,
        "password": password,
        "role": "doctor",
        "name": name
    }
    save_db(db)
    print(f"✅ Doctor added! Doctor ID: {did}")

def view_doctors(db=None):
    if db is None:
        db = load_db()
    print("\n── All Doctors ──")
    if not db["doctors"]:
        print("No doctors found.")
        return
    print(f"{'ID':<10} {'Name':<22} {'Speciality':<18} {'Mode':<10} {'Fee':>8} {'Status':<10}")
    print("─" * 80)
    for d in db["doctors"].values():
        status = "Active" if d.get("active", True) else "Inactive"
        print(f"{d['id']:<10} {d['name']:<22} {d['speciality']:<18} {d['mode']:<10} ₹{d['fee']:>7.0f} {status:<10}")

def update_doctor():
    db = load_db()
    view_doctors(db)
    did = input("\nEnter Doctor ID to update: ").strip().upper()
    if did not in db["doctors"]:
        print("❌ Doctor not found.")
        return
    d = db["doctors"][did]
    print(f"Updating {d['name']} — press Enter to keep current value")
    name = input(f"Name [{d['name']}]: ").strip() or d["name"]
    fee_input = input(f"Fee [{d['fee']}]: ").strip()
    fee = float(fee_input) if fee_input else d["fee"]
    d["name"], d["fee"] = name, fee
    save_db(db)
    print("✅ Doctor updated.")

def deactivate_doctor():
    db = load_db()
    view_doctors(db)
    did = input("\nEnter Doctor ID to deactivate: ").strip().upper()
    if did not in db["doctors"]:
        print("❌ Not found.")
        return
    db["doctors"][did]["active"] = False
    save_db(db)
    print("✅ Doctor deactivated.")

# ─── SHIFT MANAGEMENT ────────────────────────────────────────────────────────

def manage_shifts():
    while True:
        print("\n── Shift Management ──")
        print("1. Create Shift for Doctor")
        print("2. View All Shifts")
        print("3. Back")
        ch = input("Select: ").strip()
        if ch == "1": create_shift()
        elif ch == "2": view_shifts()
        elif ch == "3": break

def create_shift():
    db = load_db()
    view_doctors(db)
    did = input("\nDoctor ID: ").strip().upper()
    if did not in db["doctors"]:
        print("❌ Doctor not found.")
        return

    date = input("Date (YYYY-MM-DD): ").strip()
    print("Shift Type: 1. Morning (9AM-1PM)  2. Evening (2PM-6PM)  3. Night (7PM-11PM)")
    shift_map = {
        "1": ("Morning", "09:00", "13:00"),
        "2": ("Evening", "14:00", "18:00"),
        "3": ("Night", "19:00", "23:00")
    }
    st = input("Select shift: ").strip()
    if st not in shift_map:
        print("❌ Invalid.")
        return
    shift_name, start, end = shift_map[st]
    mode = db["doctors"][did]["mode"]

    sid = "SH" + str(uuid.uuid4())[:5].upper()
    db["shifts"][sid] = {
        "id": sid,
        "doctor_id": did,
        "doctor_name": db["doctors"][did]["name"],
        "date": date,
        "shift_name": shift_name,
        "start_time": start,
        "end_time": end,
        "mode": mode
    }
    save_db(db)
    print(f"✅ Shift created! Shift ID: {sid}")

def view_shifts(db=None, doctor_id=None):
    if db is None:
        db = load_db()
    print("\n── Shifts ──")
    shifts = [s for s in db["shifts"].values() if (doctor_id is None or s["doctor_id"] == doctor_id)]
    if not shifts:
        print("No shifts found.")
        return
    print(f"{'ShiftID':<10} {'Doctor':<20} {'Date':<12} {'Shift':<10} {'Start':<8} {'End':<8} {'Mode':<10}")
    print("─" * 82)
    for s in sorted(shifts, key=lambda x: x["date"]):
        print(f"{s['id']:<10} {s['doctor_name']:<20} {s['date']:<12} {s['shift_name']:<10} {s['start_time']:<8} {s['end_time']:<8} {s['mode']:<10}")

# ─── SLOT & TOKEN MANAGEMENT ─────────────────────────────────────────────────

def manage_slots():
    while True:
        print("\n── Slot & Token Management ──")
        print("1. Generate Slots for a Shift")
        print("2. View Slots for a Shift")
        print("3. Back")
        ch = input("Select: ").strip()
        if ch == "1": generate_slots()
        elif ch == "2": view_slots_admin()
        elif ch == "3": break

def generate_slots():
    db = load_db()
    view_shifts(db)
    sid = input("\nShift ID: ").strip().upper()
    if sid not in db["shifts"]:
        print("❌ Shift not found.")
        return
    duration = int(input("Slot duration (minutes) [15/20/30]: ").strip())
    shift = db["shifts"][sid]
    
    start_h, start_m = map(int, shift["start_time"].split(":"))
    end_h, end_m = map(int, shift["end_time"].split(":"))
    start_mins = start_h * 60 + start_m
    end_mins = end_h * 60 + end_m

    token = 1
    created = 0
    current = start_mins
    while current + duration <= end_mins:
        h = current // 60
        m = current % 60
        end_s = current + duration
        eh = end_s // 60
        em = end_s % 60
        time_str = f"{h:02d}:{m:02d}-{eh:02d}:{em:02d}"
        slot_id = f"SL{sid}{token:02d}"
        db["slots"][slot_id] = {
            "id": slot_id,
            "shift_id": sid,
            "doctor_id": shift["doctor_id"],
            "doctor_name": shift["doctor_name"],
            "date": shift["date"],
            "time": time_str,
            "mode": shift["mode"],
            "token": token,
            "booked": False,
            "patient_id": None
        }
        token += 1
        current += duration
        created += 1
    save_db(db)
    print(f"✅ {created} slots generated for shift {sid}.")

def view_slots_admin():
    db = load_db()
    view_shifts(db)
    sid = input("\nShift ID to view slots: ").strip().upper()
    slots = [s for s in db["slots"].values() if s["shift_id"] == sid]
    if not slots:
        print("No slots found.")
        return
    print(f"\n{'SlotID':<15} {'Time':<15} {'Token':>6} {'Status':<10} {'Patient'}")
    print("─" * 60)
    for s in sorted(slots, key=lambda x: x["token"]):
        status = "Booked" if s["booked"] else "Available"
        patient = s.get("patient_id") or "-"
        print(f"{s['id']:<15} {s['time']:<15} {s['token']:>6} {status:<10} {patient}")

# ─── APPOINTMENTS ─────────────────────────────────────────────────────────────

def view_all_appointments():
    db = load_db()
    apts = db["appointments"]
    if not apts:
        print("\nNo appointments found.")
        return
    print(f"\n{'AptID':<12} {'Patient':<15} {'Doctor':<18} {'Date':<12} {'Token':>6} {'Mode':<10} {'Status':<12}")
    print("─" * 90)
    for a in sorted(apts.values(), key=lambda x: x["date"]):
        print(f"{a['id']:<12} {a['patient_name'][:14]:<15} {a['doctor_name'][:17]:<18} {a['date']:<12} {a.get('token','-'):>6} {a['mode']:<10} {a['status']:<12}")

# ─── REVENUE ─────────────────────────────────────────────────────────────────

def revenue_report():
    db = load_db()
    apts = [a for a in db["appointments"].values() if a["status"] == "completed"]
    total = 0
    by_doctor = {}
    by_speciality = {}

    for a in apts:
        fee = db["doctors"].get(a["doctor_id"], {}).get("fee", 0)
        total += fee
        dname = a["doctor_name"]
        by_doctor[dname] = by_doctor.get(dname, 0) + fee
        spec = db["doctors"].get(a["doctor_id"], {}).get("speciality", "Unknown")
        by_speciality[spec] = by_speciality.get(spec, 0) + fee

    print("\n╔══════════════════════════════════════╗")
    print(f"║  TOTAL REVENUE: ₹{total:<21.0f}║")
    print("╚══════════════════════════════════════╝")
    print("\n── Revenue by Doctor ──")
    for doc, rev in sorted(by_doctor.items(), key=lambda x: -x[1]):
        print(f"  {doc:<25} ₹{rev:.0f}")
    print("\n── Revenue by Speciality ──")
    for spec, rev in sorted(by_speciality.items(), key=lambda x: -x[1]):
        print(f"  {spec:<25} ₹{rev:.0f}")

# ─── PATIENTS ─────────────────────────────────────────────────────────────────

def view_all_patients():
    db = load_db()
    patients = [u for u in db["users"].values() if u["role"] == "patient"]
    if not patients:
        print("\nNo patients found.")
        return
    print(f"\n{'PatientID':<12} {'Name':<22} {'Age':<6} {'Phone':<14} {'Username'}")
    print("─" * 70)
    for p in patients:
        print(f"{p['id']:<12} {p['name']:<22} {p.get('age','-'):<6} {p.get('phone','-'):<14} {p['username']}")

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def choose_speciality(db):
    specs = db["specialities"]
    print("\nSpecialities:")
    for i, s in enumerate(specs, 1):
        print(f"  {i}. {s}")
    idx = int(input("Select speciality number: ").strip()) - 1
    return specs[idx]

def choose_mode():
    print("Consultation Mode: 1. Online  2. Offline")
    return "Online" if input("Select: ").strip() == "1" else "Offline"
