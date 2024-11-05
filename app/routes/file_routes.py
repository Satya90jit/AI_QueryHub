from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.services import file_service, document_service
from app.dependencies import get_db
from app.schemas.document import DocumentOut  # Assuming you have a schema for response
import logging

router = APIRouter()

# Configure logging at the start of your application
logging.basicConfig(level=logging.INFO)

@router.post("/upload/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a file and save its file_metadata."""
    try:
        # Validations
        await file_service.validate_file(file)  # Validate file type
        await file_service.validate_file_size(file)  # Validate file size

        # Extract file metadata
        file_metadata = document_service.extract_metadata(file)
        logging.info(f"Extracted file metadata: {file_metadata}")  # Debugging

        # Ensure file_metadata is a list
        if not isinstance(file_metadata, list):
            file_metadata = [file_metadata]  # Wrap in a list if it's not already

        # Upload to S3
        file_url = await file_service.upload_to_s3(file)
        logging.info(f"Uploaded file to S3, URL: {file_url}")  # Debugging

        # Save document and return response
        document = document_service.save_document(db, file.filename, file_url, file.content_type, file_metadata)
        logging.info(f"Document saved: {document}")  # Debugging

        return document  # Return the saved document details as response

    except file_service.UnsupportedFileTypeError as e:
        logging.error(f"Unsupported file type: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload a PDF or CSV file.",
        )
    except file_service.FileSizeExceededError as e:
        logging.error(f"File size exceeded: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the allowed limit.",
        )
    except Exception as e:
        logging.error(f"Error occurred during file upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file.",
        )

