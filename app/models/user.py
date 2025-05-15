"""
User models and authentication utilities for the AI Financial Chatbot.
"""

import uuid
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.db.models import UserRepository

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation model."""
    password: str

class User(UserBase):
    """User model."""
    id: str
    is_active: bool = True
    is_premium: bool = False
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserInDB(User):
    """User model as stored in the database."""
    hashed_password: str

class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash."""
    return pwd_context.hash(password)

async def get_user(username: str) -> Optional[UserInDB]:
    """Get a user by username."""
    try:
        user_dict = await UserRepository.get_user_by_username(username)
        if user_dict:
            # Convert string timestamp to datetime
            if isinstance(user_dict.get("created_at"), str):
                user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"].replace("Z", "+00:00"))
            return UserInDB(**user_dict)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def create_user(user_data: UserCreate) -> User:
    """Create a new user."""
    try:
        # Check if user already exists
        existing_user = await get_user(user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        # Create user data for database
        hashed_password = get_password_hash(user_data.password)
        user_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)

        user_dict = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_premium": False,
            "created_at": created_at.isoformat()
        }

        # Insert into database
        await UserRepository.create_user(user_dict)

        # Return user without password
        return User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=True,
            is_premium=False,
            created_at=created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user(token_data.username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
