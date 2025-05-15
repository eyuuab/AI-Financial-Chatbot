"""
Database models and operations for the AI Financial Chatbot.
Provides functions to interact with the Supabase database.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from app.db.database import supabase_client

# Configure logging
logger = logging.getLogger(__name__)

# Table names
USERS_TABLE = "users"
CHAT_HISTORY_TABLE = "chat_history"

class UserRepository:
    """Repository for user operations."""
    
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user in the database.
        
        Args:
            user_data: User data to insert
            
        Returns:
            Dict: Created user data
        """
        try:
            response = supabase_client.table(USERS_TABLE).insert(user_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        try:
            response = supabase_client.table(USERS_TABLE).select("*").eq("username", username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        try:
            response = supabase_client.table(USERS_TABLE).select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    @staticmethod
    async def update_user(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user in the database.
        
        Args:
            user_id: ID of the user to update
            user_data: User data to update
            
        Returns:
            Dict: Updated user data
        """
        try:
            response = supabase_client.table(USERS_TABLE).update(user_data).eq("id", user_id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

class ChatHistoryRepository:
    """Repository for chat history operations."""
    
    @staticmethod
    async def add_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a message to the chat history.
        
        Args:
            message_data: Message data to insert
            
        Returns:
            Dict: Created message data
        """
        try:
            # Ensure timestamp is set
            if "timestamp" not in message_data:
                message_data["timestamp"] = datetime.now(timezone.utc).isoformat()
                
            response = supabase_client.table(CHAT_HISTORY_TABLE).insert(message_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error adding message to chat history: {str(e)}")
            raise
    
    @staticmethod
    async def get_user_chat_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history for a user.
        
        Args:
            user_id: User ID to get history for
            limit: Maximum number of messages to return
            
        Returns:
            List[Dict]: Chat history messages
        """
        try:
            response = supabase_client.table(CHAT_HISTORY_TABLE) \
                .select("*") \
                .eq("user_id", user_id) \
                .order("timestamp", desc=True) \
                .limit(limit) \
                .execute()
            
            # Return messages in chronological order
            return list(reversed(response.data)) if response.data else []
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            raise
