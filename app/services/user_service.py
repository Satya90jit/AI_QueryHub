# User-specific CRUD and utility functions
# app/services/user_service.py
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from app.config.settings import pwd_context

def get_user(db: Session, username: str) -> User:
    """Retrieve a user by username from the database."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with a hashed password."""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
