# app/routes/user_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import UserOut
from app.services import auth_service
from app.dependencies import get_db

router = APIRouter()

@router.get("/users/me", response_model=UserOut)
def read_user(db: Session = Depends(get_db), token: str = Depends(auth_service.oauth2_scheme)):
    username = auth_service.verify_access_token(token)
    user = auth_service.get_user(db, username=username)
    return user
