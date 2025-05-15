"""
Main application entry point for the AI Financial Chatbot.
Sets up FastAPI and includes all routes.
"""

import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.routes import chat
from app.models.user import Token, authenticate_user, create_access_token, create_user, UserCreate
from datetime import timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Financial Chatbot",
    description="An intelligent chatbot for financial queries and assistance",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "message": "Welcome to the AI Financial Chatbot API",
        "docs": "/docs",
        "version": "0.1.0",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "status": "warning",
                "message": "Supabase not configured. Using in-memory storage.",
                "supabase_url": "not configured"
            }

        # Try to import the client (will fail if connection fails)
        from app.db.database import supabase_client

        return {
            "status": "healthy",
            "database": "connected",
            "supabase_url": settings.SUPABASE_URL[:20] + "..." if settings.SUPABASE_URL else "not configured"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "warning",
            "message": "Database connection failed. Using in-memory storage.",
            "error": str(e)
        }

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register_user(user_data: UserCreate):
    """
    Register a new user.
    """
    try:
        user = await create_user(user_data)
        return {"message": "User created successfully", "username": user.username}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
