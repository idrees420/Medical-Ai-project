import models
from database import engine
from sqlalchemy import text
with engine.connect() as conn:
    res = conn.execute(text("SELECT * FROM doctors LIMIT 1"))
    print(f"Columns: {res.keys()}")
