# connection.py
import os
from sqlalchemy import create_engine, text

# Fetch the DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:abcdefgh@localhost/mydatabase")  # Fallback for testing
engine = create_engine(DATABASE_URL)


# Test the database connection
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Connected to the database")
except Exception as e:
    print(f"Could not connect to the database: {e}")
