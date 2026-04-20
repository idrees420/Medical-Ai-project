from database import SessionLocal
from models import Doctor, Patient, DoctorAvailability, BookedSlot, AppointmentStatus
import datetime

db = SessionLocal()

def update_doctor_name(old_name, new_name):
    doctor = db.query(Doctor).filter(Doctor.full_name == old_name).first()
    if doctor:
        doctor.full_name = new_name
        db.commit()
        print(f"Updated {old_name} to {new_name}")
    else:
        print("Doctor not found")

def add_patient(name, email, password):
    new_patient = Patient(full_name=name, email=email, password_hash=password)
    db.add(new_patient)
    db.commit()
    print(f"Added patient: {name}")

def add_doctor_availability(doctor_id, day, start, end):
    # Example: add_doctor_availability(1, "Monday", "09:00", "17:00")
    avail = DoctorAvailability(
        doctor_id=doctor_id, 
        day_of_week=day, 
        start_time=datetime.time.fromisoformat(start),
        end_time=datetime.time.fromisoformat(end)
    )
    db.add(avail)
    db.commit()
    print(f"Added availability for Doctor ID {doctor_id}")

# --- USAGE EXAMPLES ---
# update_doctor_name("Dr. John Smith", "Dr. Idrees")
# add_patient("Alice Smith", "alice@example.com", "hashed_pw_here")
# add_doctor_availability(1, "Monday", "09:00", "12:00")

db.close()
