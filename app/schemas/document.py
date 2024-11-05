# app/schemas/document.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any  # Import Dict and Any

class DocumentCreate(BaseModel):
    filename: str
    url: str
    file_type: str
    file_metadata: Optional[Dict[str, Any]] = None  # Allows for flexible metadata as a dictionary

class DocumentOut(BaseModel):
    id: int
    filename: str
    url: str
    file_type: str
    file_metadata: Optional[List[Dict[str, Any]]] = None  # JSON-compatible format # This can be changed to the appropriate type based on your requirements

    class Config:
        orm_mode = True  # Ensures compatibility with SQLAlchemy models
