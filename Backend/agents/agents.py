from dotenv import load_dotenv
load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import json
import os
from .state import AgentState
from .database import search_doctors, get_doctor_by_name
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from database import SessionLocal
import models
from datetime import datetime

# Initialize LLM
# Ensure MISTRAL_API is set in environment
if "MISTRAL_API" in os.environ and "MISTRAL_API_KEY" not in os.environ:
    os.environ["MISTRAL_API_KEY"] = os.environ["MISTRAL_API"]

llm = ChatMistralAI(model="mistral-small-latest", temperature=0)

# --- Tools ---

import time

@tool
def find_doctor(specialty: str):
    """Search for a doctor by specialty."""
    time.sleep(1.5) # Fix for Mistral Free Tier rate limit
    return search_doctors(specialty)

@tool
def book_appointment(doctor_id: int, date: str, time_str: str, user_email: str, predicted_disease: str = None):
    """
    Book an appointment with a doctor.
    Args:
        doctor_id: The ID of the doctor (e.g., 1).
        date: Date in YYYY-MM-DD format (e.g., '2026-04-20').
        time_str: Time in HH:MM format (e.g., '11:00').
        user_email: The email of the patient booking the appointment.
        predicted_disease: Optional. The disease diagnosed by the AI earlier.
    """
    time.sleep(1.5) # Fix for Mistral Free Tier rate limit
    db = SessionLocal()
    try:
        # 1. Find the patient
        patient = db.query(models.Patient).filter(models.Patient.email == user_email).first()
        if not patient:
            return f"Error: Patient with email {user_email} not found. Please log in again."

        # 2. Check if doctor exists
        doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if not doctor:
            return f"Error: Doctor ID {doctor_id} not found."

        # 3. Format date and time
        try:
            apt_date = datetime.strptime(date, "%Y-%m-%d").date()
            apt_time = datetime.strptime(time_str, "%H:%M").time()
        except Exception:
            return "Error: Invalid date or time format. Please use YYYY-MM-DD and HH:MM."

        # 4. Check for conflict in booked_slots
        conflict = db.query(models.BookedSlot).filter(
            models.BookedSlot.doctor_id == doctor_id,
            models.BookedSlot.appointment_date == apt_date,
            models.BookedSlot.appointment_time == apt_time
        ).first()

        if conflict:
            return f"Error: Dr. {doctor.full_name} is already booked for {date} at {time_str}. Please choose another time or doctor."

        # 5. Create appointment
        new_app = models.Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            predicted_disease=predicted_disease,
            appointment_date=apt_date,
            appointment_time=apt_time,
            status=models.AppointmentStatus.pending
        )
        db.add(new_app)
        
        # 6. Mark as booked in booked_slots
        new_slot = models.BookedSlot(
            doctor_id=doctor_id,
            appointment_date=apt_date,
            appointment_time=apt_time
        )
        db.add(new_slot)
        
        db.commit()
        return f"Successfully booked appointment with Dr. {doctor.full_name} for {date} at {time}. The doctor has been notified about your potential condition: {predicted_disease if predicted_disease else 'General Checkup'}."
    except Exception as e:
        db.rollback()
        return f"Error occurred during booking: {str(e)}"
    finally:
        db.close()

# --- Agents ---

# 1. Supervisor Agent
supervisor_system_prompt = """You are a supervisor agent managing a medical appointment system.

You must ALWAYS return ONLY valid JSON.
Do NOT return explanations.

Available agents
- InfoAgent
- BookingAgent
- EndAgent
- USER

Rules:

1. If user asks for doctor → InfoAgent
2. If doctor already shown AND user says "yes", "ok", "book", → BookingAgent
3. If booking done → EndAgent
4. If unclear → USER

IMPORTANT:
- ONLY return JSON
- Example:
{{ "next_agent": "InfoAgent" }}
Now decide next agent.
"""

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", supervisor_system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "Given the conversation above, who should act next? Return JSON with 'next_agent' key.")
])

supervisor_chain = supervisor_prompt | llm

# 2. Info Agent
# We use create_react_agent which returns a compiled graph
# agents.py (Line 59 - AFTER fix)
info_agent = create_react_agent(
    llm, 
    tools=[find_doctor], 
    # RENAME 'state_modifier' to 'system_message'
    prompt="You are an Info Agent. Your job is to find doctors based on the user's request. Use the 'find_doctor' tool. When you find doctors, ALWAYS include their ID in your response to the user so they can be booked."
)
# 3. Booking Agent
# agents.py (Line AFTER fix)
booking_agent = create_react_agent(
    llm, 
    tools=[book_appointment],
    prompt="You are a Booking Agent. Your job is to book the appointment. You need a doctor's ID, a date (YYYY-MM-DD), a time (HH:MM), and the patient's email. Use 'book_appointment' tool. If you don't know the date, assume the user means the upcoming date for that day. Current year is 2026."
)
# 4. End Agent
end_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are the End Agent. Your job is to confirm the booking to the user in a polite and professional manner. Summarize the booking details."),
    MessagesPlaceholder(variable_name="messages"),
])
end_chain = end_prompt | llm

# --- Node Functions for Graph ---

from langchain_core.messages import AIMessage

def supervisor_node(state: AgentState):
    response = supervisor_chain.invoke(state)

    import json

    try:
        content = response.content.strip()

        # Remove markdown formatting if present
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(content)

        next_agent = parsed.get("next_agent", "USER")

    except Exception as e:
        print("Supervisor parsing error:", e)
        print("Raw response:", response.content)

        # Fallback (VERY IMPORTANT)
        next_agent = "USER"

    return {"next_agent": next_agent}

def info_node(state: AgentState):
    # create_react_agent expects a dict with 'messages'
    # It returns a dict with 'messages' (full history including new ones)
    result = info_agent.invoke(state)
    # We return the last message which is the agent's final response
    # However, create_react_agent might produce multiple messages (tool calls etc)
    # We want to append all new messages.
    # Since we passed the full history in 'state', result['messages'] has everything.
    # We need to filter for new messages.
    # But AgentState with add_messages handles appending.
    # If we return the FULL list, add_messages might duplicate if IDs are missing.
    # LangChain messages usually have IDs? Not always.
    # A safer way is to return only the messages that are NOT in the input state.
    # Or, simpler: just return the last message if we assume the agent summarizes.
    # But the agent might have done tool calls.
    # Let's return the last message for now, assuming it's the final answer.
    return {"messages": [result["messages"][-1]]}

def booking_node(state: AgentState):
    # Pass user_email to the agent via a system message or by modifying the state
    email = state.get("user_email")
    messages = state["messages"]
    if email:
        # Add a hidden message for the agent to know the user's email
        from langchain_core.messages import SystemMessage
        messages = messages + [SystemMessage(content=f"The current user's email is: {email}")]
    
    result = booking_agent.invoke({"messages": messages})
    return {"messages": [result["messages"][-1]]}

def end_node(state: AgentState):
    result = end_chain.invoke(state)
    return {"messages": [result]}
# --- Agents Definition End ---