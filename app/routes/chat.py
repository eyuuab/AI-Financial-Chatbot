"""
Chat API routes for the AI Financial Chatbot.
Handles user message processing and response generation.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from app.nlp.intent import IntentClassifier
from app.services.financial_api import FinancialService
from app.models.user import User, get_current_user

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
intent_classifier = IntentClassifier()
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
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """
    Get the chat history for the current user.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        List[Dict]: The chat history
    """
    # This would typically fetch from a database
    # For now, return a placeholder
    return [
        {"role": "user", "message": "What's the current price of Apple stock?", "timestamp": "2023-05-01T12:00:00Z"},
        {"role": "bot", "message": "The current price of Apple (AAPL) is $173.50.", "timestamp": "2023-05-01T12:00:01Z"}
    ]
