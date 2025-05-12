"""
Tests for the chat API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.routes.chat import router as chat_router
from app.models.user import User, create_access_token
from datetime import datetime, timedelta

# Test client
client = TestClient(app)

# Mock user for testing
mock_user = User(
    id="test1",
    username="testuser",
    email="test@example.com",
    full_name="Test User",
    is_active=True,
    created_at=datetime.utcnow()
)

# Create a test token
test_token = create_access_token(
    data={"sub": mock_user.username},
    expires_delta=timedelta(minutes=30)
)

@pytest.fixture
def auth_headers():
    """Fixture for authentication headers."""
    return {"Authorization": f"Bearer {test_token}"}

# Mock the get_current_user dependency
@pytest.fixture(autouse=True)
def mock_get_current_user():
    """Mock the get_current_user dependency."""
    with patch("app.routes.chat.get_current_user", return_value=mock_user):
        yield

class TestChatAPI:
    """Tests for the chat API."""
    
    def test_process_message_stock_price(self, auth_headers):
        """Test processing a stock price message."""
        # Mock the intent classifier and financial service
        with patch("app.routes.chat.intent_classifier.classify", return_value=("stock_price", 0.95)), \
             patch("app.routes.chat.financial_service.get_data") as mock_get_data, \
             patch("app.routes.chat.financial_service.generate_response") as mock_generate_response:
            
            # Set up the mocks
            mock_data = {
                "symbol": "AAPL",
                "price": 150.25,
                "change": 2.5,
                "change_percent": 1.7
            }
            mock_get_data.return_value = mock_data
            mock_generate_response.return_value = "The current price of AAPL is $150.25, which is 1.7% up today."
            
            # Make the request
            response = client.post(
                "/api/v1/chat/message",
                json={"text": "What's the price of Apple stock?"},
                headers=auth_headers
            )
            
            # Check the response
            assert response.status_code == 200
            data = response.json()
            assert data["intent"] == "stock_price"
            assert data["confidence"] == 0.95
            assert data["response"] == "The current price of AAPL is $150.25, which is 1.7% up today."
            assert data["data"] == mock_data
            
            # Verify the mocks were called correctly
            mock_get_data.assert_called_once()
            mock_generate_response.assert_called_once()
    
    def test_process_message_greeting(self, auth_headers):
        """Test processing a greeting message."""
        # Mock the intent classifier and financial service
        with patch("app.routes.chat.intent_classifier.classify", return_value=("greeting", 0.98)), \
             patch("app.routes.chat.financial_service.generate_response") as mock_generate_response:
            
            # Set up the mocks
            mock_generate_response.return_value = "Hello! I'm your financial assistant. How can I help you today?"
            
            # Make the request
            response = client.post(
                "/api/v1/chat/message",
                json={"text": "Hello"},
                headers=auth_headers
            )
            
            # Check the response
            assert response.status_code == 200
            data = response.json()
            assert data["intent"] == "greeting"
            assert data["confidence"] == 0.98
            assert data["response"] == "Hello! I'm your financial assistant. How can I help you today?"
            
            # Verify the mocks were called correctly
            mock_generate_response.assert_called_once()
    
    def test_get_chat_history(self, auth_headers):
        """Test getting chat history."""
        response = client.get("/api/v1/chat/history", headers=auth_headers)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "role" in data[0]
        assert "message" in data[0]
