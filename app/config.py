"""
Configuration management for the AI Financial Chatbot.
Loads environment variables and provides settings for the application.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""

    # API settings
    API_PREFIX: str = "/api/v1"

    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Security settings
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", "supersecretkey"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # NLP model settings
    NLP_MODEL_PATH: str = Field(default=os.getenv("NLP_MODEL_PATH", "models/intent_classifier"))

    # External API settings
    FINANCIAL_API_KEY: str = Field(default=os.getenv("FINANCIAL_API_KEY", ""))
    FINANCIAL_API_URL: str = Field(default=os.getenv("FINANCIAL_API_URL", "https://api.example.com"))

    # Database settings
    SUPABASE_URL: str = Field(default=os.getenv("SUPABASE_URL", ""))
    SUPABASE_KEY: str = Field(default=os.getenv("SUPABASE_KEY", ""))

    # Database table names
    DB_USERS_TABLE: str = "users"
    DB_CHAT_HISTORY_TABLE: str = "chat_history"

    # Database credentials (optional)
    DB_PASSWORD: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields not defined in the model
    }

# Initialize settings
settings = Settings()
