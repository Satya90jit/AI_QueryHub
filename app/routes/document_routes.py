# app/routes/document_routes.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.services import file_service, document_service, nlp_service
from app.dependencies import get_db
from app.schemas.document import DocumentOut
from app.models.document import Document
import logging
import json
from app.services.nlp_service import NLPService

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Upload and create a document with metadata extraction and S3 storage
@router.post("/upload/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Validate file type and size
        await file_service.validate_file(file)
        await file_service.validate_file_size(file)

        # Extract metadata and upload file to S3
        file_metadata = document_service.extract_metadata(file)
        file_url = await file_service.upload_to_s3(file)

        # Save document details in the database
        document = document_service.save_document(
            db, file.filename, file_url, file.content_type, file_metadata
        )

          # Parse `file_metadata` to ensure it's a list for the response
        if isinstance(document.file_metadata, str):
            document.file_metadata = json.loads(document.file_metadata)

        return DocumentOut(
            id=document.id,
            filename=document.filename,
            url=document.url,
            file_type=document.file_type,
            file_metadata=document.file_metadata  # Ensure this is a list
        )
    except Exception as e:
        logging.error(f"Error occurred during file upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while uploading the file.")

# Retrieve a document by ID
@router.get("/document/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Parse file_metadata if it's a string
    if isinstance(document.file_metadata, str):
        try:
            document.file_metadata = json.loads(document.file_metadata)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing file metadata")
    
    return DocumentOut.from_orm(document)

# Query the NLP model
@router.get("/query/")
async def query_document_nlp(query: str = Query(...), db: Session = Depends(get_db)):
    try:
        logger.info(f"Received query: {query}")
        response = NLPService.query_document(query, db)
        logger.info(f"Query response: {response}")
        return {"query": query, "response": response}
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Query failed")