"""
collections.py
Defines the main MongoDB collections and index creation routines.
"""

from pymongo import IndexModel, ASCENDING
from backend.db.database import db

# Collections
users_collection = db["users"]
refresh_tokens_collection = db["refresh_tokens"]
applications_collection = db["applications"]
outputs_collection = db["outputs"]

# Note: FAISS is used for vector search, so we do not need an Atlas Search index or resume_embeddings collection here.

async def setup_indexes():
    """
    Creates necessary database indexes to ensure uniqueness and fast querying.
    To be called during FastAPI app lifespan startup.
    """
    
    # 1. Users: email must be unique
    await users_collection.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("user_id", ASCENDING)], unique=True)
    ])
    
    # 2. Refresh tokens: indexed by token_hash
    await refresh_tokens_collection.create_indexes([
        IndexModel([("token_hash", ASCENDING)], unique=True),
        IndexModel([("user_id", ASCENDING)])
    ])
    
    # 3. Applications: ordered by user and creation date
    await applications_collection.create_indexes([
        IndexModel([("user_id", ASCENDING), ("created_at", ASCENDING)])
    ])
    
    # 4. Outputs: linked by application run_id
    await outputs_collection.create_indexes([
        IndexModel([("run_id", ASCENDING)])
    ])
