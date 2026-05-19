from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Doctor
import datetime

def seed_doctors():
    db: Session = SessionLocal()
    
    # Check if we already have the full list of doctors
    if db.query(Doctor).count() >= 14:
        print("All doctors already exist in the database. Skipping seed.")
        db.close()
        return

    doctors = [
        Doctor(full_name="Dr. John Smith", email="john.smith@hospital.com", phone="123-456-7890", specialization="Cardiology"),
        Doctor(full_name="Dr. Sarah Johnson", email="sarah.johnson@hospital.com", phone="123-456-7891", specialization="Dermatology"),
        Doctor(full_name="Dr. Michael Brown", email="michael.brown@hospital.com", phone="123-456-7892", specialization="General Physician"),
        Doctor(full_name="Dr. Emily Davis", email="emily.davis@hospital.com", phone="123-456-7893", specialization="Neurology"),
        Doctor(full_name="Dr. Robert Wilson", email="robert.wilson@hospital.com", phone="123-456-7894", specialization="Pediatrics"),
        Doctor(full_name="Dr. Alan Parker", email="alan.parker@hospital.com", phone="123-456-7895", specialization="Gastroenterologist"),
        Doctor(full_name="Dr. Susan Lee", email="susan.lee@hospital.com", phone="123-456-7896", specialization="Psychiatrist"),
        Doctor(full_name="Dr. David Miller", email="david.miller@hospital.com", phone="123-456-7897", specialization="Orthopedist"),
        Doctor(full_name="Dr. Karen White", email="karen.white@hospital.com", phone="123-456-7898", specialization="Pulmonologist"),
        Doctor(full_name="Dr. Richard Harris", email="richard.harris@hospital.com", phone="123-456-7899", specialization="Ophthalmologist"),
        Doctor(full_name="Dr. Nancy Clark", email="nancy.clark@hospital.com", phone="123-456-7800", specialization="ENT Specialist"),
        Doctor(full_name="Dr. Thomas Lewis", email="thomas.lewis@hospital.com", phone="123-456-7801", specialization="Endocrinologist"),
        Doctor(full_name="Dr. Laura Walker", email="laura.walker@hospital.com", phone="123-456-7802", specialization="Urologist"),
        Doctor(full_name="Dr. Kevin Hall", email="kevin.hall@hospital.com", phone="123-456-7803", specialization="Oncologist")
    ]

    try:
        added_count = 0
        for doc in doctors:
            if not db.query(Doctor).filter(Doctor.email == doc.email).first():
                db.add(doc)
                added_count += 1
        db.commit()
        print(f"Successfully seeded {added_count} new doctors.")
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables are created first (if not using migrations for simple testing)
    # Base.metadata.create_all(bind=engine)
    seed_doctors()
