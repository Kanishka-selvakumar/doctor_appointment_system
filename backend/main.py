from database import load_db, init_db
from auth import login, register_patient
from admin_module import admin_menu
from doctor_module import doctor_menu
from patient_module import patient_menu

def main():
    print("╔══════════════════════════════════════════╗")
    print("║   🏥  HOSPITAL APPOINTMENT SYSTEM  🏥    ║")
    print("╠══════════════════════════════════════════╣")
    print("║         Role-Based Medical Platform       ║")
    print("╚══════════════════════════════════════════╝")

    # Ensure DB exists
    load_db()

    while True:
        print("\n╔══════════════════════════╗")
        print("║         MAIN MENU         ║")
        print("╠══════════════════════════╣")
        print("║  1. Login                 ║")
        print("║  2. Register as Patient   ║")
        print("║  3. Exit                  ║")
        print("╚══════════════════════════╝")
        choice = input("Select option: ").strip()

        if choice == "1":
            user = login()
            if user:
                role = user["role"]
                if role == "admin":
                    admin_menu(user)
                elif role == "doctor":
                    doctor_menu(user)
                elif role == "patient":
                    patient_menu(user)

        elif choice == "2":
            register_patient()

        elif choice == "3":
            print("\n👋 Thank you for using Hospital Appointment System. Goodbye!")
            break
        else:
            print("❌ Invalid option. Try again.")

if __name__ == "__main__":
    main()
