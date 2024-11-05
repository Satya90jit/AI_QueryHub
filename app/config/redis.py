# app/config/redis.py

from .settings import Settings  # Import the Settings class
import redis
import logging

# Create an instance of Settings
settings = Settings()

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis client setup
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Test connection
try:
    redis_client.ping()
    logger.info("Connected to Redis")
except redis.ConnectionError as e:
    logger.error("Could not connect to Redis: %s", e)
