#!/usr/bin/env python3
"""
Database setup script for the AI Financial Chatbot.
Creates the necessary tables in Supabase.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime, timezone
from passlib.context import CryptContext

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.db.database import supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_tables():
    """Create the necessary tables in Supabase."""
    try:
        # Create users table
        logger.info("Creating users table...")
        
        # Using raw SQL with Supabase's PostgreSQL
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_premium BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        # Create chat_history table
        logger.info("Creating chat_history table...")
        chat_history_table_sql = """
        CREATE TABLE IF NOT EXISTS chat_history (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            intent TEXT,
            data JSONB,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS chat_history_user_id_idx ON chat_history(user_id);
        CREATE INDEX IF NOT EXISTS chat_history_timestamp_idx ON chat_history(timestamp);
        """
        
        # Execute SQL
        await supabase_client.postgrest.schema("public").execute(users_table_sql)
        await supabase_client.postgrest.schema("public").execute(chat_history_table_sql)
        
        logger.info("Tables created successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

async def create_test_user():
    """Create a test user in the database."""
    try:
        # Check if test user already exists
        response = supabase_client.table("users").select("*").eq("username", "testuser").execute()
        
        if response.data:
            logger.info("Test user already exists")
            return True
        
        # Create test user
        logger.info("Creating test user...")
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
        
        response = supabase_client.table("users").insert(test_user).execute()
        
        if response.data:
            logger.info("Test user created successfully")
            return True
        else:
            logger.error("Failed to create test user")
            return False
    
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        return False

async def main():
    """Main function to set up the database."""
    logger.info("Starting database setup...")
    
    # Check Supabase connection
    try:
        # Simple query to check connection
        response = supabase_client.table("users").select("count(*)", count="exact").execute()
        logger.info("Connected to Supabase successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        return False
    
    # Create tables
    tables_created = await create_tables()
    if not tables_created:
        return False
    
    # Create test user
    user_created = await create_test_user()
    if not user_created:
        return False
    
    logger.info("Database setup completed successfully")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
