from database import load_db, save_db
import uuid

def login():
    db = load_db()
    print("\n╔══════════════════════════════╗")
    print("║         HOSPITAL LOGIN        ║")
    print("╚══════════════════════════════╝")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    for uid, user in db["users"].items():
        if user["username"] == username and user["password"] == password:
            print(f"\n✅ Welcome, {user['name']}! (Role: {user['role'].upper()})")
            return user
    print("❌ Invalid credentials.")
    return None

def register_patient():
    db = load_db()
    print("\n╔══════════════════════════════╗")
    print("║      PATIENT REGISTRATION     ║")
    print("╚══════════════════════════════╝")
    name = input("Full Name: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    age = input("Age: ").strip()
    phone = input("Phone: ").strip()

    for u in db["users"].values():
        if u["username"] == username:
            print("❌ Username already exists.")
            return

    uid = "P" + str(uuid.uuid4())[:6].upper()
    db["users"][uid] = {
        "id": uid,
        "username": username,
        "password": password,
        "role": "patient",
        "name": name,
        "age": age,
        "phone": phone
    }
    save_db(db)
    print(f"✅ Patient registered! Your Patient ID: {uid}")
