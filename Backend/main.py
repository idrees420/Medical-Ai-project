import bcrypt
# Passlib fix for modern bcrypt versions
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("bcrypt_about", (object,), {"__version__": bcrypt.__version__})

import hashlib
import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from passlib.context import CryptContext

from database import get_db
import models
from prediction.mistral_predict import predict_disease
from agents import run_agents
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Backend is reachable"}

# -----------------------------
# Models
# -----------------------------
class SignupRequest(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SymptomRequest(BaseModel):
    symptoms: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[str]] = []
    email: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    history: List[str]

class AppointmentRequest(BaseModel):
    email: str  # Use email to identify patient
    doctor_id: int
    predicted_disease: Optional[str] = None
    appointment_date: str  # YYYY-MM-DD
    appointment_time: str  # HH:MM

# -----------------------------
# Helper Functions
# -----------------------------
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# Authentication Endpoints
# -----------------------------
@app.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.Patient).filter(models.Patient.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new patient
    new_patient = models.Patient(
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        password_hash=hash_password(request.password)
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return {
        "message": "User created successfully", 
        "user_id": new_patient.id,
        "full_name": new_patient.full_name,
        "email": new_patient.email
    }

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.Patient).filter(
        models.Patient.email == request.email,
        models.Patient.password_hash == hash_password(request.password)
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"message": "Login successful", "full_name": user.full_name, "email": user.email}

# -----------------------------
# /predict endpoint
# -----------------------------
@app.post("/predict")
def predict(request: SymptomRequest):
    print(f"Predict endpoint triggered. Symptoms: {request.symptoms}")
    result = predict_disease(request.symptoms)
    return {"result": result}

# -----------------------------
# /chat endpoint
# -----------------------------
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    chat_history = []
    for msg in request.history:
        if msg.startswith("User:"):
            chat_history.append(HumanMessage(content=msg.replace("User:", "").strip()))
        else:
            chat_history.append(AIMessage(content=msg.replace("AI:", "").strip()))

    result = run_agents(request.message, chat_history, user_email=request.email)
    
    formatted_history = []
    for msg in result["chat_history"]:
        if msg.__class__.__name__ == "HumanMessage":
            formatted_history.append(f"User: {msg.content}")
        else:
            formatted_history.append(f"AI: {msg.content}")

    return {
        "response": result["response"],
        "history": formatted_history
    }

# -----------------------------
# Doctor & Appointment Endpoints
# -----------------------------
@app.get("/doctors")
def get_doctors(specialization: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Doctor)
    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
    return query.all()

@app.post("/book-appointment")
def book_appointment(request: AppointmentRequest, db: Session = Depends(get_db)):
    # Find patient by email
    patient = db.query(models.Patient).filter(models.Patient.email == request.email).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check for conflict
    apt_date = datetime.date.fromisoformat(request.appointment_date)
    apt_time = datetime.time.fromisoformat(request.appointment_time)
    
    conflict = db.query(models.BookedSlot).filter(
        models.BookedSlot.doctor_id == request.doctor_id,
        models.BookedSlot.appointment_date == apt_date,
        models.BookedSlot.appointment_time == apt_time
    ).first()
    
    if conflict:
        raise HTTPException(status_code=400, detail="This slot is already booked for this doctor.")

    # Create the appointment record
    new_app = models.Appointment(
        patient_id=patient.id,
        doctor_id=request.doctor_id,
        predicted_disease=request.predicted_disease,
        appointment_date=apt_date,
        appointment_time=apt_time,
        status=models.AppointmentStatus.pending
    )
    
    # Also add to booked_slots
    new_slot = models.BookedSlot(
        doctor_id=request.doctor_id,
        appointment_date=apt_date,
        appointment_time=apt_time
    )
    
    db.add(new_app)
    db.add(new_slot)
    db.commit()
    db.refresh(new_app)
    
    return {
        "message": "Appointment booked successfully", 
        "appointment_id": new_app.id,
        "doctor_id": request.doctor_id,
        "date": request.appointment_date
    }

@app.get("/my-appointments")
def get_my_appointments(email: str, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.email == email).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == patient.id).all()
    
    result = []
    for app in appointments:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == app.doctor_id).first()
        result.append({
            "id": app.id,
            "doctor_name": doctor.full_name if doctor else "Unknown",
            "specialization": doctor.specialization if doctor else "Unknown",
            "date": app.appointment_date.isoformat(),
            "time": app.appointment_time.strftime("%H:%M"),
            "status": app.status.value,
            "predicted_disease": app.predicted_disease
        })
    
    return result

# -----------------------------
# Doctor Specific Endpoints
# -----------------------------

class DoctorLoginRequest(BaseModel):
    email: str
    password: str

class DoctorSignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    specialization: str
    password: str
    availability: str = "Mon-Fri"
    working_hours: str = "09:00 - 17:00"

@app.post("/doctor/signup")
def doctor_signup(request: DoctorSignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.Doctor).filter(models.Doctor.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = pwd_context.hash(request.password)
    new_doctor = models.Doctor(
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        specialization=request.specialization,
        password_hash=hashed_pw,
        availability=request.availability,
        working_hours=request.working_hours
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return {"message": "Doctor registered successfully", "id": new_doctor.id}

@app.post("/doctor/login")
def doctor_login(request: DoctorLoginRequest, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.email == request.email).first()
    if not doctor or not pwd_context.verify(request.password, doctor.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {
        "id": doctor.id, 
        "full_name": doctor.full_name, 
        "specialization": doctor.specialization,
        "availability": doctor.availability,
        "working_hours": doctor.working_hours
    }

class UpdateAvailabilityRequest(BaseModel):
    availability: str
    working_hours: str

@app.put("/doctor/{doctor_id}/availability")
def update_availability(doctor_id: int, request: UpdateAvailabilityRequest, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor.availability = request.availability
    doctor.working_hours = request.working_hours
    db.commit()
    return {"message": "Availability updated"}

@app.get("/doctor/appointments/{doctor_id}")
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).all()
    
    result = []
    for app in appointments:
        patient = db.query(models.Patient).filter(models.Patient.id == app.patient_id).first()
        result.append({
            "id": app.id,
            "patient_name": patient.full_name if patient else "Unknown",
            "date": app.appointment_date.isoformat(),
            "time": app.appointment_time.strftime("%H:%M"),
            "status": app.status.value,
            "predicted_disease": app.predicted_disease
        })
    return result

class StatusRequest(BaseModel):
    status: str  # confirmed or cancelled

@app.put("/appointment/{appointment_id}/status")
def update_appointment_status(appointment_id: int, request: StatusRequest, db: Session = Depends(get_db)):
    app = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    try:
        app.status = models.AppointmentStatus(request.status)
        db.commit()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    return {"message": f"Appointment status updated to {request.status}"}