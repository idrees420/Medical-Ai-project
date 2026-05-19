import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("No DATABASE_URL found")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE doctors ADD COLUMN IF NOT EXISTS fee VARCHAR DEFAULT '1000'"))
        conn.commit()
    print("Successfully added 'fee' column to doctors table.")
except Exception as e:
    print(f"Error updating schema: {e}")
