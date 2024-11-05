#  File upload, S3 storage, and validation
# app/services/file_service.py
import boto3
from fastapi import UploadFile, HTTPException, status
from app.config.settings import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)

async def upload_to_s3(file: UploadFile) -> str:
    try:
        s3_client.upload_fileobj(file.file, settings.AWS_S3_BUCKET_NAME, file.filename)
        return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{file.filename}"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def validate_file(file: UploadFile):
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

async def validate_file_size(file: UploadFile):
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")
    file.file.seek(0)
