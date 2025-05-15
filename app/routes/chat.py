"""
Chat API routes for the AI Financial Chatbot.
Handles user message processing and response generation.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from app.nlp.intent import IntentClassifier
from app.services.financial_api import FinancialService
from app.models.user import User, get_current_user
from app.db.models import ChatHistoryRepository

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
try:
    intent_classifier = IntentClassifier()
except Exception as e:
    # Create a simple mock classifier if the real one fails
    from app.nlp.intent import IntentClassifier

    class MockIntentClassifier:
        def classify(self, text: str) -> Tuple[str, float]:
            """Simple mock classifier that returns greeting or unknown."""
            text_lower = text.lower()
            if any(greeting in text_lower for greeting in ["hello", "hi", "hey", "greetings"]):
                return "greeting", 0.9
            elif any(word in text_lower for word in ["bye", "goodbye", "see you"]):
                return "goodbye", 0.9
            elif "stock" in text_lower and "price" in text_lower:
                return "stock_price", 0.8
            elif "market" in text_lower:
                return "market_info", 0.8
            elif "advice" in text_lower or "invest" in text_lower:
                return "financial_advice", 0.8
            else:
                return "unknown", 0.5

    logger.warning(f"Failed to initialize IntentClassifier: {str(e)}. Using mock classifier.")
    intent_classifier = MockIntentClassifier()

financial_service = FinancialService()

class Message(BaseModel):
    """Message model for chat requests."""
    text: str
    context: Optional[Dict] = {}

class ChatResponse(BaseModel):
    """Response model for chat API."""
    response: str
    intent: str
    confidence: float
    data: Optional[Dict] = None

@router.post("/message", response_model=ChatResponse)
async def process_message(
    message: Message,
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """
    Process a user message and generate a response.

    Args:
        message: The user's message
        current_user: The authenticated user

    Returns:
        ChatResponse: The chatbot's response
    """
    try:
        # Classify the intent of the message
        intent, confidence = intent_classifier.classify(message.text)

        # Get financial data if needed
        data = None
        if intent in ["stock_price", "market_info", "financial_advice"]:
            data = await financial_service.get_data(intent, message.text, message.context)

        # Generate response based on intent and data
        response = financial_service.generate_response(intent, message.text, data)

        # Save user message to chat history
        await ChatHistoryRepository.add_message({
            "user_id": current_user.id,
            "role": "user",
            "message": message.text,
            "intent": intent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Save bot response to chat history
        await ChatHistoryRepository.add_message({
            "user_id": current_user.id,
            "role": "bot",
            "message": response,
            "intent": intent,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return ChatResponse(
            response=response,
            intent=intent,
            confidence=confidence,
            data=data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/history", response_model=List[Dict])
async def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """
    Get the chat history for the current user.

    Args:
        limit: Maximum number of messages to return
        current_user: The authenticated user

    Returns:
        List[Dict]: The chat history
    """
    try:
        # Fetch chat history from database
        history = await ChatHistoryRepository.get_user_chat_history(current_user.id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")
