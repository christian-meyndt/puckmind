"""
Database module for PuckMind
Provides MongoDB connection and database operations.
"""

from .connection import get_db, get_client

__all__ = ["get_db", "get_client"]
