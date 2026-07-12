import logging
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from src.server.core.config import settings

logger = logging.getLogger(__name__)

# Initialize the MongoDB client with explicit connection pool configuration
client = AsyncIOMotorClient(
    settings.MONGODB_URL,
    maxPoolSize=100,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000
)

# Reference the configured database name
db = client[settings.DATABASE_NAME]


async def get_db() -> AsyncGenerator:
    """
    Asynchronous dependency function yielding the active database instance.
    This manages session context and database lifecycle securely.
    """
    try:
        yield db
    except Exception as e:
        logger.error(f"Error yielding database connection: {e}")
        raise
    finally:
        # Motor AsyncIOMotorClient has internal connection pool management;
        # no manual connection teardown is required for simple per-request cycles.
        pass
