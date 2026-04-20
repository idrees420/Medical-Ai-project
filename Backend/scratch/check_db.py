import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def check_appointments():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM appointments;"))
        rows = result.fetchall()
        print(f"Total Appointments: {len(rows)}")
        for row in rows:
            print(row)

if __name__ == "__main__":
    try:
        check_appointments()
    except Exception as e:
        print(f"Error connecting to database: {e}")
