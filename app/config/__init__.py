from .redis import redis_client
from dotenv import load_dotenv
from .settings import settings

# Load environment variables from .env file
load_dotenv()

__all__ = [
    "redis_client",
    "settings",  # Include the settings instance in the exports
]
