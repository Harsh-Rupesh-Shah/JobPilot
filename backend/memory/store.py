"""
store.py
Initializes the MongoDBStore for LangGraph long-term memory (cross-thread state).
"""

from typing import Optional
from langchain_core.documents import Document
# If using a specific implementation, you'd import MongoDBStore here. 
# LangGraph currently has InMemoryStore and BaseStore. 
# For long-term memory across threads, we will build a simple async class 
# since a native `MongoDBStore` in the style of BaseStore might not be in the base lib yet.
# Note: In standard LangGraph, memory is primarily Checkpointer.

# We will implement a minimal BaseStore wrapper for MongoDB if required,
# or just rely on direct MongoDB insertions for "store".

from langgraph.store.memory import InMemoryStore

def get_store():
    """
    Returns the long-term memory store. 
    (Currently defaulting to InMemoryStore as placeholder, but in production 
    we will wire this to MongoDB for cross-thread profiles if LangGraph supports it directly, 
    otherwise we use direct DB calls).
    """
    # For now, return InMemoryStore. The real user profile memory will be managed via ApplicationState 
    # reading from direct MongoDB calls in the nodes if cross-thread memory is needed.
    return InMemoryStore()
