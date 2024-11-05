# document.py
import json
from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    url = Column(String)
    file_type = Column(String)
    file_metadata = Column(Text)  # JSON-encoded metadata

    def get_file_metadata(self):
         # Ensure metadata is parsed as a list of dictionaries
        try:
            return json.loads(self.file_metadata) if self.file_metadata else []
        except json.JSONDecodeError:
            return []  # Return empty list if JSON is invalid
