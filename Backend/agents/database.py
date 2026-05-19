from typing import List, Dict, Optional
import os
import sys

# Ensure we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models

def search_doctors(specialty: str) -> List[Dict]:
    """Search for doctors in the real PostgreSQL database by specialty."""
    db = SessionLocal()
    try:
        # We use a case-insensitive search for the specialization
        doctors = db.query(models.Doctor).filter(
            models.Doctor.specialization.ilike(f"%{specialty}%")
        ).all()
        
        results = []
        for d in doctors:
            results.append({
                "id": d.id,
                "name": f"Dr. {d.full_name}",
                "specialty": d.specialization,
                "availability": f"{d.availability} ({d.working_hours})",
                "fee": getattr(d, 'fee', '1000')
            })
        return results
    finally:
        db.close()

def get_doctor_by_name(name: str) -> Optional[Dict]:
    """Get a doctor from PostgreSQL by name."""
    db = SessionLocal()
    try:
        # Search for name (Dr. prefix ignored)
        search_name = name.replace("Dr. ", "").strip()
        d = db.query(models.Doctor).filter(
            models.Doctor.full_name.ilike(f"%{search_name}%")
        ).first()
        
        if d:
            return {
                "id": d.id,
                "name": f"Dr. {d.full_name}",
                "specialty": d.specialization,
                "availability": f"{d.availability} ({d.working_hours})",
                "fee": getattr(d, 'fee', '1000')
            }
        return None
    finally:
        db.close()
