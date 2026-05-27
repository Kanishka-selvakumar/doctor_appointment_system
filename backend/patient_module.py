from database import load_db, save_db
import uuid
from datetime import datetime

def patient_menu(patient):
    pid = patient["id"]
    while True:
        db = load_db()
        doc_info = db["doctors"].get(pid)
        mode = patient.get("mode", "Online")
        print(f"\n╔══════════════════════════════════════╗")
        print(f"║        PATIENT DASHBOARD              ║")
        print(f"║  Mode: {'🌐 Online' if mode == 'Online' else '🏥 Offline':<30}║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  1. Toggle Mode (Online / Offline)    ║")
        print(f"║  2. Browse & Book Appointment         ║")
        print(f"║  3. View My Appointments              ║")
        print(f"║  4. View My Medical History           ║")
        print(f"║  5. Cancel Appointment                ║")
        print(f"║  6. Logout                            ║")
        print(f"╚══════════════════════════════════════╝")
        ch = input("Select: ").strip()
        if ch == "1":
            patient["mode"] = "Offline" if mode == "Online" else "Online"
            db["users"][pid]["mode"] = patient["mode"]
            save_db(db)
            print(f"✅ Mode switched to {patient['mode']}")
        elif ch == "2": book_appointment(patient)
        elif ch == "3": view_my_appointments(pid)
        elif ch == "4": view_medical_history(pid)
        elif ch == "5": cancel_appointment(pid)
        elif ch == "6":
            print("👋 Logged out.")
            break

