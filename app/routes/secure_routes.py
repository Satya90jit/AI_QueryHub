# app/routes/secure_routes.py
from fastapi import APIRouter, Depends
from app.services import auth_service

router = APIRouter()

@router.get("/secure-data/")
def read_secure_data(token: str = Depends(auth_service.oauth2_scheme)):
    username = auth_service.verify_access_token(token)
    return {"username": username, "data": "This is protected data"}
