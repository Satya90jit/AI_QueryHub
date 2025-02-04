# Main application entry point
# app/main.py
from fastapi import FastAPI
from app.db.init_db import create_database
from app.routes import auth_routes, user_routes, secure_routes,document_routes


app = FastAPI()

# Initialize the database (optional to run every time)
create_database()
    
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with Redis and Database!"}

# Include routers
app.include_router(auth_routes)
app.include_router(user_routes)
app.include_router(secure_routes)
app.include_router(document_routes)