def book_appointment(patient):
    db = load_db()
    pid = patient["id"]
    mode = patient.get("mode", "Online")

    print(f"\n── Book Appointment ({mode} Mode) ──")
    print("Filter by Speciality:")
    specs = db["specialities"]
    print("  0. All Specialities")
    for i, s in enumerate(specs, 1):
        print(f"  {i}. {s}")
    spec_choice = input("Select: ").strip()
    chosen_spec = None if spec_choice == "0" else specs[int(spec_choice) - 1]

    # Find active doctors matching mode
    doctors = [d for d in db["doctors"].values()
               if d.get("active", True) and d["mode"] == mode
               and (chosen_spec is None or d["speciality"] == chosen_spec)]

    if not doctors:
        print(f"❌ No {mode} doctors found for selected speciality.")
        return

    print(f"\nAvailable {mode} Doctors:")
    print(f"{'#':<4} {'ID':<10} {'Name':<22} {'Speciality':<18} {'Fee':>8}")
    print("─" * 65)
    for i, d in enumerate(doctors, 1):
        print(f"{i:<4} {d['id']:<10} {d['name']:<22} {d['speciality']:<18} ₹{d['fee']:>7.0f}")

    dchoice = int(input("\nSelect doctor number: ").strip()) - 1
    selected_doc = doctors[dchoice]
    did = selected_doc["id"]

    # Show available slots
    today = datetime.now().strftime("%Y-%m-%d")
    slots = [s for s in db["slots"].values()
             if s["doctor_id"] == did and not s["booked"] and s["date"] >= today]
    if not slots:
        print("❌ No available slots for this doctor.")
        return

    print(f"\nAvailable Slots for Dr. {selected_doc['name']}:")
    print(f"{'#':<4} {'SlotID':<15} {'Date':<12} {'Time':<15} {'Token':>6}")
    print("─" * 56)
    for i, s in enumerate(slots, 1):
        print(f"{i:<4} {s['id']:<15} {s['date']:<12} {s['time']:<15} {s['token']:>6}")

    schoice = int(input("\nSelect slot number: ").strip()) - 1
    chosen_slot = slots[schoice]

    # Check patient doesn't already have appointment at same time
    conflict = [a for a in db["appointments"].values()
                if a["patient_id"] == pid and a["date"] == chosen_slot["date"]
                and a["status"] not in ("cancelled",)]
    if conflict:
        print("⚠️  You already have an appointment on this date.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != "y":
            return

    # Lock and book the slot (transactional)
    slot_id = chosen_slot["id"]
    if db["slots"][slot_id]["booked"]:
        print("❌ This slot was just booked by someone else. Please choose another.")
        return

    apt_id = "APT" + str(uuid.uuid4())[:6].upper()
    db["slots"][slot_id]["booked"] = True
    db["slots"][slot_id]["patient_id"] = pid

    db["appointments"][apt_id] = {
        "id": apt_id,
        "patient_id": pid,
        "patient_name": patient["name"],
        "doctor_id": did,
        "doctor_name": selected_doc["name"],
        "speciality": selected_doc["speciality"],
        "date": chosen_slot["date"],
        "time": chosen_slot["time"],
        "token": chosen_slot["token"],
        "mode": mode,
        "slot_id": slot_id,
        "status": "confirmed",
        "video_link": None
    }
    save_db(db)
    print(f"\n✅ Appointment Booked Successfully!")
    print(f"   Appointment ID : {apt_id}")
    print(f"   Doctor         : Dr. {selected_doc['name']}")
    print(f"   Date & Time    : {chosen_slot['date']} | {chosen_slot['time']}")
    print(f"   Token Number   : {chosen_slot['token']}")
    print(f"   Mode           : {mode}")
    print(f"   Fee            : ₹{selected_doc['fee']:.0f}")
    if mode == "Offline":
        print(f"   📍 Clinic Address: City Hospital, Main Road")

def view_my_appointments(pid):
    db = load_db()
    apts = [a for a in db["appointments"].values() if a["patient_id"] == pid]
    if not apts:
        print("\nNo appointments found.")
        return
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = [a for a in apts if a["date"] >= today and a["status"] not in ("cancelled",)]
    past = [a for a in apts if a["date"] < today or a["status"] in ("completed", "cancelled", "no-show")]

    if upcoming:
        print("\n── Upcoming Appointments ──")
        print(f"{'AptID':<12} {'Doctor':<20} {'Date':<12} {'Token':>6} {'Mode':<10} {'Status'}")
        print("─" * 72)
        for a in sorted(upcoming, key=lambda x: x["date"]):
            print(f"{a['id']:<12} {a['doctor_name'][:19]:<20} {a['date']:<12} {str(a.get('token','-')):>6} {a['mode']:<10} {a['status']}")
            if a["mode"] == "Online" and a.get("video_link"):
                print(f"   🔗 Video Link: {a['video_link']}")
            elif a["mode"] == "Offline":
                print(f"   📍 Clinic Address: City Hospital, Main Road")

    if past:
        print("\n── Past Appointments ──")
        print(f"{'AptID':<12} {'Doctor':<20} {'Date':<12} {'Status'}")
        print("─" * 55)
        for a in sorted(past, key=lambda x: x["date"], reverse=True)[:10]:
            print(f"{a['id']:<12} {a['doctor_name'][:19]:<20} {a['date']:<12} {a['status']}")

def view_medical_history(pid):
    db = load_db()
    prescriptions = [p for p in db["prescriptions"].values() if p["patient_id"] == pid]
    if not prescriptions:
        print("\nNo medical records found.")
        return
    print("\n── My Medical History ──")
    for p in sorted(prescriptions, key=lambda x: x["date"], reverse=True):
        print(f"\n  Date      : {p['date']}")
        print(f"  Doctor    : Dr. {p['doctor_name']}")
        print(f"  Diagnosis : {p['diagnosis']}")
        print(f"  Medicines : {p['medicines']}")
        print(f"  Follow-up : {p['followup']}")
        print(f"  Timestamp : {p['timestamp']}")
        print("  " + "─" * 40)

def cancel_appointment(pid):
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    apts = [a for a in db["appointments"].values()
            if a["patient_id"] == pid and a["status"] == "confirmed" and a["date"] >= today]
    if not apts:
        print("\nNo cancellable appointments.")
        return
    print(f"\n{'AptID':<12} {'Doctor':<20} {'Date':<12} {'Token'}")
    print("─" * 55)
    for a in apts:
        print(f"{a['id']:<12} {a['doctor_name'][:19]:<20} {a['date']:<12} {a.get('token','-')}")
    apt_id = input("\nEnter Appointment ID to cancel: ").strip().upper()
    if apt_id not in db["appointments"] or db["appointments"][apt_id]["patient_id"] != pid:
        print("❌ Not found.")
        return
    db["appointments"][apt_id]["status"] = "cancelled"
    slot_id = db["appointments"][apt_id].get("slot_id")
    if slot_id and slot_id in db["slots"]:
        db["slots"][slot_id]["booked"] = False
        db["slots"][slot_id]["patient_id"] = None
    save_db(db)
    print("✅ Appointment cancelled. Slot is now available.")
