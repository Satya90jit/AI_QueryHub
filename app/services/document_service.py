# app/services/document_service.py
from sqlalchemy.orm import Session
from app.models.document import Document
from io import BytesIO
import json
from unstructured.partition.auto import partition
from app.services.nlp_service import NLPService

def save_document(db: Session, filename: str, url: str, file_type: str, file_metadata: list) -> Document:
    db_document = Document(
        filename=filename,
        url=url,
        file_type=file_type,
        file_metadata=json.dumps(file_metadata)
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Index the document content in the NLP engine
    # Ensure to pass the actual content of the document here, 
    # assuming you want to index some content rather than metadata
    NLPService.index_document(doc_content=json.dumps(file_metadata), doc_id=db_document.id)
    return db_document

def extract_metadata(file) -> list:
    file_data = BytesIO(file.file.read())
    elements = partition(file=file_data)
    file.file.seek(0)  # Reset pointer after reading
    
    # Convert elements to JSON-serializable format
    file_metadata = [{"type": type(element).__name__, "text": getattr(element, "text", None)} for element in elements]
    return file_metadata
