"""
Database connection module for the AI Financial Chatbot.
Initializes and provides the Supabase client.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Mock database for fallback when Supabase is not configured
class MockSupabaseClient:
    """Mock Supabase client for development and testing."""

    def __init__(self):
        """Initialize the mock database."""
        from datetime import datetime, timezone
        from passlib.context import CryptContext

        # Password hashing
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Create a test user
        test_user = {
            "id": "00000000-0000-0000-0000-000000000001",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": pwd_context.hash("password123"),
            "is_active": True,
            "is_premium": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.tables = {
            "users": [test_user],
            "chat_history": []
        }
        logger.warning("Using MockSupabaseClient as Supabase is not configured")

    def table(self, table_name: str):
        """Get a table reference."""
        return MockTable(self, table_name)

    def postgrest(self):
        """Get a postgrest reference."""
        return self

    def schema(self, schema_name: str):
        """Get a schema reference."""
        return self

    def execute(self, sql: str):
        """Execute SQL (mock implementation)."""
        logger.info(f"Mock SQL execution: {sql}")
        return {"data": [], "count": 0}

class MockTable:
    """Mock table for the mock Supabase client."""

    def __init__(self, client, table_name: str):
        """Initialize the mock table."""
        self.client = client
        self.table_name = table_name
        self.filters = []
        self.order_by = None
        self.limit_val = None
        self.selected_columns = "*"

    def select(self, columns: str = "*", count: str = None):
        """Select columns from the table."""
        self.selected_columns = columns
        return self

    def eq(self, column: str, value: Any):
        """Filter by equality."""
        self.filters.append((column, "=", value))
        return self

    def order(self, column: str, desc: bool = False):
        """Order results."""
        self.order_by = (column, desc)
        return self

    def limit(self, limit_val: int):
        """Limit results."""
        self.limit_val = limit_val
        return self

    def insert(self, data: Dict[str, Any]):
        """Insert data into the table."""
        if isinstance(data, dict):
            self.client.tables[self.table_name].append(data)
        elif isinstance(data, list):
            self.client.tables[self.table_name].extend(data)
        return self

    def update(self, data: Dict[str, Any]):
        """Update data in the table."""
        return self

    def execute(self):
        """Execute the query."""
        # Apply filters
        results = self.client.tables[self.table_name]
        for column, op, value in self.filters:
            if op == "=":
                results = [r for r in results if r.get(column) == value]

        # Apply ordering
        if self.order_by:
            column, desc = self.order_by
            results = sorted(results, key=lambda x: x.get(column, ""), reverse=desc)

        # Apply limit
        if self.limit_val:
            results = results[:self.limit_val]

        return MockResponse(results)

class MockResponse:
    """Mock response from the mock Supabase client."""

    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize the mock response."""
        self.data = data

def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client.

    Returns:
        Client: Initialized Supabase client or MockSupabaseClient
    """
    try:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_KEY

        if not url or not key:
            logger.warning("Supabase URL or key not provided, using mock client")
            return MockSupabaseClient()

        client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
        return client

    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
        logger.warning("Falling back to mock client")
        return MockSupabaseClient()

# Initialize the Supabase client
supabase_client = get_supabase_client()
