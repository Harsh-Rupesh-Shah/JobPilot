"""
checkpointer.py
Initializes the MongoDBSaver for LangGraph checkpointing (per-thread state).
Uses the synchronous PyMongo client as required by langgraph-checkpoint-mongodb.
"""

from langgraph.checkpoint.mongodb import MongoDBSaver
from backend.db.database import sync_client
from backend.config import settings

def get_checkpointer():
    """
    Returns a configured MongoDBSaver instance using the sync MongoDB client.
    """
    # LangGraph creates a "checkpoints" collection in this database automatically.
    return MongoDBSaver(sync_client, db_name=settings.DATABASE_NAME)
