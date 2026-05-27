import json
import os
from datetime import datetime

DB_FILE = "hospital_data.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2, default=str)

def init_db():
    db = {
        "users": {
            "admin1": {
                "id": "admin1",
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "name": "Hospital Admin"
            }
        },
        "doctors": {},
        "specialities": ["Cardiology", "Dermatology", "General Medicine", "Orthopedics", "Pediatrics", "Neurology", "Gynecology", "ENT"],
        "shifts": {},
        "slots": {},
        "appointments": {},
        "prescriptions": {}
    }
    save_db(db)
    print("✅ Database initialized with default admin (username: admin, password: admin123)")
    return db
