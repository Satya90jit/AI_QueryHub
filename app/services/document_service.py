from sqlalchemy.orm import Session
from app.models.document import Document
from io import BytesIO
import json
from unstructured.partition.auto import partition
from app.services.nlp_service import DocumentIndexer

# Initialize indexer instance
indexer = DocumentIndexer()

def save_document(db: Session, filename: str, url: str, file_type: str, file_metadata: list) -> Document:
    """
    Saves document metadata to the database and indexes its text content.
    
    Args:
        db (Session): Database session.
        filename (str): Name of the file.
        url (str): URL to the file location.
        file_type (str): File type (e.g., PDF, DOCX).
        file_metadata (list): List of extracted text segments.

    Returns:
        Document: Document model instance with metadata and content.
    """
    # Save document metadata in the database
    db_document = Document(
        filename=filename,
        url=url,
        file_type=file_type,
        file_metadata=json.dumps(file_metadata)
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Extract and combine all text parts for indexing
    text_content = " ".join([metadata["text"] for metadata in file_metadata if metadata["text"]])

    # Index the document content using the DocumentIndexer
    indexer.index_document([text_content])  # Using a list to index a single document

    return db_document

def extract_metadata(file) -> list:
    """
    Extracts metadata from a file and prepares it for indexing.
    
    Args:
        file (File): The file from which text needs to be extracted.

    Returns:
        list: List of text segments extracted from the file.
    """
    file_data = BytesIO(file.file.read())
    elements = partition(file=file_data)
    file.file.seek(0)  # Reset pointer after reading for future use

    # Prepare JSON-serializable metadata
    file_metadata = [{"type": type(element).__name__, "text": getattr(element, "text", None)} for element in elements]
    return file_metadata
