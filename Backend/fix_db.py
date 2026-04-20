import sys
import os
from sqlalchemy import text
from database import engine

def migrate():
    print("Checking database schema for availability columns...")
    try:
        with engine.connect() as conn:
            # Check for availability
            res1 = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='doctors' AND column_name='availability'"))
            if not res1.fetchone():
                print("Adding 'availability' column...")
                conn.execute(text("ALTER TABLE doctors ADD COLUMN availability VARCHAR DEFAULT 'Mon-Fri';"))
            
            # Check for working_hours
            res2 = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='doctors' AND column_name='working_hours'"))
            if not res2.fetchone():
                print("Adding 'working_hours' column...")
                conn.execute(text("ALTER TABLE doctors ADD COLUMN working_hours VARCHAR DEFAULT '09:00 - 17:00';"))
            
            conn.commit()
            print("Successfully updated database with availability fields!")
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    migrate()
