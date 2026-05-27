from database import load_db, save_db
from datetime import datetime
import uuid

def doctor_menu(doctor_user):
    did = doctor_user["id"]
    while True:
        print("\n╔══════════════════════════════════════╗")
        print("║          DOCTOR DASHBOARD             ║")
        print("╠══════════════════════════════════════╣")
        print("║  1. View My Schedule                  ║")
        print("║  2. View Today's Appointments         ║")
        print("║  3. Update Appointment Status         ║")
        print("║  4. Add Prescription                  ║")
        print("║  5. Add Video Link (Online)           ║")
        print("║  6. View Patient History              ║")
        print("║  7. Logout                            ║")
        print("╚══════════════════════════════════════╝")
        ch = input("Select: ").strip()
        if ch == "1": view_my_schedule(did)
        elif ch == "2": view_my_appointments(did)
        elif ch == "3": update_appointment_status(did)
        elif ch == "4": add_prescription(did)
        elif ch == "5": add_video_link(did)
        elif ch == "6": view_patient_history(did)
        elif ch == "7":
            print("👋 Logged out.")
            break

def view_my_schedule(did):
    db = load_db()
    shifts = [s for s in db["shifts"].values() if s["doctor_id"] == did]
    if not shifts:
        print("\nNo shifts assigned yet.")
        return
    print(f"\n── My Schedule ──")
    print(f"{'ShiftID':<10} {'Date':<12} {'Shift':<10} {'Start':<8} {'End':<8} {'Mode':<10}")
    print("─" * 62)
    for s in sorted(shifts, key=lambda x: x["date"]):
        print(f"{s['id']:<10} {s['date']:<12} {s['shift_name']:<10} {s['start_time']:<8} {s['end_time']:<8} {s['mode']:<10}")
        # Show booked patients for this shift
        slots = [sl for sl in db["slots"].values() if sl["shift_id"] == s["id"] and sl["booked"]]
        for sl in sorted(slots, key=lambda x: x["token"]):
            # find patient name
            pname = db["users"].get(sl["patient_id"], {}).get("name", "Unknown")
            print(f"   Token {sl['token']:>2}: {pname} | {sl['time']}")

def view_my_appointments(did):
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did and a["date"] == today]
    if not apts:
        print(f"\nNo appointments today ({today}).")
        return
    print(f"\n── Today's Appointments ({today}) ──")
    print(f"{'AptID':<12} {'Patient':<20} {'Time':<15} {'Token':>6} {'Status':<12}")
    print("─" * 70)
    for a in sorted(apts, key=lambda x: x.get("token", 0)):
        print(f"{a['id']:<12} {a['patient_name'][:19]:<20} {a.get('time','N/A'):<15} {str(a.get('token','-')):>6} {a['status']:<12}")

def update_appointment_status(did):
    db = load_db()
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did and a["status"] in ("confirmed", "no-show")]
    if not apts:
        print("\nNo active appointments to update.")
        return
    print(f"\n{'AptID':<12} {'Patient':<20} {'Date':<12} {'Status'}")
    print("─" * 60)
    for a in apts:
        print(f"{a['id']:<12} {a['patient_name'][:19]:<20} {a['date']:<12} {a['status']}")
    apt_id = input("\nEnter Appointment ID: ").strip().upper()
    if apt_id not in db["appointments"]:
        print("❌ Not found.")
        return
    print("New status: 1. confirmed  2. completed  3. cancelled  4. no-show")
    status_map = {"1": "confirmed", "2": "completed", "3": "cancelled", "4": "no-show"}
    s = input("Select: ").strip()
    if s not in status_map:
        print("❌ Invalid.")
        return
    db["appointments"][apt_id]["status"] = status_map[s]
    save_db(db)
    print(f"✅ Status updated to '{status_map[s]}'.")

def add_prescription(did):
    db = load_db()
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did and a["status"] == "completed"]
    if not apts:
        print("\nNo completed appointments to prescribe.")
        return
    print(f"\n{'AptID':<12} {'Patient':<20} {'Date'}")
    print("─" * 45)
    for a in apts:
        print(f"{a['id']:<12} {a['patient_name'][:19]:<20} {a['date']}")
    apt_id = input("\nAppointment ID: ").strip().upper()
    if apt_id not in db["appointments"]:
        print("❌ Not found.")
        return
    apt = db["appointments"][apt_id]
    print("\n── Add Prescription ──")
    diagnosis = input("Diagnosis: ").strip()
    medicines = input("Medicines (comma-separated): ").strip()
    followup = input("Follow-up Instructions: ").strip()

    pres_id = "PR" + str(uuid.uuid4())[:6].upper()
    db["prescriptions"][pres_id] = {
        "id": pres_id,
        "appointment_id": apt_id,
        "patient_id": apt["patient_id"],
        "doctor_id": did,
        "doctor_name": apt["doctor_name"],
        "date": apt["date"],
        "diagnosis": diagnosis,
        "medicines": medicines,
        "followup": followup,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_db(db)
    print(f"✅ Prescription saved! ID: {pres_id}")

def add_video_link(did):
    db = load_db()
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did and a["mode"] == "Online" and a["status"] == "confirmed"]
    if not apts:
        print("\nNo online confirmed appointments.")
        return
    print(f"\n{'AptID':<12} {'Patient':<20} {'Date'}")
    print("─" * 45)
    for a in apts:
        print(f"{a['id']:<12} {a['patient_name'][:19]:<20} {a['date']}")
    apt_id = input("\nAppointment ID: ").strip().upper()
    if apt_id not in db["appointments"]:
        print("❌ Not found.")
        return
    link = input("Video Consultation Link: ").strip()
    db["appointments"][apt_id]["video_link"] = link
    save_db(db)
    print("✅ Video link added. Visible to patient.")

def view_patient_history(did):
    db = load_db()
    apts = [a for a in db["appointments"].values() if a["doctor_id"] == did]
    if not apts:
        print("\nNo patient history.")
        return
    patient_ids = list(set(a["patient_id"] for a in apts))
    print("\nPatients seen:")
    for i, pid in enumerate(patient_ids, 1):
        pname = db["users"].get(pid, {}).get("name", "Unknown")
        print(f"  {i}. {pid} - {pname}")
    idx = int(input("Select patient number (0 to cancel): ").strip()) - 1
    if idx < 0:
        return
    pid = patient_ids[idx]
    patient_apts = [a for a in apts if a["patient_id"] == pid]
    print(f"\n── History for {db['users'].get(pid, {}).get('name','Unknown')} ──")
    for a in sorted(patient_apts, key=lambda x: x["date"]):
        print(f"  {a['date']} | {a['status']} | Token {a.get('token','-')}")
        pres = [p for p in db["prescriptions"].values() if p["appointment_id"] == a["id"]]
        for p in pres:
            print(f"    📋 Diagnosis: {p['diagnosis']}")
            print(f"    💊 Medicines: {p['medicines']}")
            print(f"    📅 Follow-up: {p['followup']}")
