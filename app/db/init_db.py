# Database initialization (e.g., creating tables)
# init_db.py
from .base import Base
from .connection import engine

def create_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
