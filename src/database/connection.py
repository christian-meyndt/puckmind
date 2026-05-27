"""
Shared MongoDB Connection for PuckMind
Centralizes database connection to avoid duplication.
"""

import ssl
from pymongo import MongoClient
from pymongo.database import Database
from src.config import MONGODB_URI, DATABASE_NAME

# Global connection pool
_client: MongoClient = None
_db: Database = None


def get_client() -> MongoClient:
    """
    Get MongoDB client (singleton pattern).
    Returns the same client instance across all calls.
    """
    global _client
    if _client is None:
        _client = MongoClient(
            MONGODB_URI,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE
        )
    return _client


def get_db() -> Database:
    """
    Get MongoDB database (singleton pattern).
    Returns the same database instance across all calls.
    """
    global _db
    if _db is None:
        client = get_client()
        _db = client[DATABASE_NAME]
    return _db


def close_connection():
    """
    Close MongoDB connection.
    Useful for cleanup in tests or when shutting down.
    """
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
