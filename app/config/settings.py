import os
from passlib.context import CryptContext
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")  # Add this line

    # Redis Configuration
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION_NAME: str = Field(..., env="AWS_REGION_NAME")
    AWS_S3_BUCKET_NAME: str = Field(..., env="AWS_S3_BUCKET_NAME")

    # OpenAI API Key
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # File settings
    ALLOWED_FILE_TYPES: set = Field(default={"application/pdf", "application/vnd.ms-powerpoint", "text/csv"})
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024)  # 10 MB


    class Config:
        env_file = ".env"  # Specify the .env file to load environment variables

# Create an instance of Settings
settings = Settings()

# Password hashing context
pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
