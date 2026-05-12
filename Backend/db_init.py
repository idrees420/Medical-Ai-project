from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Doctor
import datetime

def seed_doctors():
    db: Session = SessionLocal()
    
    # Check if doctors already exist to avoid duplicates
    if db.query(Doctor).first():
        print("Doctors already exist in the database. Skipping seed.")
        db.close()
        return

    doctors = [
        Doctor(
            full_name="Dr. John Smith",
            email="john.smith@hospital.com",
            phone="123-456-7890",
            specialization="Cardiology"
        ),
        Doctor(
            full_name="Dr. Sarah Johnson",
            email="sarah.johnson@hospital.com",
            phone="123-456-7891",
            specialization="Dermatology"
        ),
        Doctor(
            full_name="Dr. Michael Brown",
            email="michael.brown@hospital.com",
            phone="123-456-7892",
            specialization="General Physician"
        ),
        Doctor(
            full_name="Dr. Emily Davis",
            email="emily.davis@hospital.com",
            phone="123-456-7893",
            specialization="Neurology"
        ),
        Doctor(
            full_name="Dr. Robert Wilson",
            email="robert.wilson@hospital.com",
            phone="123-456-7894",
            specialization="Pediatrics"
        ),
        Doctor(
            full_name="Dr. Alan Parker",
            email="alan.parker@hospital.com",
            phone="123-456-7895",
            specialization="Gastroenterologist"
        )
    ]

    try:
        db.add_all(doctors)
        db.commit()
        print(f"Successfully seeded {len(doctors)} doctors.")
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables are created first (if not using migrations for simple testing)
    # Base.metadata.create_all(bind=engine)
    seed_doctors()
