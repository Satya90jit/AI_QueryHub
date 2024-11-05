# app/services/auth_service.py
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.config.settings import settings
from app.config.redis import redis_client  # Import redis_client directly
from fastapi.security import OAuth2PasswordBearer


#Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Adjust tokenUrl as per your endpoint

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    redis_client.setex(encoded_jwt, int(expires_delta.total_seconds()), data["sub"])
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None or not redis_client.exists(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
