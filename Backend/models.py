from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class AppointmentStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # Added for doctor login
    specialization = Column(String, nullable=False)
    availability = Column(String, default="Mon-Fri")
    working_hours = Column(String, default="09:00 - 17:00")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")
    availability_slots = relationship("DoctorAvailability", back_populates="doctor")
    booked_slots = relationship("BookedSlot", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    predicted_disease = Column(String, nullable=True)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    day_of_week = Column(String, nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationships
    doctor = relationship("Doctor", back_populates="availability_slots")

class BookedSlot(Base):
    __tablename__ = "booked_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)

    # Relationships
    doctor = relationship("Doctor", back_populates="booked_slots")
