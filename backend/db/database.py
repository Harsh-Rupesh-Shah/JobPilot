"""
database.py
Provides a shared asynchronous Motor client and database connection.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from backend.config import settings

# Async client for FastAPI routes and Motor operations
async_client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGODB_URI)
db = async_client[settings.DATABASE_NAME]

# Synchronous client (required for LangGraph checkpointer & store)
# langgraph-checkpoint-mongodb uses synchronous pymongo under the hood.
sync_client = MongoClient(settings.MONGODB_URI)
sync_db = sync_client[settings.DATABASE_NAME]
