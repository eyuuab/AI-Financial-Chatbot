"""
Configuration management for the AI Financial Chatbot.
Loads environment variables and provides settings for the application.
"""

import os
from typing import List
from pydantic import BaseModel, Field

class Settings(BaseModel):
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

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

# Initialize settings
settings = Settings()
