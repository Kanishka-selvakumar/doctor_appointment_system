# 🏥 Hospital Appointment System

A role-based hospital appointment management system built in Python.

## 📁 Files
- `main.py` — Entry point (run this)
- `database.py` — Data storage (JSON-based, no external DB needed)
- `auth.py` — Login & registration
- `admin_module.py` — Admin features
- `doctor_module.py` — Doctor features
- `patient_module.py` — Patient features

## ▶️ How to Run

```bash
python main.py
```

> Requires Python 3.x only. No pip installs needed.

## 🔐 Default Login

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |

## 🔄 Typical Workflow

### Step 1 — Admin Setup
1. Login as Admin
2. **Add a Doctor** → Manage Doctors → Add Doctor
   - Set mode: Online OR Offline (not both)
3. **Create a Shift** → Manage Shifts → Create Shift
4. **Generate Slots** → Manage Slots → Generate Slots for Shift

### Step 2 — Patient Books
1. Register as Patient (Main Menu → Option 2)
2. Login as Patient
3. Toggle mode (Online/Offline) to match available doctor
4. Book Appointment → select doctor → select slot

### Step 3 — Doctor Consults
1. Login as Doctor
2. View Schedule / Today's Appointments
3. Update status → completed
4. Add Prescription

### Step 4 — Admin Reports
1. Dashboard Overview
2. Revenue Report

## ⚠️ Key Rules
- Online and Offline doctors are **separate** (strict rule)
- Slots are **auto-locked** when booked (no double booking)
- Only Admin can create/manage shifts and slots
- Video link (Online) is only visible to the booked patient
